import random
import numpy as np
np.set_printoptions(suppress=True)
import pandas as pd
import h5py
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from PyQt5.QtGui import QFont
from tqdm import tqdm

from matplotlib import cm

import time
from PyQt5.Qt import Qt
import sys

from PyQt5.QtCore import QTimer
import argparse

class Window(QMainWindow):
    def __init__(self,gui):
        super().__init__()
        self.gui=gui

        #resizes the gui screen
        self.resize(self.gui.screen_w*1//4, self.gui.screen_h*2//3)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        maingrid=QGridLayout()

        #adds the image plot
        self.figurewidget=TrackFig(self.gui)
        #adds the image plot to the main grid
        maingrid.addWidget(self.figurewidget,1,0)

        toprow=QGridLayout()
        #adds a next plot button
        self.nextplot = QPushButton('Next Plot', self)
        self.nextplot.clicked.connect(self.gotonextplot)
        toprow.addWidget(self.nextplot,0,0)

        #adds a frame display icon and label
        self.framelabel = QLabel("Frame: ",self)
        self.framelabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        toprow.addWidget(self.framelabel,0,1)

        self.frameshow = QLineEdit(self)
        toprow.addWidget(self.frameshow,0,2)
        self.frameshow.setText(str(0))
        self.frameshow.editingFinished.connect(self.updateframe)
        toprow.setColumnStretch(0, 5)
        toprow.setColumnStretch(2, 5)

        maingrid.addLayout(toprow,0,0)
        #maingrid.setRowStretch(0,5)
        #adds the main grid to the central widget
        self.centralWidget.setLayout(maingrid)

    def closeEvent(self, event): #correctly closes the gui
        self.gui.respond("close")

    def updateframe(self):
        print("frame in spinbox: "+str(self.frameshow.text()))
        if self.frameshow.text().isdigit():
            print("Spin updated")
            self.gui.frame=int(self.frameshow.text())
            self.gui.respond("update_data")


    def gotonextplot(self):
        self.gui.frame+=1
        self.gui.respond("update_data")

class GUI():
    def __init__(self,imgpath):
        self.close=False
        self.imgdata=h5py.File(imgpath, 'r')#path of image file
        self.sumarray=np.load("sumarray.npy")#path of file that sums up all of the images, useful for normalizing later
        self.app = QApplication(sys.argv)

        #creates screen with screen width and screen height
        screen = self.app.primaryScreen()
        size = screen.size()
        self.screen_w=size.width()
        self.screen_h=size.height()

        self.win = Window(self)
        self.win.show()

        #sets the first frame of the image to zero
        self.frame=0

    def start(self):
        self.app.exec() #starts the app

    def respond(self,key,val=None):
        if key=="close": #closes the application
            self.close=True
        elif key=="update_data": #key to update the data in on the screen
            if self.close:
                return
            #normalizes data
            print("displayed frame: "+str(self.frame))
            self.win.frameshow.setText(str(self.frame))
            img=(self.imgdata[str(self.frame)]['frame'][0].max(2)-self.sumarray/np.max([int(x) for x in list(self.imgdata.keys()) if x.isdigit()]))
            xMin=0
            xMax=1944
            yMin=0
            yMax=1944
            #sets x and y limits
            self.win.figurewidget.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
            #calls the update data program
            self.win.figurewidget.update_data(img)

class TrackFig(pg.PlotWidget):
    def __init__(self,gui):
        self.gui=gui
        super().__init__()

        #creates the image item
        self.image=pg.ImageItem()
        self.addItem(self.image)

        # build lookup table
        lut = np.zeros((256,3), dtype=np.ubyte)
        lut[0:10,:] =255
        lut[10:74,:] = np.stack([np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4))],axis=1)
        lut[74:,:] = 0

        # Apply the colormap
        self.image.setLookupTable(lut)

        self.setAspectLocked()

    def keyPressEvent(self, event): #activated whenever any key is pressed
        key=event.key()
        if key==Qt.Key_Space:
            #increments frame
            self.gui.frame+=1 #increments the frame
            self.gui.win.frameshow.setValue(self.gui.frame)
            #calls update data key when space is clicked
            self.gui.respond("update_data")

    def update_data(self,img):
        #have to transpose image for it to display correctly
        self.image.setImage(img[:,:].T,autoLevels=False,levels=[0,255])

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    parser = argparse.ArgumentParser(description='Launch Annotation GUI')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('precombinedwormtracks', help='track for data from pre-ran algorithm')

    args=parser.parse_args()

    imgpath=args.imgpath
    precombinedwormtracks=args.precombinedwormtracks
    gui=GUI(imgpath)
    gui.start()
    print("GUI closed succesfully")
