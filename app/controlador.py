from .modelo import Service, BusquedaDTO, BusquedaError
from .vista import VistaPrincipal, CancionDTO


class Controlador:
    def __init__(self):
        self.modelo = Service()
        self.vista = VistaPrincipal()

        self.vista.buscar.connect(self.__on_buscar)

    def __on_buscar(self):
        self.modelo.almacenar_refresh_token()

        self.vista.limpiar_lista()
        dto = self.vista.obtener_busqueda()
        busqueda = BusquedaDTO(dto.consulta)

        try:
            canciones = [
                CancionDTO(cancion.nombre, cancion.artista)
                for cancion in self.modelo.obtener_canciones(busqueda)
            ]
            self.vista.actualizar_lista(canciones)
        except BusquedaError:
            return

    def show_vista(self):
        self.vista.show()
