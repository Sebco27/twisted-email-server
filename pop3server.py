import argparse
import os
import userservices as uServices
from twisted.mail.interfaces import IMailboxPOP3
from twisted.cred.portal import IRealm
from zope.interface import implementer
from twisted.mail import pop3
from twisted.internet import reactor
from twisted.cred import portal
from twisted.internet.protocol import Factory

@implementer(IRealm)
class MailRealm:
    def __init__(self, storage):
        self.storage = storage

    def requestAvatar(self, avatarId, mind, *interfaces):
        user = avatarId
        path = os.path.join(self.storage, user)

        mailbox = Mailbox(path)

        return pop3.IMailbox, mailbox, lambda: None

@implementer(IMailboxPOP3)
class Mailbox:
    def __init__(self, userPath):
        self.userPath = userPath
        self.messages = self._load()
        self.deleted = set()

    def _load(self):
        return sorted([
            os.path.join(self.userPath, message)
            for message in os.listdir(self.userPath)
        ])

    def listMessages(self, index = None):
        sizes = [os.path.getsize(message) for message in self.messages]
        if index is None:
            return sizes
        return sizes[index]

    def getMessage(self, index):
        return open(self.messages[index], "rb")

    def getMessageCount(self):
        return len(self.messages)

    def deleteMessage(self, index):
        self.deleted.add(index - 1)

    def undelete(self, index):
        self.deleted.discard(index - 1)

    def sync(self):
        for index in sorted(self.deleted, reverse=True):
            os.remove(self.messages[index])
        self.deleted.clear()

    def getUidl(self, index):
        return os.path.basename(self.messages[index])

class PortalFactory(Factory):
    def __init__(self, authPortal):
        self.portal = authPortal

    def buildProtocol(self, addr):
        popPortal = pop3.POP3()
        popPortal.portal = self.portal
        return popPortal

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--storage', required=True, help="Email Storage Path")
    parser.add_argument('-p', '--port', type=int, required=True, help="Server Port")
    args = parser.parse_args()
    users = uServices.loadUsers()
    realm = MailRealm(args.storage)
    authPortal = portal.Portal(realm)
    authPortal.registerChecker(uServices.UserValidator(users))
    factory = PortalFactory(authPortal)
    reactor.listenTCP(args.port, factory)
    print(f"POP3 corriendo en puerto {args.port}")
    reactor.run()

if __name__ == "__main__":
    main()
