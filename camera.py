#!/usr/bin/env python

import time
import sys

from PyQt4 import QtCore, QtGui
from umodule import GraphicsView, videoThread

class MyGui(QtGui.QWidget):
    def __init__(self,*argv,**kwargs):
        super(MyGui,self).__init__()

        # self.ip=argv[0]
        # self.path=argv[1]
        self.path="/home/programmer/Videos"
        self.ip = "video.mp4"
        self.initStyleParams(kwargs)
        self.video = videoThread(self.ip,self.path)

        self.recc = False
        self.view = GraphicsView(self)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setMargin(0)
        self.vbox.addWidget(self.view)

        self.setLayout(self.vbox)
        self.connect(self.video,QtCore.SIGNAL('newImage(QImage)'),self.setFrame)

        self.video.start()
        # self.video.frameSignal.connect(self.Record)

        # self.video.errorSignal.connect(lambda x,y,z: self.hide_overlay(x,y,z))



    def updateCfgs(self, *args):
        self.ip = args[0]



    def restart(self):
        # print 'restart'
        if hasattr(self, "video"):
            self.video.state=False

        self.video = videoThread(self.ip,self.path)
        self.video.start()
        self.video.frameSignal.connect(self.Record)

        self.connect(self.video,QtCore.SIGNAL('newImage(QImage)'),self.setFrame)
        self.video.errorSignal.connect(lambda x,y,z: self.hide_overlay(x,y,z))
  
    def STOP(self):
        # print 'STOP'
        self.video.state=False
        del self.video


    def setFrame(self,frame):
        self.pix = QtGui.QPixmap.fromImage(frame)
        self.view.setPhoto(self.pix)

    def keyPressEvent(self, ev):
        key = ev.key()

        if key== 43 or key == 61:
            self.view.zoomIn()

        if key == 45:
            self.view.zoomOut()

        if key==16777216:
            if self.isFullScreen():
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setWindowFlags(QtCore.Qt.Widget)
                self.showNormal()
                self.setFocus()


        if key==70:
            if not self.isFullScreen():
                self.setWindowFlags(QtCore.Qt.Window)
                self.setWindowState(QtCore.Qt.WindowFullScreen)
                self.show()
                self.setFocus()

            else:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setWindowFlags(QtCore.Qt.Widget)
                self.showNormal()
                self.setFocus()

    def save(self,NAME,text='Default'):

    #    p = QPixmap.grabWindow(self.winId())
    #    p.save('grabed', 'jpg')
        if not hasattr(self, 'pix'):
            return

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        painter = QtGui.QPainter (self.pix)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(18, 173, 42))
        painter.drawText( QtCore.QRectF(5, 5, 400, 400),
              QtCore.Qt.AlignLeft, 
              str(text))
        painter.end()
        self.pix.save(self.path+'/PHOTO/'+str(NAME)+'.PNG')
        # self.export(NAME,text)

    def initStyleParams(self,kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    window = MyGui()
    window.show()
    sys.exit(app.exec_())
