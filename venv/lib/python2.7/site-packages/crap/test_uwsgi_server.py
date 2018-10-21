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
        #print "polling {}".format(query['user'])
        try:
            # we are going to listen on uwsgi and redis
            msg = uwsgi.websocket_recv_nb()
            if msg:
                print "sending {} in {} from {}".format(msg, query['room'], query['user'])
                r.publish(query['room'], ws2redis_msg(websocket_fd, query['user'], msg))

            msg = channel.get_message()
            if msg:
                if msg['type'] == 'message':
                    container = redis2ws_msg(msg['data'])
                    if container['user'] != query['user']:
                        print "received {} in {} from {}".format(container['text'], query['room'], container['user'])
                        uwsgi.websocket_send(container['text'])

        except IOError as e:
            print "#" * 80
            print "# IOERROR - {} for {}".format(e, query['user'])
            print "#" * 80
            break

        except Exception as e:
            print "*" * 80
            print str(e)
            print "*" * 80
            break

        finally:
            #channel.unsubscribe(query['room'])
            pass



    return ['']

