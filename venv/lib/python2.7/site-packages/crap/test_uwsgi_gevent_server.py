import time
import urlparse
import pickle
import random

import gevent.select
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
    #print "user {} connected to {}".format(query['user'], query['room'])

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    channel = r.pubsub(ignore_subscribe_messages=True)
    channel.subscribe(query['room'])

    websocket_fd = uwsgi.connection_fd()
    redis_fd = channel.connection._sock.fileno()
    print "user {} listening on ws {} and redis {} in room {}".format(query['user'], websocket_fd, redis_fd, query['room'])

    try:
        while True:
            try:
                ready = gevent.select.select([websocket_fd, redis_fd], [], [], 5)
                if ready[0]:
                    for fd in ready[0]:
                        if fd == websocket_fd:
                            # we've received a message from this client's websocket
                            msg = uwsgi.websocket_recv_nb()
                            if msg:
                                #print "{} sending {} in {}".format(query['user'], msg, query['room'])
                                r.publish(query['room'], ws2redis_msg(websocket_fd, query['user'], msg))


                        elif fd == redis_fd:
                            #msg = channel.get_message()
                            msg = channel.parse_response()
                            if msg and msg[0] == 'message':
                                container = redis2ws_msg(msg[2])
                                if container['user'] != query['user']:
#                                    print "{} received {} in {} from {}".format(
#                                        query['user'],
#                                        container['text'],
#                                        query['room'],
#                                        container['user']
#                                    )
                                    uwsgi.websocket_send(container['text'])

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

    except Exception as e:
        raise

    finally:
        # we are done with this connection
        channel.unsubscribe(query['room'])
        channel.close()

    return

