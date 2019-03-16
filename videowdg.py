# Standard Python Library
import time
import sys

# 3-rd party Library
from PyQt4 import QtCore, QtGui

# Local modules
from corelib import GraphicsView, videoThread

class MyGui(QtGui.QWidget):
    """GUI related class no need to change"""
    def __init__(self):
        super(MyGui,self).__init__()

        self.source=None
        self.view = GraphicsView(self)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setMargin(0)
        self.vbox.addWidget(self.view)
        self.setLayout(self.vbox)

        """Minimum size of the videowdg [minimal resizeing size]"""
        self.setMinimumWidth(40)
        self.setMinimumHeight(40)

    def stop(self):
        if hasattr(self, 'video'):
            self.video.state = False
            self.video.wait()

    def start(self):
        if self.source is not None:
            self.video = videoThread(self.source)
            self.connect(self.video, QtCore.SIGNAL('newImage(QImage)'), self.setFrame)
            self.video.start()

    def updateCfgs(self, *args):
        self.source = args[0]


    def setFrame(self,frame):
        self.pix = QtGui.QPixmap.fromImage(frame)
        self.view.setPhoto(self.pix)