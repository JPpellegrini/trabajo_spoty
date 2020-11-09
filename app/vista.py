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


@dataclass
class DispositivoDTO:
    id: str
    nombre: str


@dataclass
class ReproduccionDTO:
    id_dispositivo: str
    id_cancion: str


class VistaPrincipal(QtWidgets.QMainWindow):

    buscar = QtCore.pyqtSignal()
    anterior = QtCore.pyqtSignal()
    play = QtCore.pyqtSignal()
    pausa = QtCore.pyqtSignal()
    reproducir = QtCore.pyqtSignal(object)
    siguiente = QtCore.pyqtSignal()
    actualizar = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__ui = Ui_reproductor()
        self.__setupUi()

    def __setupUi(self):
        self.__ui.setupUi(self)

        self.__ui.imagen_principal.setPixmap(
            QtGui.QPixmap("app/icons/png/imagen_spoty.png")
        )

        self.__ui.icono_lupa = QtGui.QIcon()
        self.__ui.icono_lupa.addPixmap(
            QtGui.QPixmap("app/icons/png/buscar.png"),
        )
        self.__ui.boton_buscar.setIcon(self.__ui.icono_lupa)

        self.__ui.icono_anterior = QtGui.QIcon()
        self.__ui.icono_anterior.addPixmap(
            QtGui.QPixmap("app/icons/png/anterior.png"),
        )
        self.__ui.boton_anterior.setIcon(self.__ui.icono_anterior)

        self.__ui.icono_pausa = QtGui.QIcon()
        self.__ui.icono_pausa.addPixmap(
            QtGui.QPixmap("app/icons/png/pausa.png"),
        )
        self.__ui.boton_pausa.setIcon(self.__ui.icono_pausa)

        self.__ui.icono_play = QtGui.QIcon()
        self.__ui.icono_play.addPixmap(
            QtGui.QPixmap("app/icons/png/play.png"),
        )
        self.__ui.boton_play.setIcon(self.__ui.icono_play)

        self.__ui.icono_siguiente = QtGui.QIcon()
        self.__ui.icono_siguiente.addPixmap(
            QtGui.QPixmap("app/icons/png/siguiente.png"),
        )
        self.__ui.boton_siguiente.setIcon(self.__ui.icono_siguiente)

        self.__ui.icono_actualizar = QtGui.QIcon()
        self.__ui.icono_actualizar.addPixmap(
            QtGui.QPixmap("app/icons/png/actualizar.png"),
        )
        self.__ui.boton_actualizar.setIcon(self.__ui.icono_actualizar)

    def on_clicked_buscar(self):
        self.buscar.emit()

    def on_clicked_anterior(self):
        self.anterior.emit()

    def on_clicked_pausa(self):
        self.pausa.emit()

    def on_clicked_reproducir(self):
        id_dispositivo = self.__ui.combo_dispositivo.currentData().id
        id_cancion = self.__ui.lista.currentItem().data(1)
        self.reproducir.emit(ReproduccionDTO(id_dispositivo, id_cancion))

    def on_clicked_siguiente(self):
        self.siguiente.emit()

    def on_clicked_play(self):
        self.play.emit()

    def on_clicked_actualizar(self):
        self.actualizar.emit()

    def __limpiar_lista(self):
        self.__ui.lista.clear()

    def obtener_busqueda(self):
        consulta = self.__ui.linea_buscador.text()
        return BusquedaDTO(consulta)

    def actualizar_canciones(self, canciones: list = None):
        self.__limpiar_lista()
        if canciones:
            for cancion in canciones:
                item = QtWidgets.QListWidgetItem(f"{cancion.nombre}-{cancion.artista}")
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
