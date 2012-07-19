import sys
import time

from tornado import ioloop

from connection import MuninNodeClient


if __name__ == "__main__":

    timeout = int(sys.argv[1]) * 1000
    filename = sys.argv[2]

    def result_callback(node, stream, data):
        now = int(time.time())
        with open(filename, "a+") as fd:
            data = data.strip()
            data = data.replace("\n", " {0}\n{1}.".format(now, node)) + " {0}".format(now)
            fd.write(data.strip())

    def cbk(node, client, data):
        metrics = data.strip().split()
        MuninNodeClient.fetch_data(metrics, lambda s, d: result_callback(node, s, d))

    def task():
        MuninNodeClient.list_metrics(cbk)

    p = ioloop.PeriodicCallback(task, timeout)
    p.start()

    ioloop.IOLoop.instance().start()
