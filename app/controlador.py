from .modelo import Service, BusquedaDTO, BusquedaError, TokenError
from .vista import VistaPrincipal, CancionDTO


class Controlador:
    def __init__(self):
        self.modelo = Service()
        self.vista = VistaPrincipal()

        self.vista.buscar.connect(self.__on_buscar)

    def __on_buscar(self):
        try:
            self.modelo.almacenar_refresh_token()
        except TokenError:
            return
            
        try:
            canciones = [
                CancionDTO(cancion.nombre, cancion.artista)
                for cancion in self.modelo.obtener_canciones(busqueda)
            ]
            self.vista.actualizar_canciones(canciones)
        except BusquedaError:
            self.vista.actualizar_canciones()

    def show_vista(self):
        self.vista.show()
