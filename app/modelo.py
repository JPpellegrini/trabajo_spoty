import webbrowser
from os import getenv, path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from .server import Server


load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")


class TokenCache:
    def __init__(self):
        self.next_refresh = None
        self.data = None

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            if not self.data or datetime.now() >= self.next_refresh:
                last_refresh = datetime.now()
                self.data = function(*args, **kwargs)
                self.next_refresh = last_refresh + timedelta(
                    seconds=self.data["expires_in"]
                )

            return self.data

        return wrapper


class Spotify:
    def autorizar_usuario():
        url = "https://accounts.spotify.com/authorize"
        parameters = dict(
            client_id=CLIENT_ID,
            response_type="code",
            redirect_uri=REDIRECT_URI,
        )
        url += "?" + urlencode(parameters)
        webbrowser.open(url)

    def obtener_refresh_token(code):
        url = "https://accounts.spotify.com/api/token"
        data = dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=REDIRECT_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        response = requests.post(url, data)
        return response.json()

    @TokenCache()
    def actualizar_access_token(token):
        url = "https://accounts.spotify.com/api/token"
        data = dict(
            grant_type="refresh_token",
            refresh_token=token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        response = requests.post(url, data)
        return response.json()


class Service:
    def solicitar_permisos(self):
        server = Server()
        Spotify.autorizar_usuario()
        server.activate()

        if server.code:
            return server.code
        if server.error:
            raise Exception(str(server.error))

    def almacenar_refresh_token(self):
        if path.isfile(".refresh_token"):
            return

        try:
            code = self.solicitar_permisos()
        except Exception:
            return

        data = Spotify.obtener_refresh_token(code)
        refresh_token = data["refresh_token"]
        access_token = data["access_token"]

        with open(".refresh_token", "w") as archivo:
            archivo.write(refresh_token)
