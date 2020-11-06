from .modelo import Service, BusquedaDTO, BusquedaError, TokenError
from .vista import VistaPrincipal, CancionDTO, DispositivoDTO


class Controlador:
    def __init__(self):
        self.__modelo = Service()
        self.__vista = VistaPrincipal()

        self.__vista.buscar.connect(self.__on_buscar)
        self.__vista.play.connect(self.__on_play)
        self.__vista.actualizar.connect(self.__on_actualizar)

        self.__vista.actualizar.emit()

    def __on_buscar(self):
        try:
            self.__modelo.almacenar_refresh_token()
        except TokenError:
            return

        dto = self.__vista.obtener_busqueda()
        busqueda = BusquedaDTO(dto.consulta)
        
        try:
            canciones = [
                CancionDTO(cancion.id, cancion.nombre, cancion.artista)
                for cancion in self.__modelo.obtener_canciones(busqueda)
            ]
            self.__vista.actualizar_canciones(canciones)
        except BusquedaError:
            self.__vista.actualizar_canciones()

    def __on_actualizar(self):
        dispositivos = [
            DispositivoDTO(dispositivo.id, dispositivo.nombre)
            for dispositivo in self.__modelo.obtener_dispositivos()
        ]
        self.__vista.actualizar_dispositivos(dispositivos)

    def __on_play(self):
        pass

    def show_vista(self):
        self.__vista.show()
