from dataclasses import dataclass
from os import path
from threading import Thread

from .server import Server
from .recursos import Spotify


class BusquedaError(Exception):
    def __str__(self):
        return "Busqueda sin resultados"


class AccesoError(Exception):
    def __init__(self, mensaje):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje


class TokenError(Exception):
    def __str__(self):
        return "Refresh token no generado"


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


@dataclass
class PausarDTO:
    id_dispositivo: str


@dataclass
class ReanudarDTO:
    id_dispositivo: str


class Service:
    def __solicitar_permisos(self):
        server = Server()
        Spotify.autorizar_usuario()
        server.activate()

        if server.code:
            return server.code
        if server.error:
            raise AccesoError(str(server.error))

    def __obtener_access_token(self):
        try:
            with open("app/.refresh_token", "r") as archivo:
                refresh_token = archivo.read()
        except FileNotFoundError:
            raise TokenError

        data = Spotify.actualizar_access_token(refresh_token)
        return data["access_token"]

    def almacenar_refresh_token(self):
        if path.isfile("app/.refresh_token"):
            return

        try:
            code = self.__solicitar_permisos()
        except AccesoError:
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
                id = item["uri"]
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

    def reproducir_cancion(self, data: ReproduccionDTO):
        access_token = self.__obtener_access_token()
        Thread(
            target=Spotify.reproducir,
            args=(access_token, data.id_dispositivo, data.id_cancion),
        ).start()

    def pausar_cancion(self, data: PausarDTO):
        access_token = self.__obtener_access_token()
        Thread(target=Spotify.pausar, args=(access_token, data.id_dispositivo)).start()

    def reanudar_cancion(self, data: ReanudarDTO):
        access_token = self.__obtener_access_token()
        Thread(
            target=Spotify.reanudar, args=(access_token, data.id_dispositivo)
        ).start()
