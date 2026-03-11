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
    def __init__(self,imgpath,precombinedwormtracks,rotate,invert,minlevel):
        self.close=False
        self.rotate=rotate
        self.invert=invert
        self.minlevel=minlevel
        #gets all of the track data out
        with open(precombinedwormtracks, 'rb') as handle:
            inputs = pickle.load(handle)
        self.tracksdf=inputs["tracksdf"]
        print(f"Loaded {len(self.tracksdf)} track points from {len(np.unique(self.tracksdf['ID']))} unique tracks")
        if len(self.tracksdf) == 0:
            print("WARNING: No tracking data found in the pickle file!")
            print("This could mean:")
            print("  1. The input CSV/NPY file to precombinewormtracks.py was empty")
            print("  2. All tracks were filtered out as too short or stationary")
            print("  3. The input file format was incorrect")
            print("You can still view the video frames in the GUI.")
        
        # Calculate ends only if there's data
        if len(self.tracksdf) > 0:
            self.ends = self.tracksdf.loc[
                self.tracksdf.groupby('ID')['time'].idxmax()
            ].loc[
                lambda df: (df['time'] < (self.tracksdf['time'].max() - 50)) &
                        (df['x'] > 50) & (df['x'] < (self.tracksdf['x'].max() - 50)) &
                        (df['y'] > 50) & (df['y'] < (self.tracksdf['y'].max() - 50))
            ].sort_values('time')['ID'].tolist()
        else:
            self.ends = []

        print(f"Found {len(self.ends)} track endings that need manual review")
        if len(self.ends) == 0:
            print("Great! All tracks have been automatically combined or end at screen edges.")
            print("Opening GUI in view-only mode...")
        
        self.view_mode = False  # Will be set to True if entering view mode
        self.trackstemp=self.tracksdf.copy()
        self.endstemp=self.ends

        self.timeadd=10000
        # Distance window (in pixels) used to decide which nearby tracks to show in comparisons
        # and populate the dropdowns.
        self.xdist=10000
        self.timesubt=50
        #path of image file
        self.imgdata=h5py.File(imgpath, 'r')
        #gets maximum frame
        self.maxframe=np.max([int(x) for x in list(self.imgdata.keys()) if x.isdigit()])
        #path of file that sums up all of the images, useful for normalizing later
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
        self.drawn=[]

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
            self.win.tracksdist.setText(str(self.xdist))
            self.win.trackstime.setText(str(self.timeadd))
            self.win.framesbefore.setText(str(self.timesubt))
            self.win.figurewidget.update_comp()
        elif key=="update_data": #key to update the data in on the screen
            if self.close:
                return
            #normalizes data
            self.win.frameshow.setText(str(self.frame))
            img=np.asarray(self.imgdata[str(self.frame)])
            if self.rotate:
                img=np.swapaxes(img, 0, 1)
            if self.invert:
                img=255-img
            xMin=0
            xMax=np.shape(img)[0]
            yMin=0
            yMax=np.shape(img)[1]
            #sets x and y limits
            self.win.figurewidget.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
            #calls the update data program
            self.win.figurewidget.update_data(img)
