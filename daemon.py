import sys
import time

from tornado import ioloop

from connection import MuninNodeClient, GraphitePlaintextClient


if __name__ == "__main__":

    timeout = int(sys.argv[1]) * 1000
    filename = sys.argv[2]

    def result_callback(node, stream, data):
        now = int(time.time())
        data = data.strip()
        data = data.replace("\n", " {0}\ny{1}.".format(now, node)) + " {0}".format(now)
        data = data.strip()
        # with open(filename, "a+") as fd:
        #     fd.write(data.strip())
        GraphitePlaintextClient.send_data(data, host="srv00187.edelight.net")

    def cbk(node, client, data):
        metrics = data.strip().split()
        MuninNodeClient.fetch_data(metrics, lambda s, d: result_callback(node, s, d))

    def task():
        MuninNodeClient.list_metrics(cbk)

    p = ioloop.PeriodicCallback(task, timeout)
    p.start()

    ioloop.IOLoop.instance().start()
