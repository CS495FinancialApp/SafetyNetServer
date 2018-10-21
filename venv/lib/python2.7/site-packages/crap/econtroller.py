import time

from endpoints import Controller

class Default(Controller):
    def GET(self, *args, **kwargs):
        return "boom"

    def POST(self, **kwargs):
        pout.v(kwargs)
        return "bam"

class Gen(Controller):
    def GET(self, *args, **kwargs):
        pout.b('before')
        yield "pow"
        #yield None
        pout.b('after')
        time.sleep(3)
        pout.b("more after")


class Yieldtest(Controller):
    def GET(self, *args, **kwargs):
        pout.b('before yt')
        yield None
        #yield "something"
        #yield ""
        pout.b('after yt')
        time.sleep(30)
        pout.b("more after yt")


class Wait(Controller):
    def GET(self, *args, **kwargs):
        pout.b("starting to wait")
        pout.v(self.request)
        time.sleep(5)
        pout.b("done waiting")


