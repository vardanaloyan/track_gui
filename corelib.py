# Standard Python Library
import cv2
import sys
import time
import numpy as np

# 3-rd party Library
from PyQt4 import QtCore,QtGui

# Local modules
import vehicles

class videoThread(QtCore.QThread):

    def __init__(self,address):
        """Constructor of class no need to change"""
        super(videoThread,self).__init__()
        self.source = address
        self.state = True


    def initParameters(self):
        """Initial Parameters"""
        self.cap = cv2.VideoCapture(self.source)
        self.w = self.cap.get(3)
        self.h = self.cap.get(4)

        self.cnt_up=0
        self.cnt_down=0

        self.frameArea=self.h*self.w
        self.areaTH=self.frameArea/400

        #Lines
        self.line_up=int(2*(self.h/5))
        self.line_down=int(3*(self.h/5))

        self.up_limit=int(1*(self.h/5))
        self.down_limit=int(4*(self.h/5))

        # print("Red line y:",str(self.line_down))
        # print("Blue line y:",str(self.line_up))
        self.line_down_color=(255,0,0)
        self.line_up_color=(255,0,255)
        self.pt1 =  [0, self.line_down]
        self.pt2 =  [self.w, self.line_down]
        self.pts_L1 = np.array([self.pt1,self.pt2], np.int32)
        self.pts_L1 = self.pts_L1.reshape((-1,1,2))
        self.pt3 =  [0, self.line_up]
        self.pt4 =  [self.w, self.line_up]
        self.pts_L2 = np.array([self.pt3,self.pt4], np.int32)
        self.pts_L2 = self.pts_L2.reshape((-1,1,2))

        self.pt5 =  [0, self.up_limit]
        self.pt6 =  [self.w, self.up_limit]
        self.pts_L3 = np.array([self.pt5,self.pt6], np.int32)
        self.pts_L3 = self.pts_L3.reshape((-1,1,2))
        self.pt7 =  [0, self.down_limit]
        self.pt8 =  [self.w, self.down_limit]
        self.pts_L4 = np.array([self.pt7,self.pt8], np.int32)
        self.pts_L4 = self.pts_L4.reshape((-1,1,2))

        #Background Subtractor
        self.fgbg=cv2.createBackgroundSubtractorMOG2(detectShadows=True)

        #Kernals
        self.kernalOp = np.ones((3,3),np.uint8)
        self.kernalOp2 = np.ones((5,5),np.uint8)
        self.kernalCl = np.ones((11,11),np.uint)


        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cars = []
        self.max_p_age = 5
        self.pid = 1


        _,__ = self.cap.read()
        try:
            hh, ww = __.shape[:2]
            # print '> Resolution: %sx%s' % (ww, hh)
            return True
        except Exception as ex:
            print ex
            return False

    def run(self):
        """ core function no need to change"""
        if self.initParameters() == False:
            return

        while self.cap.isOpened() and self.state==True:
            self.ret ,self.frame = self.cap.read()
            hh, ww = self.frame.shape[:2]
            self.Processing(self.frame)
            image = QtGui.QImage(self.frame.tostring(),ww,hh,QtGui.QImage.Format_RGB888).rgbSwapped()
            self.emit(QtCore.SIGNAL('newImage(QImage)'), image)

    def Processing(self, frame):
        """Image Processing part, all algorithmic calculation must done in this function"""
        for i in self.cars:
            i.age_one()

        fgmask=self.fgbg.apply(frame)
        fgmask2=self.fgbg.apply(frame)

        if self.ret==True:

            #Binarization
            self.ret,imBin=cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
            self.ret,imBin2=cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
            #OPening i.e First Erode the dilate
            mask=cv2.morphologyEx(imBin,cv2.MORPH_OPEN,self.kernalOp)
            mask2=cv2.morphologyEx(imBin2,cv2.MORPH_CLOSE,self.kernalOp)

            #Closing i.e First Dilate then Erode
            mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,self.kernalCl)
            mask2=cv2.morphologyEx(mask2,cv2.MORPH_CLOSE,self.kernalCl)


            #Find Contours
            _, countours0,hierarchy=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            for cnt in countours0:
                area=cv2.contourArea(cnt)
                # print(area)
                if area>self.areaTH:
                    ####Tracking######
                    m=cv2.moments(cnt)
                    cx=int(m['m10']/m['m00'])
                    cy=int(m['m01']/m['m00'])
                    x,y,w,h=cv2.boundingRect(cnt)

                    new=True
                    if cy in range(self.up_limit, self.down_limit):
                        for i in self.cars:
                            if abs(x - i.getX()) <= self.w and abs(y - i.getY()) <= self.h:
                                new = False
                                i.updateCoords(cx, cy)

                                if i.going_UP(self.line_down, self.line_up)==True:
                                    self.cnt_up+=1
                                    # print("ID:",i.getId(),'crossed going up at', time.strftime("%c"))
                                elif i.going_DOWN(self.line_down, self.line_up)==True:
                                    self.cnt_down+=1
                                    # print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                                break
                            if i.getState()=='1':
                                if i.getDir()=='down'and i.getY()>self.down_limit:
                                    i.setDone()
                                elif i.getDir()=='up'and i.getY()<self.up_limit:
                                    i.setDone()
                            if i.timedOut():
                                index=self.cars.index(i)
                                self.cars.pop(index)
                                del i

                        if new==True: #If nothing is detected,create new
                            p=vehicles.Car(self.pid,cx,cy,self.max_p_age)
                            self.cars.append(p)
                            self.pid+=1

                    cv2.circle(frame,(cx,cy),5,(0,0,255),-1)
                    img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            for i in self.cars:
                cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), self.font, 0.3, i.getRGB(), 1, cv2.LINE_AA)

            str_up='UP: '+str(self.cnt_up)
            str_down='DOWN: '+str(self.cnt_down)
            frame=cv2.polylines(frame,[self.pts_L1],False,self.line_down_color,thickness=2)
            frame=cv2.polylines(frame,[self.pts_L2],False,self.line_up_color,thickness=2)
            frame=cv2.polylines(frame,[self.pts_L3],False,(255,255,255),thickness=1)
            frame=cv2.polylines(frame,[self.pts_L4],False,(255,255,255),thickness=1)
            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_up, (10, 40), self.font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, str_down, (10, 90), self.font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

  

class GraphicsView(QtGui.QGraphicsView):
    """ core class no need to change"""
    def __init__(self, *args, **kwargs):
        QtGui.QGraphicsView.__init__(self, *args, **kwargs)
        self._scene = QtGui.QGraphicsScene(self)
        self._photo = QtGui.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtGui.QFrame.NoFrame)

    def fitInView(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
