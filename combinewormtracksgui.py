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

        #clears the manual output file
        self.writefile = open("manualoutput.txt", "w")
        self.writefile.write("")
        self.writefile.close()
        self.writefile = open("manualoutput.txt", "a")


        #resizes the gui screen
        self.resize(int(self.gui.screen_w*0.3), self.gui.screen_h*4//5)

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
        rightbartop=QVBoxLayout()
        rightbarmiddle=QVBoxLayout()
        rightbar=QVBoxLayout()


        #Labels and explanations for comparisons
        self.complabel = QLabel("Track evaluation explanation:",self)
        rightbartop.addWidget(self.complabel)
        self.compind = QLabel("",self)
        self.compind.setWordWrap(True)
        rightbarmiddle.addWidget(self.compind)
        self.compexp = QLabel("",self)
        rightbarmiddle.addWidget(self.compexp)

        self.comboboxes=[]
        for i in range(5):
            self.comboboxes.append(QComboBox())

        rightbar.setSpacing(5)
        self.text1 = QLabel("Option 1: Track",self)
        rightbar.addWidget(self.text1)
        self.comboboxes[0].setFixedWidth(100)
        rightbar.addWidget(self.comboboxes[0])
        self.text2 = QLabel("is the same worm as track",self)
        rightbar.addWidget(self.text2)
        self.comboboxes[1].setFixedWidth(100)
        rightbar.addWidget(self.comboboxes[1])
        self.addchange1 = QPushButton("Add change",self)
        self.addchange1.setFixedWidth(100)
        self.addchange1.clicked.connect(self.addchange1func)
        rightbar.addWidget(self.addchange1)


        self.text3 = QLabel("Option 2: Track",self)
        rightbar.addWidget(self.text3)
        self.comboboxes[2].setFixedWidth(100)
        rightbar.addWidget(self.comboboxes[2])
        self.text4 = QLabel("took the place of track",self)
        rightbar.addWidget(self.text4)
        self.comboboxes[3].setFixedWidth(100)
        rightbar.addWidget(self.comboboxes[3])
        self.text5 = QLabel("at time",self)
        rightbar.addWidget(self.text5)
        self.timeedit = QLineEdit(self)
        self.timeedit.setFixedWidth(100)
        rightbar.addWidget(self.timeedit)
        self.addchange2 = QPushButton("Add change",self)
        self.addchange2.setFixedWidth(100)
        self.addchange2.clicked.connect(self.addchange2func)
        rightbar.addWidget(self.addchange2)


        self.text6 = QLabel("Option 3: Delete",self)
        rightbar.addWidget(self.text6)
        self.comboboxes[4].setFixedWidth(100)
        rightbar.addWidget(self.comboboxes[4])
        self.addchange3 = QPushButton("Add change",self)
        self.addchange3.setFixedWidth(100)
        self.addchange3.clicked.connect(self.addchange3func)
        rightbar.addWidget(self.addchange3)
        verticalSpacer = QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        rightbar.addItem(verticalSpacer)

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

        #sets the ratio of the items in the top and bottom row
        toprow.setColumnStretch(0, 2)
        toprow.setColumnStretch(1, 2)
        bottomrow.setColumnStretch(0, 2)
        bottomrow.setColumnStretch(1, 2)

        #adds buttons that affect the comparisons
        self.nextcomp = QPushButton('Next comparison', self)
        self.nextcomp.clicked.connect(self.gotonextcomp)
        bottomrow.addWidget(self.nextcomp,0,0)
        self.prevcomp = QPushButton('Previous comparison', self)
        self.prevcomp.clicked.connect(self.gotoprevcomp)
        bottomrow.addWidget(self.prevcomp,0,1)


        #adds a comparison index display icon and label
        self.complabel = QLabel("Comparison: ",self)
        self.complabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        bottomrow.addWidget(self.complabel,0,2)

        #adds a box that both shows and edits the current comparison index
        self.compshow = QLineEdit(self)
        bottomrow.addWidget(self.compshow,0,3)
        self.compshow.setText("NaN")
        self.compshow.editingFinished.connect(self.updatecomp)

        #adds layouts to main grid
        maingrid.addLayout(bottomrow,1,0)
        maingrid.addLayout(toprow,0,0)
        maingrid.addLayout(rightbartop,0,1)
        maingrid.addLayout(rightbarmiddle,1,1)
        maingrid.addLayout(rightbar,2,1)

        #makes the rows adjacent
        bottomrow.setAlignment(Qt.AlignTop)

        #adds the main grid to the central widget
        self.centralWidget.setLayout(maingrid)


    def addchange1func(self):
        ID1=int(self.comboboxes[0].currentText())
        ID2=int(self.comboboxes[1].currentText())
        self.gui.tracksdf.loc[self.gui.tracksdf.ID==ID2,["ID"]]=ID1
        self.gui.tracksdf=self.gui.tracksdf[np.isin(self.gui.tracksdf.ID,[ID2],invert=True)]
        self.writefile.write("Combined tracks "+str(ID1)+" and "+str(ID2)+"\n")
        self.gui.respond("update_data")

    def addchange2func(self):
        ID1=int(self.comboboxes[2].currentText())
        ID2=int(self.comboboxes[3].currentText())
        time=int(self.timeedit.text())
        self.gui.tracksdf.loc[(self.gui.tracksdf.ID==ID1)&(self.gui.tracksdf.time>=time),["ID"]]=ID2
        self.writefile.write("Switched track "+str(ID1)+" to "+str(ID2)+" at time "+str(time)+"\n")
        self.gui.respond("update_data")


    def addchange3func(self):
        ID1=int(self.comboboxes[4].currentText())
        self.gui.tracksdf=self.gui.tracksdf[(self.gui.tracksdf.ID!=ID1)]
        self.writefile.write("Deleted ID "+str(ID1)+"\n")
        self.gui.respond("update_data")


    def gotonextcomp(self):
        self.gui.enditer+=1
        self.compshow.setText(str(self.gui.enditer+1))
        self.gui.respond("update_comp")

    def updatecomp(self):
        if self.compshow.text().isdigit():
            self.gui.enditer=int(self.compshow.text())
            self.gui.respond("update_comp")

    def gotoprevcomp(self):
        if self.gui.enditer >= 1:
            self.gui.enditer-=1
        self.compshow.setText(str(self.gui.enditer+1))
        self.gui.respond("update_comp")

    def closeEvent(self, event): #correctly closes the gui
        self.gui.respond("close")

    #updates the frame and called update_data
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
        self.ends=inputs["ends"]
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
        self.enditer=-1#iterator that shows which track end the user is on
        self.graphstodraw=[]

    def start(self):
        self.app.exec() #starts the app

    def respond(self,key,val=None):
        if key=="close": #closes the application
            self.close=True
        elif key=="update_comp":
            if self.close:
                return
            self.win.figurewidget.update_comp()
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
        #creates a legend
        self.legend=self.addLegend()

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
        colors=np.tile(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf'],3)
        iter=0
        for key in self.plots.keys():
            self.plots[key].clear()
        self.legend.clear()
        for track in self.gui.graphstodraw:
            xs=[]
            ys=[]
            for time in range(self.gui.starttime,self.gui.frame):
                x=self.gui.tracksdf[(self.gui.tracksdf.ID==track)&(self.gui.tracksdf.time==time)].x.values
                y=self.gui.tracksdf[(self.gui.tracksdf.ID==track)&(self.gui.tracksdf.time==time)].y.values
                len(x) > 0 and xs.append(x[0])
                len(y) > 0 and ys.append(y[0])
            if iter <= 7:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.SolidLine))
            elif iter <= 14:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.DotLine))
            elif iter <= 21:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.DashLine))
            #print("xs: "+str(np.round(xs,2)))
            #print("ys: "+str(np.round(ys,2)))
            self.addItem(self.plots[track])
            self.legend.addItem(self.plots[track],str(int(track)))
            iter+=1

    def update_comp(self):
        self.gui.starttime=self.gui.startend.loc[self.gui.ends[self.gui.enditer]].end-5
        self.gui.frame=self.gui.starttime+10
        self.gui.graphstodraw=[]
        #gets all the data about when/where the worm track ends
        if self.gui.ends[self.gui.enditer] not in self.gui.tracksdf.ID.values:
            self.gui.win.compind.setText(f"<p style='background-color:white'>Track already removed or merged, go to next comparison.</p>")
            self.gui.win.compexp.setText(f"<p style='background-color:white'></p>")
            for i in range(5):
                self.gui.win.comboboxes[i].clear()
            self.gui.respond("update_data")
        else:
            end,endtime,endx,endy=list(self.gui.tracksdf[(self.gui.tracksdf.ID==self.gui.ends[self.gui.enditer])\
                                                        & (self.gui.tracksdf.time==self.gui.startend.loc[self.gui.ends[self.gui.enditer]].end)].values)[0]
            compindtext="Comparison "+str(int(self.gui.enditer+1))+" out of "+str(int(len(self.gui.ends)))
            self.gui.win.compind.setText(f"<p style='background-color:white'>{compindtext}</p>")
            compexptext="Track "+str(int(end))+" ended at time t="+str(int(endtime))
            self.gui.win.compexp.setText(f"<p style='background-color:white'>{compexptext}</p>")
            timedist=70
            spacedist=200
            #gets all the tagged worms in the area
            for ID in np.unique(self.gui.tracksdf.ID.values):
                if len(self.gui.tracksdf[(self.gui.tracksdf.ID==ID)&(np.abs(endtime-self.gui.tracksdf.time)<timedist)&(np.abs(self.gui.tracksdf.x-endx)<spacedist)&(np.abs(self.gui.tracksdf.y-endy)<spacedist)]):
                    self.gui.graphstodraw.append(int(ID))
            for i in range(5):
                self.gui.win.comboboxes[i].clear()
                self.gui.win.comboboxes[i].addItems(list(map(str, np.sort(self.gui.graphstodraw))))
            self.gui.respond("update_data")



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
