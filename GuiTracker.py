from PyQt4 import QtGui, QtCore, uic
import os, sys
import numpy as np
from camera import MyGui

class GUI(QtGui.QMainWindow):
    def __init__(self, **kwargs):
        super(GUI, self).__init__()
        uic.loadUi('GUI.ui', self)
        self.video = MyGui(**{"a":"b"})
        self.hbox1.addWidget(self.video)
        self.icon_lbl.setPixmap(QtGui.QPixmap("logo.png").scaled(64, 64, QtCore.Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = GUI()

    window.show()
    sys.exit(app.exec_())