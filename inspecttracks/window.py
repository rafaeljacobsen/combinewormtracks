import random
from widgets import *
import numpy as np
import pandas as pd
import h5py
from PyQt5 import QtCore
import pyqtgraph as pg
import pickle
import sys
import argparse
import time as TIME

class Window(QMainWindow):
    def __init__(self,gui):
        pg.setConfigOption('background', 'w')
        super().__init__()
        self.gui=gui
        self.gui.timedist=15

        ####################################################################
        # This area is for laying out the buttons, dropdowns, and displays #
        ####################################################################

        #resizes the gui screen
        self.resize(int(self.gui.screen_w*0.3), self.gui.screen_h*4//5)

        #creats the central widget that takes up the whole window
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        #creates the grid that all of the subgrids will be placed into
        maingrid=QGridLayout()

        #adds the image plot
        self.figurewidget=TrackFig(self.gui)

        #adds the image plot to the main grid
        maingrid.addWidget(self.figurewidget,3,0)

        #creates the grid layouts
        toprow=QGridLayout()
        bottomrow=QGridLayout()
        rightbartop=QVBoxLayout()


        #widgets for the top row
        self.nextplot = QPushButton('Next Plot', self)
        self.nextplot.clicked.connect(self.gotonextplot)
        self.prevplot = QPushButton('Previous Plot', self)
        self.prevplot.clicked.connect(self.gotoprevplot)
        #adds a frame display icon and label
        self.framelabel = QLabel("Frame: ",self)
        self.framelabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #adds a box that both shows and edits the current frame
        self.frameshow = QLineEdit(self)
        self.frameshow.setText(str(0))
        self.frameshow.editingFinished.connect(self.updateframe)
        #buttons that modify how the tracks are shown
        self.label1 = QLabel("Time range to show frames: ",self)
        self.label1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.trackstime = QLineEdit(self)
        self.trackstime.setText(str(15))
        self.trackstime.editingFinished.connect(self.modtime)

        #adds widgets to layout
        toprow.addWidget(self.nextplot,0,0)
        toprow.addWidget(self.prevplot,0,1)
        toprow.addWidget(self.label1,0,2)
        toprow.addWidget(self.trackstime,0,3)
        toprow.addWidget(self.framelabel,0,4)
        toprow.addWidget(self.frameshow,0,5)

        #sets the ratio of the items in the top and middle row
        toprow.setColumnStretch(0, 2)
        toprow.setColumnStretch(1, 2)


        #adds layouts to main grid
        maingrid.addLayout(toprow,0,0)

        #makes the bottom rows adjacent to the top row
        bottomrow.setAlignment(Qt.AlignTop)

        #adds the main grid to the central widget
        self.centralWidget.setLayout(maingrid)

    #called when the previous frames button is edited
    def modprevframes(self):
        self.gui.prevframes=int(self.framesbefore.text())
        self.gui.respond("update_data")

    #called when the trackstime button is edited
    def modtime(self):
        if self.trackstime.text().isdigit():
            self.gui.timedist=int(self.trackstime.text())
            self.gui.respond("update_data")

    #correctly closes the gui
    def closeEvent(self, event):
        self.gui.respond("close")

    #called when frame number is changed
    def updateframe(self):
        if self.frameshow.text().isdigit():
            self.gui.frame=int(self.frameshow.text())
            if self.gui.frame < self.gui.maxframe and self.gui.frame >= 0:
                self.gui.respond("update_data")

    #go to the next plot
    def gotonextplot(self):
        if self.gui.frame < self.gui.maxframe-1:
            self.gui.frame+=1
        self.gui.respond("update_data")

    #go to the previous plot
    def gotoprevplot(self):
        if self.gui.frame >= 1:
            self.gui.frame-=1
        self.gui.respond("update_data")
