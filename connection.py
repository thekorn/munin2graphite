from tornado import ioloop
from tornado import iostream
import socket


def default_callback(stream, data):
    print data.strip()
    stream.close()
    ioloop.IOLoop.instance().stop()


def get_nodes(callback, stream, data):
    stream.write("nodes\n")
    stream.read_until("\n", lambda data: callback(stream, data))


def get_metrics(callback, stream, data):
    node = data.strip()
    print ">>>>>>", node, callback
    stream.write("list {0}\n".format(node))
    stream.read_until("\n\n", lambda data: callback(stream, data))


class MuninNodeClient(iostream.IOStream):

    @classmethod
    def list_nodes(cls, callback=None, host="127.0.0.1", port=4949):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)

        if callback is None:
            callback = default_callback
        client.get_nodes(callback)

    @classmethod
    def list_metrics(cls, callback=None, host="127.0.0.1", port=4949):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)

        if callback is None:
            callback = default_callback
        client.get_metrics(callback)

    def __init__(self, sock, host="127.0.0.1", port=4949):
        self.host = host
        self.port = port
        super(MuninNodeClient, self).__init__(sock)

    def open(self, callback=None):
        self.connect((self.host, self.port), lambda: self.on_connected(callback))

    def on_connected(self, callback):
        self.read_until("\n", lambda data: self.on_banner(data, callback))

    def on_banner(self, data, callback):
        if "munin node at" not in data:
            raise RuntimeError("Not allowed")
        callback(self, data)

    def get_nodes(self, callback):
        self.open(lambda s, d: get_nodes(callback, s, d))

    def get_metrics(self, callback):
        cbk = lambda st, da: get_metrics(callback, st, da)
        self.open(lambda s, d: get_nodes(cbk, s, d))


c = MuninNodeClient.list_metrics()
ioloop.IOLoop.instance().start()
