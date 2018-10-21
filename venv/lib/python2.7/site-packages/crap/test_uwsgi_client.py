import threading
import time

import pout
from websocket import create_connection
import websocket

def run(name):
    count = 0
    ws = None
    while not ws:
        try:
            ws = create_connection("ws://localhost:9000")
        except websocket.WebSocketConnectionClosedException:
            time.sleep(0.25)

    for count in range(1000):
        try:
            #print "{} sending {}".format(name, count)
            msg = "{}-{}-{:f}".format(name, count, time.time())
            ws.send(msg)
            ret_msg = ws.recv()
            if msg != ret_msg:
                print "{} failed {} != {}".format(name, msg, ret_msg)
            else:
                #print "{} received {}".format(name, count)
                pass

        except websocket.WebSocketConnectionClosedException:
            print "{} failed on iteration {}".format(name, count)
            ws = create_connection("ws://localhost:9000")

    print "{} done".format(name)
    ws.close()


if __name__ == "__main__":
    threads = []
    for i in range(1000):
        t = threading.Thread(target=run, args=["t{}".format(i)])
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

