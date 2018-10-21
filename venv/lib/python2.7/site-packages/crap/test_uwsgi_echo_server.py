import uwsgi
import time
import pout


def application(env, start_response):
    uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
    print "connected"
    count = 0
    while True:
        try:
            msg = uwsgi.websocket_recv()
            #print "echo {}".format(msg)
            count += 1
            #pout.v("received {}".format(msg))
            uwsgi.websocket_send(msg)
            if count % 1000 == 0:
                print "handled {} messages".format(count)
        except IOError as e:
            print str(e.args[0])
            break
        #pout.v("echoed {}".format(msg))
        #time.sleep(5)
        #pout.v("done sleeping, let's read another")

    return ['']

