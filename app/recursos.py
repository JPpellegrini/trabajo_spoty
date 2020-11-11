import webbrowser
from datetime import datetime, timedelta
from os import getenv
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

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
            scope=" ".join(
                [
                    "user-read-playback-state",
                    "user-modify-playback-state",
                ]
            ),
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

    def buscar_canciones(token, consulta):
        url = "https://api.spotify.com/v1/search"
        header = dict(Authorization=f"Bearer {token}")
        data = dict(
            q=consulta.replace(" ", "+"),
            type="track",
        )
        response = requests.get(url, data, headers=header)
        return response.json()

    def buscar_dispositivo(token):
        url = "https://api.spotify.com/v1/me/player/devices"
        header = dict(Authorization=f"Bearer {token}")
        response = requests.get(url, headers=header)
        return response.json()["devices"]

    def reproducir(token, device_id, tracks):
        url = "https://api.spotify.com/v1/me/player/play"
        header = dict(Authorization=f"Bearer {token}")
        params = dict(device_id=device_id)
        tracks = dict(uris=[tracks])
        requests.put(url, headers=header, params=params, json=tracks)

    def pausar(token, device_id):
        url = "https://api.spotify.com/v1/me/player/pause"
        header = dict(Authorization=f"Bearer {token}")
        params = dict(device_id=device_id)
        requests.put(url, headers=header, params=params)

    def reanudar(token, device_id):
        url = "https://api.spotify.com/v1/me/player/play"
        header = dict(Authorization=f"Bearer {token}")
        params = dict(device_id=device_id)
        requests.put(url, headers=header, params=params)
