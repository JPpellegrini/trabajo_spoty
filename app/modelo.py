import webbrowser
from os import getenv
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENTE_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")


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

    def actualizar_access_token(token):
        url = "https://accounts.spotify.com/api/token"
        data = dict(
            grant_type="refresh_token",
            refresh_token=token,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        response = requests.post(url, data)
