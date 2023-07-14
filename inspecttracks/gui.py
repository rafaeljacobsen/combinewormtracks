import random
from widgets import *
from window import Window
import numpy as np
import pandas as pd
import h5py
from PyQt5 import QtCore
import pyqtgraph as pg
import pickle
import sys
import argparse
import time as TIME

class GUI():
    def __init__(self,imgpath,trackspath,rotate,sumarraypath):
        self.close=False
        self.rotate=rotate
        self.tracksdf=pd.read_csv(trackspath)
        if 'Unnamed: 0' in self.tracksdf.columns:
            self.tracksdf=self.tracksdf.drop(columns=['Unnamed: 0'])
        if not "ID" in self.tracksdf.columns:
            self.tracksdf=pd.DataFrame(np.genfromtxt(trackspath), columns = ['ID','time','x','y'])

        #path of image file
        self.imgdata=h5py.File(imgpath, 'r')
        #gets maximum frame
        self.maxframe=np.max([int(x) for x in list(self.imgdata.keys()) if x.isdigit()])
        #path of file that sums up all of the images, useful for normalizing later
        self.sumarray=np.load(sumarraypath)
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
        self.respond("update_data")

    def start(self):
        self.app.exec() #starts the app

    def respond(self,key,val=None):
        if key=="close": #closes the application
            self.close=True
        elif key=="get_tracks":
            if self.close:
                return
            self.win.figurewidget.get_tracks()
        elif key=="update_data": #key to update the data in on the screen
            if self.close:
                return
            #normalizes data
            self.win.frameshow.setText(str(self.frame))
            img=(self.imgdata[str(self.frame)]['frame'][0].max(2)-self.sumarray/self.maxframe)
            if self.rotate:
                img=img.T
                #img=np.rot90(img,3)
            xMin=0
            xMax=np.shape(img)[0]
            yMin=0
            yMax=np.shape(img)[1]
            #sets x and y limits
            self.win.figurewidget.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
            #calls the update data program
            self.win.figurewidget.update_data(img)
