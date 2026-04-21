from twisted.mail import smtp
from twisted.internet import reactor, defer
from zope.interface import implementer

@implementer(smtp.IMessageDelivery)
class PostOffice:
    def receivedHeader(self, helo, origin, recipients):
        sender = helo[0]
        if isinstance(sender, bytes):
            sender = sender.decode("utf-8")
        senderIP = helo[1]
        if isinstance(senderIP, bytes):
            senderIP = senderIP.decode("utf-8")
        return f"Received: from {sender} ({senderIP})"

    def validateFrom(self, helo, origin):
        return origin

    def validateTo(self, user):
        domain = user.dest.domain
        if not domain:
            raise smtp.SMTPBadRcpt(user)
        return lambda: Message()

@implementer(smtp.IMessage)
class Message:
    def __init__(self):
        self.message = []

    def lineReceived(self, strLine):
        if isinstance(strLine, bytes):
            strLine = strLine.decode("utf-8")
        self.message.append(strLine)

    def eomReceived(self):
        print("----- NUEVO MENSAJE -----")
        print("\n".join(self.message))
        print("-------------------------")
        return defer.succeed(None)

class Protocol(smtp.SMTPFactory):
    def buildProtocol(self, addr):
        protocol = smtp.SMTP()
        protocol.delivery = PostOffice()
        return protocol

def main():
    reactor.listenTCP(2525, Protocol())
    reactor.run()

if __name__ == "__main__":
    main()
