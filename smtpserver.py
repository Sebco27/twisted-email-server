import argparse
import os
import time
from twisted.mail import smtp
from twisted.internet import reactor, defer
from zope.interface import implementer

@implementer(smtp.IMessageDelivery)
class PostOffice:
    def __init__(self, storagePath):
        self.storagePath = storagePath

    def receivedHeader(self, helo, origin, recipients):
        sender = origin
        if isinstance(sender, bytes):
            sender = sender.decode("utf-8")
        senderIP = helo[1]
        if isinstance(senderIP, bytes):
            senderIP = senderIP.decode("utf-8")
        return f"Received: from {sender} ({senderIP})"

    def validateFrom(self, helo, origin):
        return origin

    def validateTo(self, user):
        username = user.dest.local
        domain = user.dest.domain
        if not domain:
            raise smtp.SMTPBadRcpt(user)
        mailbox = os.path.join(self.storagePath, username.decode("utf-8"))
        os.makedirs(mailbox, exist_ok=True)
        return lambda: Message(mailbox)

@implementer(smtp.IMessage)
class Message:
    def __init__(self, storagePath):
        self.message = []
        self.storagePath = storagePath

    def lineReceived(self, strLine):
        if isinstance(strLine, bytes):
            strLine = strLine.decode("utf-8")
        self.message.append(strLine)

    def eomReceived(self):
        emailFilename = os.path.join(self.storagePath, f"email-{int(time.time() * 1000)}.txt")
        with open(emailFilename, "w", encoding="utf-8") as filename:
            filename.write("\n".join(self.message))
        print("New mail received!")
        return defer.succeed(None)

class ProtocolFactory(smtp.SMTPFactory):
    def __init__(self, domains, storagePath):
        self.domains = domains
        self.storagePath = storagePath

    def buildProtocol(self, addr):
        protocol = smtp.SMTP()
        protocol.delivery = PostOffice(self.storagePath)
        return protocol

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domains', required=True, help="Allowed Domains")
    parser.add_argument('-s', '--storage', required=True, help="Email Storage Path")
    parser.add_argument('-p', '--port', type=int, required=True, help="Server Port")
    args = parser.parse_args()
    print("Starting SMTP Server...")
    reactor.listenTCP(args.port, ProtocolFactory(args.domains, args.storage))
    print(f"Accepted Domains: {args.domains}")
    print(f"Storage Path: {args.storage}")
    print(f"SMTP Server running on port {args.port}")
    reactor.run()

if __name__ == "__main__":
    main()
