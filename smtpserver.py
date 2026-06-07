import argparse
import csv
import os
import time
from twisted.mail import smtp
from twisted.internet import reactor, defer
from zope.interface import implementer

@implementer(smtp.IMessageDelivery)
class PostOffice:
    def __init__(self, storagePath, domains):
        self.storagePath = storagePath
        self.domains = domains

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
        username = user.dest.local.decode("utf-8")
        domain = user.dest.domain.decode("utf-8")
        if not domain or domain not in self.domains:
            raise smtp.SMTPBadRcpt(user)
        mailbox = os.path.join(self.storagePath, username)
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
        emailFilename = os.path.join(self.storagePath, f"email-{int(time.time() * 1000)}.eml")
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
        protocol.delivery = PostOffice(self.storagePath, self.domains)
        return protocol

def loadAllowedDomains(domainsCSV):
    allowedDomains = []
    with open(domainsCSV) as csvFile:
        rows = csv.DictReader(csvFile)
        for row in rows:
            allowedDomains.append(row["Domain"])
    return allowedDomains

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domains', required=True, help="Allowed Domains")
    parser.add_argument('-s', '--storage', required=True, help="Email Storage Path")
    parser.add_argument('-p', '--port', type=int, required=True, help="Server Port")
    args = parser.parse_args()
    domains = loadAllowedDomains(args.domains)
    print("Starting SMTP Server...")
    reactor.listenTCP(args.port, ProtocolFactory(domains, args.storage))
    print(f"Accepted Domains: {domains}")
    print(f"Storage Path: {args.storage}")
    print(f"SMTP Server running on port {args.port}")
    reactor.run()

if __name__ == "__main__":
    main()
