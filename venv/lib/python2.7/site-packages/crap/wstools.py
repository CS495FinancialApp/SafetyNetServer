import time
import signal
import sys

from websocket import create_connection
import websocket


def send_msgs(conns, msg_count):
    for ws in conns:
        for c in range(msg_count):
            msg = "msg-{}".format(c)
            print "{} sending message {} to room {}".format(ws.user, msg, ws.room)
            ws.send(msg)
            #time.sleep(0.01)
            time.sleep(0.1)


def create_conns(conn_count, room=''):
    conns = []
    for c in range(conn_count):
        r = room
        if not r:
            r = "room-{}".format(c)

        ws = create_conn(r, "user-{}".format(c))
        print "connecting user-{}".format(c)
        conns.append(ws)

    return conns


def create_conn(room, user):
    ws = None
    while not ws:
        try:
            ws = create_connection(
                "ws://localhost:9000?room={}&user={}".format(room, user),
                timeout=5
            )
        except (websocket.WebSocketConnectionClosedException, websocket.WebSocketTimeoutException):
            print "reconnect for user {} to room {}".format(user, room)
            time.sleep(0.25)

    ws.room = room
    ws.user = user
    return ws


# http://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
def wait_for_sigint(callback):
    def close_callback():
        callback()
        sys.exit(0)

    signal.signal(signal.SIGINT, callback)
    signal.pause()

def close_on_sigint(conns):
    def callback(signal, frame):
        for c, ws in enumerate(conns):
            print "disconnecting user-{}".format(c)
            ws.close()

    wait_for_sigint(callback)

