import random
from src.widgets import *
from src.window import Window
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
    def __init__(self,imgpath,precombinedwormtracks,rotate,sumarraypath):
        self.close=False
        self.rotate=rotate
        #gets all of the track data out
        with open(precombinedwormtracks, 'rb') as handle:
            inputs = pickle.load(handle)
        self.ends=inputs["ends"]
        self.tracksdf=inputs["tracksdf"]
        self.startend=inputs["startend"]

        self.trackstemp=self.tracksdf.copy()
        self.endstemp=self.ends

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
        self.enditer=-1#iterator that shows which track end the user is on
        self.graphstodraw=[]

        #dictionary that tracks track combinations
        self.switches={}

        #dictionary that tracks number of track combinations with the original ID per combination
        self.switchpercombo={}
        #dictionary that tracks the last switch for each track combination
        self.lastswitch={}
        self.win.gotonextcomp()

    def start(self):
        self.app.exec() #starts the app

    def respond(self,key,val=None):
        if key=="close": #closes the application
            self.tracksdf.to_csv("../outputtracks.csv")
            self.close=True
        elif key=="get_tracks":
            if self.close:
                return
            self.win.figurewidget.get_tracks()
        elif key=="update_comp":
            if self.close:
                return
            self.win.tracksdist.setText(str(150))
            self.win.trackstime.setText(str(70))
            self.win.framesbefore.setText(str(5))
            self.win.figurewidget.update_comp()
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
