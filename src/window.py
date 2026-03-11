import random
from src.widgets import *
import numpy as np
import pandas as pd
import h5py
from PyQt5 import QtCore
import pyqtgraph as pg
import time as TIME
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

class Window(QMainWindow):
    def __init__(self,gui):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        super().__init__()
        self.gui=gui

        ####################################################################
        # This area is for laying out the buttons, dropdowns, and displays #
        ####################################################################

        #clears the manual output file
        self.writefile = open("manualoutput.txt", "w")
        self.writefile.write("")
        self.writefile.close()
        #opens the manual output file in append mode
        self.writefile = open("manualoutput.txt", "a")

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
        middlerow=QGridLayout()
        bottomrow=QGridLayout()
        rightbartop=QVBoxLayout()
        rightbarmiddle=QVBoxLayout()
        rightbarmiddle2=QVBoxLayout()
        rightbar=QVBoxLayout()


        #Labels and explanations for comparisons
        self.complabel = QLabel("Track evaluation explanation:",self)
        rightbartop.addWidget(self.complabel)
        #shows the comparison index and number of comparisons
        self.compind = QLabel("",self)
        self.compind.setWordWrap(True)
        rightbarmiddle.addWidget(self.compind)
        #shows track ID and when the track ended
        self.compexp = QLabel("",self)
        rightbarmiddle2.addWidget(self.compexp)

        #drop down boxes that show the possible tracks
        self.comboboxes=[]
        for i in range(5):
            self.comboboxes.append(QComboBox())

        #widgets for the first method of modification: combining tracks
        self.text1 = QLabel("Option 1: Track",self)
        self.comboboxes[0].setFixedWidth(100)
        self.text2 = QLabel("is the same worm as track",self)
        self.comboboxes[1].setFixedWidth(100)
        self.addchange1 = QPushButton("Add change",self)
        self.addchange1.setFixedWidth(100)
        self.addchange1.clicked.connect(self.combinetracks)

        #adds widgets to layout
        rightbar.addWidget(self.text1)
        rightbar.addWidget(self.comboboxes[0])
        rightbar.addWidget(self.text2)
        rightbar.addWidget(self.comboboxes[1])
        rightbar.addWidget(self.addchange1)

        #widgets for second method of modification: switching tracks
        self.text3 = QLabel("Option 2: Track",self)
        self.comboboxes[2].setFixedWidth(100)
        self.text4 = QLabel("took the place of track",self)
        self.comboboxes[3].setFixedWidth(100)
        self.text5 = QLabel("at time",self)
        self.timeedit = QLineEdit(self)
        self.timeedit.setFixedWidth(100)
        self.addchange2 = QPushButton("Add change",self)
        self.addchange2.setFixedWidth(100)
        self.addchange2.clicked.connect(self.switchtracks)

        #adds widgets to layout
        rightbar.addWidget(self.text3)
        rightbar.addWidget(self.comboboxes[2])
        rightbar.addWidget(self.text4)
        rightbar.addWidget(self.comboboxes[3])
        rightbar.addWidget(self.text5)
        rightbar.addWidget(self.timeedit)
        rightbar.addWidget(self.addchange2)

        #widgets for third method of modification: deleting tracks
        self.text6 = QLabel("Option 3: Delete",self)
        self.comboboxes[4].setFixedWidth(100)
        self.addchange3 = QPushButton("Add change",self)
        self.addchange3.setFixedWidth(100)
        self.addchange3.clicked.connect(self.deletetracks)

        
        self.text7 = QLabel("Option 4: Automatic combination",self)
        self.addchange4 = QPushButton("Add change",self)
        self.addchange4.setFixedWidth(100)
        self.addchange4.clicked.connect(self.autocombo)

        self.undobutton = QPushButton("Undo",self)
        self.undobutton.setFixedWidth(100)
        self.undobutton.clicked.connect(self.undo)
        self.savebutton = QPushButton("Save",self)
        self.savebutton.setFixedWidth(100)
        self.savebutton.clicked.connect(self.save)
        

        #adds widgets to layout
        rightbar.addWidget(self.text6)
        rightbar.addWidget(self.comboboxes[4])
        rightbar.addWidget(self.addchange3)
        rightbar.addWidget(self.text7)
        rightbar.addWidget(self.addchange4)
        rightbar.addWidget(self.undobutton)
        rightbar.addWidget(self.savebutton)

        #vertical spacer to keep widgets at the top close together
        verticalSpacer = QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        rightbar.addItem(verticalSpacer)

        #widgets for the top row
        self.nextplot = QPushButton('Next Plot', self)
        self.nextplot.clicked.connect(lambda: self.gotonextplot(1))

        # Create a shortcut for the F2 key
        self.shortcut = QShortcut(QKeySequence("F2"), self)
        self.shortcut.activated.connect(lambda: self.gotonextplot(1))
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("F1"), self)
        self.shortcut.activated.connect(lambda: self.gotoprevplot(1))

        
        # Create a shortcut for the F2 key
        self.shortcut = QShortcut(QKeySequence("F4"), self)
        self.shortcut.activated.connect(lambda: self.gotonextplot(10))
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("F3"), self)
        self.shortcut.activated.connect(lambda: self.gotoprevplot(10))

        
        # Create a shortcut for the F2 key
        self.shortcut = QShortcut(QKeySequence("F6"), self)
        self.shortcut.activated.connect(lambda: self.gotonextplot(100))
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("F5"), self)
        self.shortcut.activated.connect(lambda: self.gotoprevplot(100))

        
        # Create a shortcut for the F2 key
        self.shortcut = QShortcut(QKeySequence("F8"), self)
        self.shortcut.activated.connect(lambda: self.gotonextplot(500))
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("F7"), self)
        self.shortcut.activated.connect(lambda: self.gotoprevplot(500))

        
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("m"), self)
        self.shortcut.activated.connect(lambda: self.gotonextcomp())
        # Create a shortcut for the F1 key
        self.shortcut = QShortcut(QKeySequence("n"), self)
        self.shortcut.activated.connect(lambda: self.gotoprevcomp())
        
        self.prevplot = QPushButton('Previous Plot', self)
        self.prevplot.clicked.connect(lambda: self.gotoprevplot(1))
        #adds a frame display icon and label
        self.framelabel = QLabel("Frame: ",self)
        self.framelabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #adds a box that both shows and edits the current frame
        self.frameshow = QLineEdit(self)
        self.frameshow.setText(str(0))
        self.frameshow.editingFinished.connect(self.updateframe)

        #adds widgets to layout
        toprow.addWidget(self.nextplot,0,0)
        toprow.addWidget(self.prevplot,0,1)
        toprow.addWidget(self.framelabel,0,2)
        toprow.addWidget(self.frameshow,0,3)

        #widgets that affect the comparisons
        self.nextcomp = QPushButton('Next comparison', self)
        self.nextcomp.clicked.connect(self.gotonextcomp)
        self.prevcomp = QPushButton('Previous comparison', self)
        self.prevcomp.clicked.connect(self.gotoprevcomp)
        #comparison index display icon and label
        self.complabel = QLabel("Comparison: ",self)
        self.complabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #box that both shows and edits the current comparison index
        self.compshow = QLineEdit(self)
        self.compshow.setText("NaN")
        self.compshow.editingFinished.connect(self.updatecomp)

        #adds widgets to layout
        middlerow.addWidget(self.nextcomp,0,0)
        middlerow.addWidget(self.prevcomp,0,1)
        middlerow.addWidget(self.complabel,0,2)
        middlerow.addWidget(self.compshow,0,3)

        #sets the ratio of the items in the top and middle row
        toprow.setColumnStretch(0, 2)
        toprow.setColumnStretch(1, 2)
        middlerow.setColumnStretch(0, 2)
        middlerow.setColumnStretch(1, 2)

        #buttons that modify how the tracks are shown
        self.label1 = QLabel("Frames shown before end time: ",self)
        self.label1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.framesbefore = QLineEdit(self)
        self.framesbefore.setText(str(self.gui.timesubt))
        self.framesbefore.editingFinished.connect(self.modprevframes)
        self.label2 = QLabel("Time range to show frames: ",self)
        self.label1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.trackstime = QLineEdit(self)
        self.trackstime.setText(str(self.gui.timeadd))
        self.trackstime.editingFinished.connect(self.modtime)
        self.label3 = QLabel("Distance to show frames: ",self)
        self.label1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.tracksdist = QLineEdit(self)
        self.tracksdist.setText(str(self.gui.xdist))
        self.tracksdist.editingFinished.connect(self.moddist)

        #adds widgets to layout
        bottomrow.addWidget(self.label1,0,0)
        bottomrow.addWidget(self.framesbefore,0,1)
        bottomrow.addWidget(self.label2,0,2)
        bottomrow.addWidget(self.trackstime,0,3)
        bottomrow.addWidget(self.label3,0,4)
        bottomrow.addWidget(self.tracksdist,0,5)

        #adds layouts to main grid
        maingrid.addLayout(toprow,0,0)
        maingrid.addLayout(middlerow,1,0)
        maingrid.addLayout(bottomrow,2,0)
        maingrid.addLayout(rightbartop,0,1)
        maingrid.addLayout(rightbarmiddle,1,1)
        maingrid.addLayout(rightbarmiddle2,2,1)
        maingrid.addLayout(rightbar,3,1)

        #makes the bottom rows adjacent to the top row
        middlerow.setAlignment(Qt.AlignTop)
        bottomrow.setAlignment(Qt.AlignTop)

        #adds the main grid to the central widget
        self.centralWidget.setLayout(maingrid)

    #called when the previous frames button is edited
    def modprevframes(self):
        self.gui.timesubt=int(self.framesbefore.text())
        self.gui.respond("update_data")

    #called when the tracksdist button is edited
    def moddist(self):
        self.gui.xdist=int(self.tracksdist.text())
        self.gui.respond("get_tracks")
        self.gui.respond("update_data")

    #called when the trackstime button is edited
    def modtime(self):
        if self.trackstime.text().isdigit():
            self.gui.timeadd=int(self.trackstime.text())
            self.gui.respond("get_tracks")
            self.gui.respond("update_data")

    #called when the user combines two tracks
    def combinetracks(self):
        start_time=TIME.time()
        self.gui.trackstemp=self.gui.tracksdf.copy()
        self.gui.endstemp=self.gui.ends
        IDs=[int(self.comboboxes[0].currentText()),
             int(self.comboboxes[1].currentText())]
        #takes ID1 as the lesser of the two IDs and ID2 as the greater
        ID1=np.min(IDs)
        ID2=np.max(IDs)
        #if the tracks overlap in time, call an error and abort
        if bool(set(self.gui.tracksdf[self.gui.tracksdf.ID==ID1].time.values)\
                & set(self.gui.tracksdf[self.gui.tracksdf.ID==ID2].time.values)):
            errorwin = CombineDialogErr()
            errorwin.setWindowTitle("ERROR")
            errorwin.exec()
        else:
            #combines the tracks in the dataset
            self.gui.tracksdf.loc[self.gui.tracksdf.ID==ID2,["ID"]]=ID1
            self.gui.tracksdf=self.gui.tracksdf[np.isin(self.gui.tracksdf.ID,[ID2],invert=True)]
            #writes to output file
            self.writefile.write("Combined tracks "+str(ID1)+" and "+str(ID2)+"\n")
            #records history of changes
            self.gui.switches[ID2]=ID1
            self.gui.respond("update_data")

    #called when the user switches tracks
    def switchtracks(self):
        self.gui.trackstemp=self.gui.tracksdf.copy()
        self.gui.endstemp=self.gui.ends
        #gets IDs and time
        ID1=int(self.comboboxes[2].currentText())
        ID2=int(self.comboboxes[3].currentText())
        if len(self.timeedit.text()) == 0:
            return
        time=int(self.timeedit.text())

        
        if len(self.gui.tracksdf[(self.gui.tracksdf.ID==ID2)&(self.gui.tracksdf.time>=time)])>0:
            nextid = np.max(self.gui.tracksdf.ID.values)+1
            self.gui.tracksdf.loc[(self.gui.tracksdf.ID == ID2) & (self.gui.tracksdf.time >= time), 'ID'] = nextid

            # self.gui.tracksdf[self.gui.tracksdf.ID==ID2]=self.gui.tracksdf[(self.gui.tracksdf.ID==ID2)&(self.gui.tracksdf.time<=time)]
            self.gui.respond("get_tracks")
            self.gui.respond("update_data")
        #switches tracks at that time
        self.gui.tracksdf.loc[(self.gui.tracksdf.ID==ID1) & (self.gui.tracksdf.time>=time), 'ID']=ID2
        #writes to output file
        self.writefile.write("Switched track "+str(ID1)+" to "+str(ID2)+" at time "+str(time)+"\n")
        self.gui.respond("update_data")

    #called when the user deletes a track
    def deletetracks(self):
        self.gui.trackstemp=self.gui.tracksdf.copy()
        self.gui.endstemp=self.gui.ends.copy()
        ID1=int(self.comboboxes[4].currentText())
        #edits the tracksdf
        self.gui.tracksdf=self.gui.tracksdf[(self.gui.tracksdf.ID!=ID1)]
        self.writefile.write("Deleted ID "+str(ID1)+"\n")
        self.gui.respond("update_data")

    #the automatic combination function
    def autocombo(self):
        ID2=self.gui.ID
        time=self.gui.endtime
        
        
        neardict = self.gui.tracksdf[(self.gui.tracksdf.time > time - 5)\
                                     & (self.gui.tracksdf.time < time + 40)\
                                     & (self.gui.tracksdf.ID != ID2)]
        
        currenttrack = self.gui.tracksdf[(self.gui.tracksdf.time == time)\
                                     & (self.gui.tracksdf.ID == ID2)]
        
        # checks if the ID is in the dataframe
        if len(list(currenttrack.x)) == 0 or len(list(neardict.x)) == 0:
            return
        x_ref=list(currenttrack.x)[0]
        y_ref=list(currenttrack.y)[0]

        closest_idx = ((neardict.x - x_ref) ** 2 + (neardict.y - y_ref) ** 2).idxmin()

        ID1 = neardict.loc[closest_idx].ID

        
        self.gui.trackstemp=self.gui.tracksdf.copy()
        self.gui.endstemp=self.gui.ends
        
        if len(self.gui.tracksdf[(self.gui.tracksdf.ID==ID2)&(self.gui.tracksdf.time>=time)])>0:
            nextid = np.max(self.gui.tracksdf.ID.values)+1
            self.gui.tracksdf.loc[(self.gui.tracksdf.ID == ID2) & (self.gui.tracksdf.time >= time), 'ID'] = nextid

            # self.gui.tracksdf[self.gui.tracksdf.ID==ID2]=self.gui.tracksdf[(self.gui.tracksdf.ID==ID2)&(self.gui.tracksdf.time<=time)]
            self.gui.respond("get_tracks")
            self.gui.respond("update_data")
        #switches tracks at that time
        self.gui.tracksdf.loc[(self.gui.tracksdf.ID==ID1) & (self.gui.tracksdf.time>=time), 'ID']=ID2
        #writes to output file
        self.writefile.write("Switched track "+str(ID1)+" to "+str(ID2)+" at time "+str(time)+"\n")
        self.gui.respond("update_data")


    def undo(self):
        self.gui.tracksdf=self.gui.trackstemp
        self.gui.ends=self.gui.endstemp
        compindtext="Comparison "+str(int(self.gui.enditer+1))+" out of "+str(int(len(self.gui.ends)))
        self.gui.win.compind.setText(f"<p style='background-color:white'>{compindtext}</p>")
        self.gui.respond("update_data")


    def save(self):
        print("Saved")
        self.gui.tracksdf.to_csv("outputtracks.csv")

    #go to the next comparison
    def gotonextcomp(self):
        self.gui.enditer+=1
        self.compshow.setText(str(self.gui.enditer+1))
        self.gui.respond("update_comp")

    #called when the comparison number is changed
    def updatecomp(self):
        if self.compshow.text().isdigit():
            self.gui.enditer=int(self.compshow.text())-1
            self.gui.respond("update_comp")

    #go to the previous comparison
    def gotoprevcomp(self):
        if self.gui.enditer >= 1:
            self.gui.enditer-=1
        self.compshow.setText(str(self.gui.enditer+1))
        self.gui.respond("update_comp")

    #correctly closes the gui
    def closeEvent(self, event):
        self.gui.respond("close")

    #called when frame number is changed
    def updateframe(self):
        if self.frameshow.text().isdigit():
            self.gui.frame=int(self.frameshow.text())
            if self.gui.frame < self.gui.maxframe and self.gui.frame >= 0:
                # Refresh track selection before re-drawing so the displayed tracks
                # don't lag behind until some other UI event (like leaving a textbox).
                self.gui.respond("get_tracks")
                self.gui.respond("update_data")

    #go to the next plot
    def gotonextplot(self,num):
        if self.gui.frame < self.gui.maxframe-num:
            self.gui.frame+=num
        # Always refresh track selection before drawing.
        self.gui.respond("get_tracks")
        self.gui.respond("update_data")

    #go to the previous plot
    def gotoprevplot(self,num):
        if self.gui.frame >= num:
            self.gui.frame-=num
        # Always refresh track selection before drawing.
        self.gui.respond("get_tracks")
        self.gui.respond("update_data")

        
