from PyQt5 import QtWidgets

from .controlador import Controlador


app = QtWidgets.QApplication([])
controlador = Controlador()
controlador.show_vista()
app.exec()
