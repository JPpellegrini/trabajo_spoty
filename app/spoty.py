import webbrowser
from os import getenv, system
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv, find_dotenv, set_key
import cherrypy

system("fuser 8888/tcp -k")
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")

class Autenticar:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI
    
    def autorizar(self):
        url = "https://accounts.spotify.com/authorize"
        parametros = dict (
            client_id = self.client_id,
            response_type = "code",
            redirect_uri = self.redirect_uri
        )
        nueva_url = url+"?"+urlencode(parametros)
        return nueva_url

class Server_local:
    autentificacion_code = None
    autentificacion_error = None

    class Handler:
        def __init__(self, reciver):
            self.reciver = reciver
            
        @cherrypy.expose
        def index(self, code = None, error = None):
            self.reciver(code = code, error = None)

    def __init__(self):
        cherrypy.config.update({
            "server.socket_port" : 8888,
        })
        cherrypy.tree.mount(Server_local.Handler(self.procesar_codigo))
    
    def procesar_codigo(self, code=None, error = None):
        self.autentificacion_code = code
        self.autentificacion_error = error
        cherrypy.engine.exit()

    def start(self):
        cherrypy.engine.start()
        cherrypy.engine.block()

class Token:
    def __init__(self):
        self.url_token = "https://accounts.spotify.com/api/token"

    def solicitar(self, autentificacion_code):
        parametros_solicitud = dict(
            grant_type = "authorization_code",
            code = autentificacion_code,
            redirect_uri = REDIRECT_URI,
            client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET
        )
        respuesta = requests.post(self.url_token, parametros_solicitud)
        set_key(dotenv_file, "ACCESS_TOKEN", respuesta.json()['access_token'])
        set_key(dotenv_file, "REFRESH_TOKEN", respuesta.json()['refresh_token'])
    
    def refrescar(self):
        parametros_refresco = dict(
            grant_type = "refresh_token",
            refresh_token = getenv("REFRESH_TOKEN"),
            client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET
        )
        respuesta = requests.post(self.url_token, parametros_refresco)
        set_key(dotenv_file, "ACCESS_TOKEN", respuesta.json()['access_token'])
    
class Solicitar:
    def __init__(self):
        self.token = getenv("ACCESS_TOKEN")

    def Mostrar_playlists(self):
        respuesta = requests.post("https://api.spotify.com/v1/me/playlists",
            headers = dict (Authorization=f'Bearer {self.token}')
        )
        print(respuesta.json)
        for item in respuesta.json()["items"]:
            print(item["name"])

autentificacion = Autenticar().autorizar()
webbrowser.open(autentificacion)
server = Server_local()
server.start()
solicitud_token = Token()
code = server.autentificacion_code
solicitudes = Solicitar()
try:
    solicitud_token.solicitar(code)
    solicitud_token.refrescar()
    solicitudes.Mostrar_playlists()
except AttributeError:
    raise Exception("Error de Autentificacion")
