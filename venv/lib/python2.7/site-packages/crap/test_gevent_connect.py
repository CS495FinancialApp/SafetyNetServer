import sys

import wstools

conn_count = int(sys.argv[1])
conns = wstools.create_conns(conn_count)

def ctrl_c(signal, frame):
    global conns
    for c, ws in enumerate(conns):
        print "disconnecting user-{}".format(c)
        ws.close()

wstools.wait_for_sigint(ctrl_c)

