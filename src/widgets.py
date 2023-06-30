import random
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from PyQt5.Qt import Qt
import time as TIME

class CombineDialogErr(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERROR")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Cannot combine overlapping tracks")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


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
            self.gui.win.frameshow.setValue(self.gui.frame)
            #calls update data key when space is clicked
            self.gui.respond("update_data")

    def update_data(self,img):
        self.clear()
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
                                &(self.gui.tracksdf.time>self.gui.starttime-self.gui.prevframes)\
                                &(self.gui.tracksdf.time<self.gui.frame)].sort_values(by=['time']).x.values
            ys=self.gui.tracksdf[(self.gui.tracksdf.ID==track)\
                                &(self.gui.tracksdf.time>self.gui.starttime-self.gui.prevframes)\
                                &(self.gui.tracksdf.time<self.gui.frame)].sort_values(by=['time']).y.values
            temp_time = TIME.time()
            if iter < len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.SolidLine))
            elif iter < 2*len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.DotLine))
            elif iter < 3*len(colors)/3:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[iter],width=5,style=QtCore.Qt.DashLine))
            else:
                self.plots[track] = pg.PlotDataItem(x=xs, y=ys, pen=pg.mkPen(colors[np.mod(iter,30)],width=5,style=QtCore.Qt.SolidLine))
            self.addItem(self.plots[track])
            self.legend.addItem(self.plots[track],str(int(track)))
            iter+=1

    def update_comp(self):
        start_time = TIME.time()
        self.gui.ID=self.gui.ends[self.gui.enditer]
        self.gui.switchpercombo[self.gui.enditer]=0
        if self.gui.ID in self.gui.switches.keys():
            self.gui.ID=self.gui.switches[self.gui.ID]
        #frames of additional tracks to show
        self.gui.prevframes=5
        #distance of tracks to show
        self.gui.spacedist=150
        #time of tracks to show
        self.gui.timedist=70
        if len(self.gui.tracksdf[self.gui.tracksdf.ID==self.gui.ID])==0:
            self.gui.enditer+=1
            self.update_comp()
        else:
            self.gui.starttime=int(np.max(self.gui.tracksdf[self.gui.tracksdf.ID==self.gui.ID].time.values))-5
            if self.gui.starttime+10<np.max(self.gui.tracksdf.time.values):
                self.gui.frame=self.gui.starttime+10

            #gets all the data about when/where the worm track ends
            if self.gui.ID not in self.gui.tracksdf.ID.values:
                self.gui.win.compind.setText(f"<p style='background-color:white'>Track {str(self.gui.ID)} already removed or merged, go to next comparison.</p>")
                self.gui.win.compexp.setText(f"<p style='background-color:white'></p>")
                for i in range(5):
                    self.gui.win.comboboxes[i].clear()
                self.gui.respond("update_data")
            else:
                _,self.gui.endtime,self.gui.endx,self.gui.endy=list(self.gui.tracksdf[(self.gui.tracksdf.ID==self.gui.ID) & (self.gui.tracksdf.time==np.max(self.gui.tracksdf[self.gui.tracksdf.ID==self.gui.ID].time.values))].values)[0]
                self.get_tracks()
                self.gui.respond("update_data")
                #print("--- %s seconds for updating the comparison ---" % (TIME.time() - start_time))



    def get_tracks(self):
        self.gui.graphstodraw=[]
        compindtext="Comparison "+str(int(self.gui.enditer+1))+" out of "+str(int(len(self.gui.ends)))
        self.gui.win.compind.setText(f"<p style='background-color:white'>{compindtext}</p>")
        compexptext="Track "+str(int(self.gui.ID))+" ended at time t="+str(int(self.gui.endtime))
        self.gui.win.compexp.setText(f"<p style='background-color:white'>{compexptext}</p>")
        #gets all the tagged worms in the area

        start_time=TIME.time()
        for ID in np.unique(self.gui.tracksdf.ID.values):
            if len(self.gui.tracksdf[(self.gui.tracksdf.ID==ID)&(np.abs(self.gui.endtime-self.gui.tracksdf.time)<self.gui.timedist)])>0:
                if len(self.gui.tracksdf[(self.gui.tracksdf.ID==ID)&(np.abs(self.gui.endtime-self.gui.tracksdf.time)<self.gui.timedist)&(np.abs(self.gui.tracksdf.x-self.gui.endx)<self.gui.spacedist)&(np.abs(self.gui.tracksdf.y-self.gui.endy)<self.gui.spacedist)]):
                    self.gui.graphstodraw.append(int(ID))
        for i in range(5):
            self.gui.win.comboboxes[i].clear()
            self.gui.win.comboboxes[i].addItems(list(map(str, np.sort(self.gui.graphstodraw))))


        #print("--- %s seconds for updating the tracks ---" % (TIME.time() - start_time))
