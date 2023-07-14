import random
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from PyQt5.Qt import Qt
import time as TIME

class TrackFig(pg.PlotWidget):
    def __init__(self,gui):
        self.gui=gui

        self.plots={}
        super().__init__()

        #creates the image item
        self.image=pg.ImageItem()
        self.addItem(self.image)

        # build lookup table
        self.lut = np.zeros((256,3), dtype=np.ubyte)
        self.lut[0:10,:] =255
        self.lut[10:74,:] = np.stack([np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4)),
                                np.flip(np.arange(0,255,4))],axis=1)
        self.lut[74:,:] = 0

        # Apply the colormap
        self.image.setLookupTable(self.lut)
        #creates a legend
        self.legend=self.addLegend()

        self.setAspectLocked()

    def keyPressEvent(self, event): #activated whenever any key is pressed
        key=event.key()
        if key==Qt.Key_Space:
            #increments frame
            self.gui.frame+=1 #increments the frame
            self.gui.win.frameshow.setText(str(self.gui.frame))
            #calls update data key when space is clicked
            self.gui.respond("update_data")

    def update_data(self,img):
        self.clear()
        self.get_tracks()
        self.image=pg.ImageItem()
        self.addItem(self.image)
        self.image.setLookupTable(self.lut)
        self.image.setImage(img[:,:],autoLevels=False,levels=[0,255])
        colors=np.tile(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#cacaca','#f3f134'],3)
        iter=0
        for key in self.plots.keys():
            self.plots[key].clear()

        self.plots={}
        self.legend.clear()
        start_time = TIME.time()
        for track in self.gui.graphstodraw:
            xs=self.gui.tracksdf[(self.gui.tracksdf.ID==track)\
                                &(self.gui.tracksdf.time>self.gui.frame-self.gui.timedist)\
                                &(self.gui.tracksdf.time<self.gui.frame)].sort_values(by=['time']).x.values
            ys=self.gui.tracksdf[(self.gui.tracksdf.ID==track)\
                                &(self.gui.tracksdf.time>self.gui.frame-self.gui.timedist)\
                                &(self.gui.tracksdf.time<self.gui.frame)].sort_values(by=['time']).y.values
            if np.mod(track,30) < len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[np.mod(track,30)],width=5,style=QtCore.Qt.SolidLine))
            elif np.mod(track,30) < 2*len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[np.mod(track,30)],width=5,style=QtCore.Qt.DotLine))
            elif np.mod(track,30) < 3*len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[np.mod(track,30)],width=5,style=QtCore.Qt.DashLine))
            self.addItem(self.plots[track])
            self.legend.addItem(self.plots[track],str(int(track)))
            iter+=1

    def get_tracks(self):
        self.gui.graphstodraw=[]


        for ID in np.unique(self.gui.tracksdf.ID.values):
            if self.gui.frame in self.gui.tracksdf[self.gui.tracksdf.ID==ID].time.values:
                self.gui.graphstodraw.append(int(ID))
