
from tornado import iostream
import socket


def get_nodes(callback, stream, data):
    stream.write("nodes\n")
    stream.read_until("\n.\n", lambda data: callback(stream, data))


def get_metrics(callback, stream, data):
    node = data.strip(".\n ")
    stream.write("list {0}\n".format(node))
    stream.read_until("\n", lambda data: callback(node, stream, data))


def fetch_data(callback, metrics, buff, stream, data):
    metric = metrics.pop()
    if not metrics:

        def cbk(sr, da):
            x = da.strip(".\n ")
            x = metric + "." + x.replace(".value", "")
            x = x.replace("\n", "\n" + metric + ".")
            if x == "# Unknown service":
                b = buff
            else:
                b = buff + x + "\n"
            callback(sr, b)
    else:

        def cbk(sr, da):
            x = da.strip(".\n ")
            x = metric + "." + x.replace(".value", "")
            x = x.replace("\n", "\n" + metric + ".")
            if x == "# Unknown service":
                b = buff
            else:
                b = buff + x + "\n"
            fetch_data(callback, metrics, b, sr, da)

    stream.write("fetch {0}\n".format(metric))
    stream.read_until("\n.\n", lambda data: cbk(stream, data))


class MuninNodeClient(iostream.IOStream):

    @classmethod
    def list_nodes(cls, callback=None, host="127.0.0.1", port=4949):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)
        client.get_nodes(callback)

    @classmethod
    def list_metrics(cls, callback=None, host="127.0.0.1", port=4949):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)
        client.get_metrics(callback)

    @classmethod
    def fetch_data(cls, metrics=None, callback=None, host="127.0.0.1", port=4949):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)
        client.get_data(callback, metrics)

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

    def get_data(self, callback, metrics=None):
        if metrics is None:
            raise NotImplementedError
        else:
            self.open(lambda s, d: fetch_data(callback, metrics, "", s, d))


class GraphitePlaintextClient(iostream.IOStream):

    @classmethod
    def send_data(cls, data, host="127.0.0.1", port=2003):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client = cls(s, host, port)
        client.open(data)

    def __init__(self, sock, host="127.0.0.1", port=2003):
        self.host = host
        self.port = port
        self.set_close_callback(self.on_closed)
        super(GraphitePlaintextClient, self).__init__(sock)

    def open(self, data):
        self.connect((self.host, self.port), lambda: self.on_connected(data))

    def on_connected(self, data):
        self.write("{0}\n".format(data.strip()))

    def on_closed(self, *args, **kwargs):
        print "closed", args, kwargs


if __name__ == "__main__":
    from tornado import ioloop

    g = GraphitePlaintextClient.send_data("x.y.z 55 234523423", "127.0.0.1")

    ioloop.IOLoop.instance().start()
