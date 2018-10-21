from endpoints import Controller

class Default(Controller):
    def GET(self):
        return "default.get"

    def POST(self, **kwargs):
        return "default.post"



class Bar(Controller):
    def GET(self):
        return "bar.get"

