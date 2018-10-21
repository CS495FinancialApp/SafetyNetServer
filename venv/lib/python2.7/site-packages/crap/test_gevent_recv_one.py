
import time
import sys
import threading

import wstools
import websocket

conn_count = int(sys.argv[1])
msg_count = int(sys.argv[2])
conns = wstools.create_conns(conn_count, "room-recv_one")

recv_conn = conns.pop(0)
msg_total = len(conns) * msg_count

def recv_cleanup(ws):
    global msg_total
    msg_count = 0
    try:
        while msg_count < msg_total:
            try:
                msg = ws.recv()
                if msg:
                    msg_count += 1
                    print "{} received msg {} with val {} in room {}".format(ws.user, msg_count, msg, ws.room)

            except websocket.WebSocketTimeoutException:
                pass

    except websocket.WebSocketConnectionClosedException:
        pass

    print "total messages received {}".format(msg_count)

t = threading.Thread(target=recv_cleanup, args=[recv_conn])
t.daemon = True
t.start()

wstools.send_msgs(conns, msg_count)

conns.append(recv_conn)
wstools.close_on_sigint(conns)

