import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta
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


class BusquedaError(Exception):
    def __str__(self):
        return "Busqueda sin resultados"


@dataclass
class CancionDTO:
    id: str
    nombre: str
    artista: str


@dataclass
class BusquedaDTO:
    consulta: str


@dataclass
class DispositivoDTO:
    id: str
    nombre: str

@dataclass
class ReproduccionDTO:
    id_dispositivo: str
    id_cancion: str


class Service:
    def __solicitar_permisos(self):
        server = Server()
        Spotify.autorizar_usuario()
        server.activate()

        if server.code:
            return server.code
        if server.error:
            raise Exception(str(server.error))

    def __obtener_access_token(self):
        try:
            with open("app/.refresh_token", "r") as archivo:
                refresh_token = archivo.read()
        except FileNotFoundError:
            raise Exception("Refresh token no generado")

        data = Spotify.actualizar_access_token(refresh_token)
        return data["access_token"]

    def almacenar_refresh_token(self):
        if path.isfile("app/.refresh_token"):
            return

        try:
            code = self.__solicitar_permisos()
        except Exception:
            return

        data = Spotify.obtener_refresh_token(code)
        refresh_token = data["refresh_token"]
        access_token = data["access_token"]

        with open("app/.refresh_token", "w") as archivo:
            archivo.write(refresh_token)

    def obtener_canciones(self, data: BusquedaDTO):
        canciones = list()
        access_token = self.__obtener_access_token()
        busqueda = Spotify.buscar_canciones(access_token, data.consulta)

        try:
            for item in busqueda["tracks"]["items"]:
                id = item["artists"][0]["uri"]
                nombre = item["name"]
                artista = item["artists"][0]["name"]
                canciones.append(CancionDTO(id, nombre, artista))
        except KeyError:
            raise BusquedaError

        return canciones

    def obtener_dispositivos(self):
        dispositivos = list()
        access_token = self.__obtener_access_token()
        dispositivos_disponibles = Spotify.buscar_dispositivo(access_token)

        try:
            for item in dispositivos_disponibles:
                id_dispositivo = item["id"]
                nombre_dispositivo = item["name"]
                dispositivos.append(DispositivoDTO(id_dispositivo, nombre_dispositivo))
        except KeyError:
            raise DispositivoError

        return dispositivos
