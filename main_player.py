# -*- coding: utf-8 -*-

import sys, os, getpass
from PyQt4 import QtCore, QtGui, uic
from PyQt4.phonon import Phonon
from source.main.OSdialog import FileDialog
import threading
import time
import datetime
import subprocess
from source.main.photoview import PhotoViewer
import multiprocessing
# from source.main.umodule import GraphicsView



class Media(QtGui.QWidget):

    def __init__(self, **kwargs):
        QtGui.QWidget.__init__(self)
        self.box = QtGui.QVBoxLayout()
        self.box.setMargin(0)
        self.setLayout(self.box)
        self.initStyleParams(kwargs)
        self.setStyleSheet('background-color: {};'.format(self.button_color))

    def initStyleParams(self,kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)
            
class Tree(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.box = QtGui.QVBoxLayout()
        self.setLayout(self.box)

class MyWindow(QtGui.QMainWindow):
    def __init__(self, **kwargs):
        super(MyWindow, self).__init__()
        if getattr(sys, 'frozen',False):
            uic.loadUi('Data/player/player.ui', self)
        else:
            uic.loadUi('source/player/player.ui', self)
            # uic.loadUi('player.ui', self)
        self.setStyleSheet("background-color: rgb(166,168,152)")
        self.initStyleParams(kwargs)
        self.Tree = Tree()
        self.Media = Media(**kwargs)
        self.pause_cond = threading.Condition(threading.Lock())
        self.videoWdt = Phonon.VideoWidget()
        self.image_view = PhotoViewer(self)
        self.files_list.setFocus()
        # self.image_view = GraphicsView()
        # self.image_view.useZoomMode()
        self.image_view.hide()
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(20)
        self.splitter.setStyleSheet('QSplitter::handle{background-color: rgb(166,168,152); margin:0; image:url("icons/split.png")}')
        self.splitter.setStyleSheet('QSplittere{background-color: red; margin-left:0 !important; image:url("icons/split.png")}')
        self.Media.box.addWidget(self.videoWdt)
        self.Media.box.addWidget(self.image_view)
        #self.Media.box.addWidget(self.videoWdt)
        #self.Media.box.addWidget(self.image_view)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(u"Տեսադարան")
        self.layout.addWidget(self.splitter)
        self.Tree.box.addWidget(self.files_list)
        self.Tree.box.addWidget(self.send)
        self.splitter.addWidget(self.Tree)
        self.splitter.addWidget(self.Media)
        # self.layout.addWidget(self.videoWdt)
        # self.layout.addWidget(self.image_view)
        self.Mobj = Phonon.MediaObject(self)
        self.Mobj.setTickInterval(1000)
        self.slider = Phonon.SeekSlider(self.Mobj)
        self.model = QtGui.QFileSystemModel()
        self.files_list.setModel(self.model)
        self.files_list.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.files_list.setAnimated(True)
        self.main_horizontal.addWidget(self.slider)
        self.play.clicked.connect(self.Play_pause)
        self.stop.clicked.connect(self.Stop)
        self.playing = False
        self.videoWdt.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        if getattr(sys, 'frozen',False):
            self.full.setIcon(QtGui.QIcon('Data/player/icons/full-screen-arrows.png'))
            self.play.setIcon(QtGui.QIcon('Data/player/icons/play.png'))
            self.stop.setIcon(QtGui.QIcon('Data/player/icons/stop.png'))
        else:
            self.full.setIcon(QtGui.QIcon('source/player/icons/full-screen-arrows.png'))
            self.play.setIcon(QtGui.QIcon('source/player/icons/play.png'))
            self.stop.setIcon(QtGui.QIcon('source/player/icons/stop.png'))



        self.full.clicked.connect(self.full_screen)
        self.shortcutFullS = QtGui.QShortcut(self)
        self.shortcutFullS.setKey(QtGui.QKeySequence('F'))
        self.shortcutFullS.setContext(QtCore.Qt.ApplicationShortcut)
        self.shortcutFullS.activated.connect(self.full_screen)
        self.shortcutFull = QtGui.QShortcut(self)
        self.shortcutFull.setKey(QtGui.QKeySequence('Esc'))
        self.shortcutFull.setContext(QtCore.Qt.ApplicationShortcut)
        self.shortcutFull.activated.connect(self.exit_full)
        # self.snap_btn.clicked.connect(self.snapShot)
        self.snap_btn.hide()
        self.send.clicked.connect(self.sendTo)
        #self.th = multiprocessing.Process(target=self.time_calc)
        self.timer_active = False
        self.th = threading.Thread(target = self.time_calc)
        self.th.daemon = True
        self.th.isAlive_ = False
        self.th.state = True

        self.files_list.activated.connect(self.click_Play)
        self.files_list.clicked.connect(self.return_path)
        self.fileSizeTh = threading.Thread(target = self.getFileSize)


    def setFilesPath(self, rootpath, rootindex):
        self.model.setRootPath(rootpath)
        self.files_list.setRootIndex(self.model.index(rootindex))


    def setSnapshotPath(self, path):
        self.snapPath = path




    def return_path(self, selected):
        self.file_addr=self.files_list.model().filePath(selected)
        self.isdir = self.files_list.model().isDir(selected)
        return self.file_addr, self.isdir




    def click_Play(self, text):
        self.text = text
        self.filePath = self.files_list.model().filePath(text)
        if not str(self.filePath).strip().lower().endswith(('.png', '.jpg', '.jpeg')):
            self.mediaSrc = Phonon.MediaSource(self.filePath)
            self.Mobj.setCurrentSource(self.mediaSrc)
            self.videoWdt.setScaleMode(1)
            self.videoWdt.setAspectRatio(1)
            Phonon.createPath(self.Mobj, self.videoWdt)
            self.image_view.hide()
            self.videoWdt.show()
            self.Mobj.play()
            if not self.th.isAlive_ or not self.th.state:
                if not self.th.state:
                    self.th = threading.Thread(target = self.time_calc)
                    self.th.daemon = True
                    self.th.isAlive_ = False
                    self.th.state = True
                self.th.isAlive_ = True
                self.th.state = True
                self.th.start()


            self.timer_active = True

            if getattr(sys, 'frozen',False):
                self.play.setIcon(QtGui.QIcon('Data/player/icons/pause.png'))
            else:
                self.play.setIcon(QtGui.QIcon('source/player/icons/pause.png'))

            self.playing = True
        else:
            self.Stop()
            self.videoWdt.hide()
            # self.timer_active = False
            #self.lock.acquire()
            #scene = QtGui.QGraphicsScene()

            #scene.addPixmap(QtGui.QPixmap(self.filePath))
            self.image_view.setPhoto(QtGui.QPixmap(self.filePath))
            #self.image_view.setScene(scene)
            self.image_view.show()




    def Play_pause(self):
        self.Mobj.play()
        if self.playing == True:
            if getattr(sys, 'frozen',False):
                self.play.setIcon(QtGui.QIcon('Data/player/icons/play.png'))
            else:
                self.play.setIcon(QtGui.QIcon('source/player/icons/play.png'))

            self.playing = False
            self.timer_active = False
            self.Mobj.pause()
        else:
            if getattr(sys, 'frozen',False):
                self.play.setIcon(QtGui.QIcon('Data/player/icons/pause.png'))
            else:
                self.play.setIcon(QtGui.QIcon('source/player/icons/pause.png'))
            self.playing = True
            self.Mobj.play()
            self.timer_active = True




    def Stop(self):

        self.Mobj.stop()
        self.timer_active = False
        # self.pause_cond.acquire()
        if getattr(sys, 'frozen',False):
            self.play.setIcon(QtGui.QIcon('Data/player/icons/play.png'))
        else:
            self.play.setIcon(QtGui.QIcon('source/player/icons/play.png'))

    def time_calc(self):
        while self.th.state:
            time.sleep(0.5)    
            if self.timer_active:
                if not str(self.filePath).strip().lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.sec_label.setText('{}/{}'.format(datetime.timedelta(seconds=int(self.Mobj.currentTime() * 0.001)), datetime.timedelta(seconds = int(self.Mobj.totalTime() * 0.001))))


    def full_screen_win(self):
        self.showFullScreen()

    def full_screen(self):
        if self.videoWdt.isVisible():
            self.videoWdt.enterFullScreen()
        elif self.Media.isVisible():
            # self.layout.removeWidget(self.Media)
            # self.Media.setParent(None)
            # self.Media.showFullScreen()
            if not self.Media.isFullScreen():
                self.Media.setWindowFlags(QtCore.Qt.Window)
                self.Media.setWindowState(QtCore.Qt.WindowFullScreen)
                self.Media.show()

    def exit_full(self):

        if self.videoWdt.isFullScreen():
            self.videoWdt.exitFullScreen()
        elif self.Media.isFullScreen():
            # self.Media.showNormal()
            # self.layout.addWidget(self.Media)
            self.Media.setWindowFlags(QtCore.Qt.Widget)
            self.Media.setWindowState(QtCore.Qt.WindowNoState)
            self.Media.show()
            # self.Media.setWindowFlags(QtCore.Qt.Widget)
        elif self.isFullScreen():
            self.showNormal()
        else:
            self.close()

    def snapShot(self):
        if os.path.exists(self.snapPath):
            #self.videoWdt.snapshot().save('aaaa.png', 'PNG')
            a=self.videoWdt.snapshot()

            # print '{}/{}.png'.format(self.snapPath, datetime.datetime.now().day)
        else:
            os.mkdir(self.snapPath)
            self.videoWdt.snapshot().save('aaa.png', 'PNG')
            # print '{}/{}.png'.format(self.snapPath, datetime.datetime.now().day)


    def getFileSize(self):
        if self.isdir == False:
            os.popen('cp {} {}'.format(self.file_addr, self.dialogSave))
        else:
            os.popen('cp -r {} {}'.format(self.file_addr, self.dialogSave))

        while 1:
            if os.path.exists(self.dialogSave):
                if os.path.getsize(self.dialogSave) == os.path.getsize(self.file_addr):
                    #self.test.loader_l.setText('Completed')
                    self.send.setText(u'Copy')
                    self.send.setEnabled(True)
                    time.sleep(2)
                    #self.test.close()
                    break
        del(self.fileSizeTh)

    def closeEvent(self, event):
        self.Stop()
        if self.th.state:
            self.th.state = False
            self.th.join()
        # event.accept()



    def sendTo(self):

        if self.file_addr is None:
            pass

        else:
            self.dialog = FileDialog(self)
            self.dialog.selectFile(self.file_addr)
            self.dialog.setSideBar('/')
            self.dialog.setDir('/media')
            self.fileSizeTh = threading.Thread(target = self.getFileSize)
            self.dialogSave = self.dialog.Save()
            if self.dialogSave != None:
                self.send.setText("Copying...")
                self.send.setEnabled(False)
                self.fileSizeTh.start()

    def initStyleParams(self,kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

class AlertDialog(QtGui.QDialog):
    def __init__(self):
        super(AlertDialog, self).__init__()
        if getattr(sys, 'frozen',False):
            uic.loadUi('Data/player/progress.ui', self)
        else:
            uic.loadUi('source/player/progress.ui', self)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    window.setFilesPath('/home/uavlab/Desktop/my_player_finish', '/home/uavlab/Desktop/my_player_finish/VIDEOS')
    window.setSnapshotPath('/home/uavlab/Desktop/my_player_finish/VIDEOS/snapshots/')
    window.show()
    sys.exit(app.exec_())

