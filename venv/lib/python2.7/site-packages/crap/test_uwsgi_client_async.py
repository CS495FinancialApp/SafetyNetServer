import threading
import time
import sys
import random
import thread

import pout
from websocket import create_connection
import websocket

lock = threading.Lock()
_, room_count, msg_count = sys.argv
room_count = int(room_count)
msg_count = int(msg_count)

send_msgs = 0
recv_msgs = 0
msgs = set()
missed_msgs = set()


def get_conn(room, user):
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

    return ws


def send(ws, room, user, count):
    global send_msgs
    try:
        for c in range(count):
            try:
                #print "{} sending {}".format(name, count)
                msg = "{}-{}".format(room, c)
                ws.send(msg)
                #print "{} send {}".format(user, msg)
                with lock:
                    msgs.add(msg)
                    send_msgs += 1

            except (websocket.WebSocketConnectionClosedException, websocket.WebSocketTimeoutException):
                print "{} failed on iteration {}".format(user, c)
                #ws.close()
                #ws = get_conn(room, user)
                break
                #raise

            time.sleep(random.triangular(0.05, 0.2))

    except Exception as e:
        print e
        thread.interrupt_main()

    finally:
        #ws.close()
        pass

    print "{} done".format(user)


def recv(ws, room, user, count):
    return
    global recv_msgs
    timeout_count = 0
    did_fail = False
    recv_c = 0
    try:
        while recv_c < count:
            try:
                ret_msg = ws.recv()
                recv_c += 1
                #print "{} received {}".format(user, ret_msg)
                with lock:
                    try:
                        msgs.remove(ret_msg)
                        recv_msgs += 1
                    except KeyError as e:
                        missed_msgs.add(ret_msg)
                        print "{} failed {}".format(user, e)

            except websocket.WebSocketTimeoutException:
                timeout_count += 1
                if timeout_count > 5:
                    print "{} finally timed out".format(user)
                    did_fail = True
                    break

            except websocket.WebSocketConnectionClosedException:
                print "{} failed".format(user)
                #ws.close()
                did_fail = True
                break

            time.sleep(random.triangular(0.01, 0.2))

    except Exception as e:
        print e
        thread.interrupt_main()

    finally:
        #ws.close()
        pass

    print "{} {}".format(user, 'FAILED' if did_fail else 'done')


print "*" * 80
print "* Connecting users to rooms"
print "*" * 80
thread_kwargs = []
conns = []
for room_num in range(room_count):
    room = 'room-{}'.format(room_num)
    print "connecting sender and receiver to {}".format(room)

    user_recv = "u-recv-{}".format(room_num)
    user_send = "u-send-{}".format(room_num)

    ws_recv = get_conn(room, user_recv)
    thread_kwargs.append({'target': recv, 'args': [ws_recv, room, user_recv, msg_count]})

    ws_send = get_conn(room, user_send)
    thread_kwargs.append({'target': send, 'args': [ws_send, room, user_send, msg_count]})

    conns.append(ws_send)
    conns.append(ws_recv)

time.sleep(4)

#sys.exit()

print "*" * 80
print "* Starting threads"
print "*" * 80
threads = []
for kw in thread_kwargs:
    t = threading.Thread(**kw)
    t.daemon = True
    t.start()
    threads.append(t)

print "*" * 80
print "* Waiting for threads to finish"
print "*" * 80

try:
    for t in threads:
        t.join()

except KeyboardInterrupt:
    pass

for ws in conns:
    ws.close()

print "missed {} messages, {} msgs sent, {} msgs received, msgs expected {}, msgs missed {}".format(
    len(msgs),
    send_msgs,
    recv_msgs,
    room_count * msg_count,
    len(missed_msgs)
)

