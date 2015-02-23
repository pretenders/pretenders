import sys
from twisted.cred import checkers, credentials, portal
from twisted.conch import avatar, interfaces as conchinterfaces
from twisted.conch.ssh import channel, factory, keys, session
from twisted.internet import defer, reactor
from twisted.python import log
from zope.interface import implements


log.startLogging(sys.stderr)

publicKey = ('ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPr'
             'J3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTw'
             'TTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV')

privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""


recorded = []


class PatchedSSHSession(session.SSHSession):
    def loseConnection(self):
        if getattr(self.client, 'transport', None) is not None:
            self.client.transport.loseConnection()
        channel.SSHChannel.loseConnection(self)


class PretendAvatar(avatar.ConchUser):
    implements(conchinterfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': PatchedSSHSession})

    def openShell(self, protocol):
        raise NotImplementedError("Interactive shell not supported")

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        print("Command: [{0}]".format(cmd))
        recorded.append(cmd)
        command = ('/bin/bash', '-c', 'echo "<dummy response>"')
        reactor.spawnProcess(protocol, '/bin/bash', command)

    def eofReceived(self):
        pass

    def closed(self):
        pass


class PretendRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if conchinterfaces.IConchUser in interfaces:
            return interfaces[0], PretendAvatar(avatarId), lambda: None
        else:
            raise Exception("No supported interfaces found.")


class RecordPassAllCredentials:
    """
    Simply record credentials and pass.
    """
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = credentials.IUsernamePassword,
    users = []

    def requestAvatarId(self, credentials):
        user = credentials.username
        print("User: [{0}]".format(user))
        self.users.append(user)
        return defer.succeed(user)


def run(host='127.0.0.1', port=2222):
    """
    Run a pretend SSH server.
    """
    sshFactory = factory.SSHFactory()
    sshFactory.portal = portal.Portal(PretendRealm())
    sshFactory.portal.registerChecker(RecordPassAllCredentials())

    sshFactory.publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=publicKey)
    }
    sshFactory.privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=privateKey)
    }

    reactor.listenTCP(port, sshFactory, interface=host)
    reactor.run()


if __name__ == "__main__":
    try:
        run()
    finally:
        print("Commands recorded:")
        print("\n".join(recorded))
