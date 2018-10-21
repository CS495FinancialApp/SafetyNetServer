from endpoints import Controller

class Default(Controller):
    def POST(self, **kwargs):
        pout.v(kwargs)
        #pout.v(self.request)
        #pout.v(self.request.body_input.read(10000))
        #pout.v(self.request.body)
        pout.v(kwargs['file'].file.read())
        return kwargs['file'].filename

