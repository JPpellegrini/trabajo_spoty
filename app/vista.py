from dataclasses import dataclass

from PyQt5 import QtCore, QtWidgets, QtGui

from app.ui.principal import Ui_reproductor


@dataclass
class BusquedaDTO:
    consulta: str


@dataclass
class CancionDTO:
    id: str
    nombre: str
    artista: str
    album: str


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


class VistaPrincipal(QtWidgets.QMainWindow):

    buscar = QtCore.pyqtSignal()
    anterior = QtCore.pyqtSignal()
    play = QtCore.pyqtSignal(object)
    pausa = QtCore.pyqtSignal(object)
    reproducir = QtCore.pyqtSignal(object)
    siguiente = QtCore.pyqtSignal()
    actualizar = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__ui = Ui_reproductor()
        self.__setupUi()

    def __setupUi(self):
        self.__ui.setupUi(self)

        self.__id_cancion_actual = False

        self.__ui.imagen_principal.setPixmap(
            QtGui.QPixmap("app/icons/png/imagen_spoty.png")
        )

        self.__ui.icono_lupa = QtGui.QIcon()
        self.__ui.icono_lupa.addPixmap(
            QtGui.QPixmap("app/icons/png/buscar.png"),
        )
        self.__ui.boton_buscar.setIcon(self.__ui.icono_lupa)

        self.__ui.icono_play = QtGui.QIcon()
        self.__ui.icono_play.addPixmap(
            QtGui.QPixmap("app/icons/png/play.png"),
        )
        self.__ui.boton_play.setIcon(self.__ui.icono_play)

        self.__ui.icono_actualizar = QtGui.QIcon()
        self.__ui.icono_actualizar.addPixmap(
            QtGui.QPixmap("app/icons/png/actualizar.png"),
        )
        self.__ui.boton_actualizar.setIcon(self.__ui.icono_actualizar)

    def on_clicked_buscar(self):
        self.buscar.emit()

    def on_clicked_lista(self):
        self.__cambiar_boton()
        self.__id_cancion_actual = True

    def on_clicked_reproducir(self):
        id_dispositivo = self.__obtener_dispositivo()
        if not id_dispositivo:
            return

        self.__id_cancion_actual = self.__ui.lista.currentItem().data(1)
        self.__cambiar_boton(True)
        self.reproducir.emit(ReproduccionDTO(id_dispositivo, self.__id_cancion_actual))

    def on_clicked_play(self):
        id_dispositivo = self.__obtener_dispositivo()
        if not id_dispositivo:
            return

        if self.__ui.boton_play.isChecked():
            self.__cambiar_boton(True)
            if (
                not self.__id_cancion_actual
                or self.__id_cancion_actual == self.__ui.lista.currentItem().data(1)
            ):
                self.play.emit(ReanudarDTO(id_dispositivo))
            else:
                self.__id_cancion_actual = self.__ui.lista.currentItem().data(1)
                self.reproducir.emit(
                    ReproduccionDTO(id_dispositivo, self.__id_cancion_actual)
                )

        else:
            self.__cambiar_boton()
            self.pausa.emit(PausarDTO(id_dispositivo))

    def on_clicked_actualizar(self):
        self.actualizar.emit()

    def __obtener_dispositivo(self):
        try:
            return self.__ui.combo_dispositivo.currentData().id
        except AttributeError:
            return

    def __cambiar_boton(self, estado=False):
        if estado:
            self.__ui.boton_play.setChecked(estado)
            self.__ui.icono_pausa = QtGui.QIcon()
            self.__ui.icono_pausa.addPixmap(
                QtGui.QPixmap("app/icons/png/pausa.png"),
            )
            self.__ui.boton_play.setIcon(self.__ui.icono_pausa)
        else:
            self.__ui.boton_play.setChecked(estado)
            self.__ui.icono_play = QtGui.QIcon()
            self.__ui.icono_play.addPixmap(
                QtGui.QPixmap("app/icons/png/play.png"),
            )
            self.__ui.boton_play.setIcon(self.__ui.icono_play)

    def __limpiar_lista(self):
        self.__ui.lista.clear()

    def obtener_busqueda(self):
        consulta = self.__ui.linea_buscador.text()
        return BusquedaDTO(consulta)

    def actualizar_canciones(self, canciones: list = None):
        self.__limpiar_lista()
        if canciones:
            for cancion in canciones:
                item = QtWidgets.QListWidgetItem(
                    f"{cancion.nombre}\nAlbum: {cancion.album}\nArtista: {cancion.artista}\n"
                )
                item.setData(1, cancion.id)
                self.__ui.lista.addItem(item)

    def actualizar_dispositivos(self, dispositivos: list):
        self.__ui.combo_dispositivo.clear()
        for dispositivo in dispositivos:
            self.__ui.combo_dispositivo.addItem(dispositivo.nombre, dispositivo)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ventana = VistaPrincipal()
    ventana.show()

    def on_buscar_cancion():
        print(ventana.buscar_cancion())

    ventana.buscar.connect(on_buscar_cancion)

    app.exec()
