# Standard Python Library
import os, sys
import numpy as np

# 3-rd party Library
from PyQt4 import QtGui, QtCore, uic

# Local modules
from videowdg import MyGui

class GUI(QtGui.QMainWindow):
    """Main window class"""
    def __init__(self, **kwargs):
        super(GUI, self).__init__()
        uic.loadUi('GUI.ui', self)

        self.logoPath = "logo.png"
        self.logoSize = (32, 32)
        """
            < self.videoFolderPath > is the absolute path of the folder containing videos
            You can edit this this variable and set your absolute path
        """
        self.videoFolderPath = os.path.join(os.getcwd(), "Video")

        self.video = MyGui()
        self.model = QtGui.QFileSystemModel()
        self.files_list = QtGui.QTreeView()
        self.files_list.setModel(self.model)
        self.files_list.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.files_list.setAnimated(True)
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.video)
        self.splitter.addWidget(self.files_list)
        self.splitter.setStretchFactor(0, 6)
        self.hbox1.addWidget(self.splitter)

        self.filePath = None
        self.files_list.activated.connect(self.click_Play)
        self.files_list.clicked.connect(self.return_path)

        self.icon_lbl.setPixmap(QtGui.QPixmap(self.logoPath).scaled(self.logoSize[0], self.logoSize[1], QtCore.Qt.KeepAspectRatio))
        self.setFilesPath(self.videoFolderPath, self.videoFolderPath)
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.nextvideo_btn.clicked.connect(self.next)

    def start(self):
        self.stop()
        if self.filePath:
            self.video.updateCfgs(self.filePath)
            self.video.start()

    def stop(self):
        self.video.stop()

    def setFilesPath(self, rootpath, rootindex):
        self.model.setRootPath(rootpath)
        self.files_list.setRootIndex(self.model.index(rootindex))

    def return_path(self, selected):
        self.currentRow = selected.row()
        self.currentCol = selected.column()
        self.selectedParent = selected.parent()
        self.filePath= str(self.files_list.model().filePath(selected))
        self.isdir = self.files_list.model().isDir(selected)
        return self.filePath, self.isdir

    def next(self):
        indexItem = self.model.index(self.currentRow + 1, self.currentCol, self.selectedParent)
        self.files_list.setCurrentIndex(self.model.index(self.currentRow + 1, 0, self.files_list.rootIndex()))
        self.filePath= str(self.files_list.model().filePath(indexItem))
        self.currentRow = indexItem.row()
        self.currentCol = indexItem.column()
        self.selectedParent = indexItem.parent()
        if self.currentRow == -1:
            self.stop()
            self.video.view.setPhoto(None)
            return
        self.start()

    def click_Play(self, text):
        self.text = text
        self.filePath = str(self.files_list.model().filePath(text))
        self.video.updateCfgs(self.filePath)
        self.start()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())