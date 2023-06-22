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

import pickle
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
        self.resize(self.gui.screen_w*1//4, self.gui.screen_h*4//5)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        maingrid=QGridLayout()

        #adds the image plot
        self.figurewidget=TrackFig(self.gui)
        #adds the image plot to the main grid
        maingrid.addWidget(self.figurewidget,2,0)

        #creates the grid layouts
        toprow=QGridLayout()
        bottomrow=QGridLayout()
        #adds a next plot button
        self.nextplot = QPushButton('Next Plot', self)
        self.nextplot.clicked.connect(self.gotonextplot)
        toprow.addWidget(self.nextplot,0,0)


        #adds a previous plot button
        self.prevplot = QPushButton('Previous Plot', self)
        self.prevplot.clicked.connect(self.gotoprevplot)
        toprow.addWidget(self.prevplot,0,1)

        #adds a frame display icon and label
        self.framelabel = QLabel("Frame: ",self)
        self.framelabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        toprow.addWidget(self.framelabel,0,2)

        #adds a box that both shows and edits the current frame
        self.frameshow = QLineEdit(self)
        toprow.addWidget(self.frameshow,0,3)
        self.frameshow.setText(str(0))
        self.frameshow.editingFinished.connect(self.updateframe)

        #sets the ratio of the items in the top row
        toprow.setColumnStretch(0, 2)
        toprow.setColumnStretch(1, 2)

        #adds buttons that affect the comparisons
        self.nextcomp = QPushButton('Next comparison', self)
        self.nextcomp.clicked.connect(self.gotonextcomp)
        bottomrow.addWidget(self.nextcomp,0,0)
        self.correct = QPushButton('Correct', self)
        self.correct.clicked.connect(self.setcorrect)
        bottomrow.addWidget(self.correct,0,1)
        self.wrong = QPushButton('Wrong', self)
        self.wrong.clicked.connect(self.setwrong)
        bottomrow.addWidget(self.wrong,0,2)

        #adds layouts to main grid
        maingrid.addLayout(bottomrow,1,0)
        maingrid.addLayout(toprow,0,0)

        #makes the rows adjacent
        bottomrow.setAlignment(Qt.AlignTop)

        #adds the main grid to the central widget
        self.centralWidget.setLayout(maingrid)

    def gotonextcomp(self):
        self.gui.starttime=300
        self.gui.frame=self.gui.starttime
        self.gui.respond("update_data")
        self.gui.graphstodraw=[11,323,335]

    def setcorrect(self):
        print("correct")

    def setwrong(self):
        print("wrong")
    def closeEvent(self, event): #correctly closes the gui
        self.gui.respond("close")

    def updateframe(self):
        if self.frameshow.text().isdigit():
            self.gui.frame=int(self.frameshow.text())
            self.gui.respond("update_data")


    def gotonextplot(self):
        self.gui.frame+=1
        self.gui.respond("update_data")

    def gotoprevplot(self):
        if self.gui.frame >= 1:
            self.gui.frame-=1
        self.gui.respond("update_data")

class GUI():
    def __init__(self,imgpath,precombinedwormtracks):
        self.close=False


        #gets all of the track data out
        with open(precombinedwormtracks, 'rb') as handle:
            inputs = pickle.load(handle)
        self.combos=inputs["combos"]
        self.tracksdf=inputs["tracksdf"]
        self.startend=inputs["startend"]

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
        self.graphstodraw=[]

    def start(self):
        self.app.exec() #starts the app

    def respond(self,key,val=None):
        if key=="close": #closes the application
            self.close=True
        elif key=="update_data": #key to update the data in on the screen
            if self.close:
                return
            #normalizes data
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

        self.plots={}
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
        self.image.setImage(img[:,:],autoLevels=False,levels=[0,255])
        colors=['r','g','b','p','o','y']
        iter=0
        for key in self.plots.keys():
            self.plots[key].clear()
        for track in self.gui.graphstodraw:
            xs=[]
            ys=[]
            for time in range(self.gui.starttime,self.gui.frame):
                x=self.gui.tracksdf[(self.gui.tracksdf.ID==track)&(self.gui.tracksdf.time==time)].x.values
                y=self.gui.tracksdf[(self.gui.tracksdf.ID==track)&(self.gui.tracksdf.time==time)].y.values
                len(x) > 0 and xs.append(x[0])
                len(y) > 0 and ys.append(y[0])
            self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=3))
            #print("xs: "+str(np.round(xs,2)))
            #print("ys: "+str(np.round(ys,2)))
            self.addItem(self.plots[track])
            iter+=1

if __name__ == '__main__':
    pg.setConfigOption('background', 'w')
    parser = argparse.ArgumentParser(description='Launch Annotation GUI')
    parser.add_argument('imgpath', help='image path')
    parser.add_argument('precombinedwormtracks', help='track for data from pre-ran algorithm')

    args=parser.parse_args()

    imgpath=args.imgpath
    precombinedwormtracks=args.precombinedwormtracks
    gui=GUI(imgpath,precombinedwormtracks)
    gui.start()
    print("GUI closed succesfully")
