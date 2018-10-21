import time
import urlparse
import pickle
import random

import redis
import uwsgi
import pout

def ws2redis_msg(fd, user, msg):
    d = {
        'fd': fd,
        'user': user,
        'text': msg
    }
    return pickle.dumps(d, pickle.HIGHEST_PROTOCOL)

def redis2ws_msg(msg):
    return pickle.loads(msg)


def application(env, start_response):
    query = urlparse.parse_qs(env['QUERY_STRING'])
    for k, kv in query.items():
        if len(kv) > 1:
            query[k] = kv
        else:
            query[k] = kv[0]

    uwsgi.websocket_handshake()
    print "user {} connected to {}".format(query['user'], query['room'])

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    channel = r.pubsub(ignore_subscribe_messages=True)
    channel.subscribe(query['room'])
#    sub_msg = channel.get_message()
#    pout.v(sub_msg)

    websocket_fd = uwsgi.connection_fd()
    redis_fd = channel.connection._sock.fileno()
    print "user {} listening on ws {} and redis {}".format(query['user'], websocket_fd, redis_fd)

    while True:
        try:
            # we are going to listen on uwsgi and redis
            uwsgi.wait_fd_read(websocket_fd, 3)
            uwsgi.wait_fd_read(redis_fd)
            uwsgi.suspend()
            fd = uwsgi.ready_fd()
            if fd > -1:
                if fd == websocket_fd:
                    # we've received a message from this client's websocket
                    msg = uwsgi.websocket_recv_nb()
                    if msg:
                        print "sending {} in {} from {}".format(msg, query['room'], query['user'])
                        r.publish(query['room'], ws2redis_msg(websocket_fd, query['user'], msg))


                elif fd == redis_fd:
                    #msg = channel.get_message()
                    msg = channel.parse_response()
                    if msg and msg[0] == 'message':
                        container = redis2ws_msg(msg[2])
                        if container['user'] != query['user']:
                            print "received {} in {} from {}".format(container['text'], query['room'], container['user'])
                            uwsgi.websocket_send(container['text'])

            else:
                # on timeout call websocket_recv_nb again to manage ping/pong
                msg = uwsgi.websocket_recv_nb()
                if msg:
                    r.publish(query['room'], msg)

        except IOError as e:
            print "#" * 80
            print "# IOERROR - {} for {}".format(e, query['user'])
            print "#" * 80
            raise

        except Exception as e:
            print "*" * 80
            print str(e)
            print "*" * 80
            raise

        finally:
            #channel.unsubscribe(query['room'])
            pass

    return

