from twisted.cred import credentials, error
from twisted.cred.checkers import ICredentialsChecker
from twisted.internet import defer
from zope.interface import implementer

ENV_PATH = ".env"

def loadUsers():
    usernames = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                username, password = line.split("=", 1)
                usernames[username.strip()] = password.strip()
    return usernames

@implementer(ICredentialsChecker)
class UserValidator:
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, users):
        self.users = users

    def requestAvatarId(self, credentials):
        emailAdress = credentials.username.decode()
        username = emailAdress.split("@")[0]
        password = credentials.password.decode()
        if username in self.users and self.users[username] == password:
            return defer.succeed(username)
        return defer.fail(error.UnauthorizedLogin())
