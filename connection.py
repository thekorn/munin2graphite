from tornado import ioloop
from tornado import iostream
import socket


def send_request():
    stream.read_until("\n", on_headers)


def on_headers(data):
    print data
    stream.close()
    ioloop.IOLoop.instance().stop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
stream = iostream.IOStream(s)
stream.connect(("127.0.0.1", 4949), send_request)
ioloop.IOLoop.instance().start()
