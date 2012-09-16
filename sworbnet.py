#!/usr/bin/python2.7

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import ssl, reactor

class SworbNet:
    def __init__(self):
        self.hashes = {} # dict of hashes->file handle
        self.connections = []
    def addHash(self, hash, handle):
        self.hashes[hash] = handle

class SworbMessaging(Protocol):
    def __init__(self, factory, snet=None):
        self.factory = factory
        self.snet = snet

    def connectionMade(self):
        self.transport.write("ID 1") # TODO send back our IDo
        self.factory.numProtocols += 1

    def connectionLost(self, reason):
        self.factory.numProtocols -= 1

    def dataReceived(self, data):
        str = data.split(" ")

        try:
            # Hash lookup
            if str[0] is "0":
                if self.snet.hashes[str[1]] is not None:
                    # sucessful lookup
                    self.transport.write("1")
                else:
                    self.transport.write("0")
                    # TODO ask other people we are connected to if they have it

            # File request
            if str[0] is "1":
                # TODO get file
                pass

        except:
            self.transport.write("ILLEGAL")

class SMFactory(Factory):
    def __init__(self, net):
        self.net = net
    def buildProtocol(self, addr):
        return SworbMessaging(self, snet=self.net)

if __name__ == "__main__":
    net = SworbNet()

    factory = SMFactory(net)

    reactor.listenSSL(8666, factory, ssl.DefaultOpenSSLContextFactory(
        'keys/server.key', 'keys/server.crt'))

    reactor.run()
