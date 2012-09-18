#!/usr/bin/python2.7

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import ssl, reactor
from hasher import FileHasher

import ConfigParser

class SworbNet:
    def __init__(self):
        self.hashes = {} # dict of hashes->file location
        self.clients = []
        self.connections = []
    def addHash(self, hash, handle):
        self.hashes[hash] = handle
    def addClient(self, client):
        self.clients.append(client)

class SworbGetFileByHashClient(Protocol):
    def connectionMade(self):
        # ask for the hash
        self.transport.write("0 " + self.factory.hash)
        self.file = False
        self.f = open(self.factory.filename, 'w')

    def dataReceived(self, data):
        if self.file is False:
            if data is "1":
                # they have it, ask for it!
                self.transport.write("1 " + self.factory.hash)
                self.file = True
            else:
                self.transport.loseConnection()
        else:
            # we're getting the file
            if self.passthrough is True:
                self.factory.ptransport.write(data)
            else:
                self.f.write(data)
                self.f.close()

class SGetFileByHashFactory(Factory):
    def __init__(self, net, hash, filename, passthrough=False, t=None):
        self.net = net
        self.hash = hash
        self.filename = filename
        self.protocol = SworbGetFileByHashClient
        self.passthrough = passthrough
        self.ptransport = t

    def clientConnectionFailed(self, connector, reason):
        print "Failed connection - " + reason
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - " + reason

class SworbServer(Protocol):
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
                    for client in self.snet.clients:
                        host = client.split(":")[0]
                        port = client.split(":")[1]

                        cfactory = SGetFileByHashFactory(str[1], str[1], passthrough=True,
                                t=self.transport)
                        reactor.connectSSL(host, port, cfactory, ssl.ClientContextFactory())

            # File request
            if str[0] is "1":
                # TODO get file
                pass

        except:
            self.transport.write("ILLEGAL")

class SSFactory(Factory):
    def __init__(self, net):
        self.net = net
    def buildProtocol(self, addr):
        return SworbServer(self, snet=self.net)

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read("sworbnet.cfg")

    clients = config.get("clients", "clients").split(",")
    port = config.getint("server", "port")

    sharepath = config.get("server", "share")
    hasher = FileHasher(sharepath)

    net = SworbNet()

    for c in clients:
        net.addClient(c)

    serverfactory = SSFactory(net)

    reactor.listenSSL(port, serverfactory, ssl.DefaultOpenSSLContextFactory(
        'keys/server.key', 'keys/server.crt'))

    reactor.run()
