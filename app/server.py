import cherrypy


class Handler:
    def __init__(self, set_data):
        self.set_data = set_data

    @cherrypy.expose
    def index(self, code=None, error=None):
        self.set_data(code, error)


class Server:
    def __init__(self):
        port = cherrypy.config.update(
            {
                "server.socket_port": 8888,
            }
        )
        cherrypy.tree.mount(Handler(self.set_data))

    def set_data(self, code=None, error=None):
        self.error = error
        self.code = code
        self.deactivate()

    def activate(self):
        cherrypy.engine.start()
        cherrypy.engine.block()

    def deactivate(self):
        cherrypy.engine.exit()
