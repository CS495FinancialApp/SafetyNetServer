
import time
import sys

import wstools

conn_count = int(sys.argv[1])
msg_count = int(sys.argv[2])
conns = wstools.create_conns(conn_count)

for ws in conns:
    for c in range(msg_count):
        msg = "msg-{}".format(c)
        print "{} sending message {} to room {}".format(ws.user, msg, ws.room)
        ws.send(msg)
        time.sleep(0.01)


def ctrl_c(signal, frame):
    global conns
    for c, ws in enumerate(conns):
        print "disconnecting user-{}".format(c)
        ws.close()

wstools.wait_for_sigint(ctrl_c)

