import sys
import matplotlib as mpl
mpl.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QInputDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True)
import pandas as pd
from tqdm import tqdm
from PyQt5.QtCore import pyqtSlot

def findpair(ID2,history,possiblecombos):
    if ID2 in list(possiblecombos.ID1):
        #need to consider that there may be more than one possibility for an end point
        #ended up taking the first value because it's the closest in time
        return(findpair(list(possiblecombos.loc[possiblecombos.ID1==ID2].ID2)[0],history+[ID2],possiblecombos))
    else:
        return(history+[ID2])

def findpairreverse(ID1,history,possiblecombos):
    if ID1 in list(possiblecombos.ID2):
        #need to consider that there may be more than one possibility for an end point
        #ended up taking the first value because it's the closest in time
        return(findpairreverse(list(possiblecombos.loc[possiblecombos.ID2==ID1].ID1)[0],history+[ID1],possiblecombos))
    else:
        return(history+[ID1])

def combinewormtracks(path):
    tracks=np.load(path)
    tracksdf=pd.DataFrame(tracks, columns = ['ID','time','x','y'])

    meanangles=pd.DataFrame(columns=["meanangle"],index=np.unique(tracksdf.ID).astype(int))
    for ID in tqdm(np.unique(tracksdf.ID).astype(int)):
        if len(tracksdf.loc[tracksdf.ID==ID])<6:
            meanangles.loc[ID]=120
            continue
        start=int(min(tracksdf.loc[tracksdf.ID==ID].time))
        end=int(max(tracksdf.loc[tracksdf.ID==ID].time))
        #takes three consecutive points in time and calculates the engle between them
        a=tracksdf.loc[(tracksdf.ID==ID)
                       &(start<tracksdf.time)
                       &(tracksdf.time<end-2)]
        b=tracksdf.loc[(tracksdf.ID==ID)
                       &(start+1<tracksdf.time)
                       &(tracksdf.time<end-1)]
        c=tracksdf.loc[(tracksdf.ID==ID)
                       &(start+2<tracksdf.time)
                       &(tracksdf.time<end)]
        meanangles.loc[ID]=np.mean(np.abs(np.degrees(np.arctan2(np.asarray(c.y)-np.asarray(b.y),
                                                                          np.asarray(c.x)-np.asarray(b.x))
                                                               - np.arctan2(np.asarray(a.y)-np.asarray(b.y),
                                                                            np.asarray(a.x)-np.asarray(b.x)))))
    tracksdf=tracksdf[np.isin(np.asarray(tracksdf.ID),meanangles[meanangles.meanangle>=120].index)]
    #creates dataframe with start and end times for each ID
    startend=pd.DataFrame(columns=["start","end"])
    for ID in np.unique(tracksdf.ID).astype(int):
        startend.loc[ID,:]=int(np.min(tracksdf.loc[tracksdf.ID==ID].time)),int(np.max(tracksdf.loc[tracksdf.ID==ID].time))
    startend=startend.astype(int)


    #gets all possible combinations of two indexes within 10 frames and 20 distance
    possiblecombos=pd.DataFrame(columns=["ID1","ID2","end","start"])#,"dist"])
    for ID in tqdm(np.unique(tracksdf.ID)):
        endindex=startend.loc[ID].end
        endlocation=tracksdf.loc[(tracksdf.ID==ID) & (tracksdf.time==endindex),["x","y"]].values
        for end in range(endindex,endindex+10):
            if end+1 in list(startend.start):
                for startID in startend.index[startend.start==end+1]:
                    startlocation=tracksdf.loc[(tracksdf.ID==startID) & (tracksdf.time==end+1),["x","y"]].values
                    if np.linalg.norm(startlocation-endlocation) < 20:
                        possiblecombos.loc[len(possiblecombos.index)] = [int(ID),startID,endindex,end+1]#,np.linalg.norm(startlocation-endlocation)] 


    combos=[]
    for ID in np.unique(tracksdf.ID).astype(int):
        combo=list(np.flip(findpairreverse(ID,[],possiblecombos))[:-1])+findpair(ID,[],possiblecombos)
        len(combo)>1 and combos.append(sorted(combo))

    dists=[]
    angles=[]
    lengths=np.zeros([len(possiblecombos.index),2])
    for i in tqdm(range(len(possiblecombos.index))):
        ID1=int(possiblecombos[possiblecombos.index==i].ID1)#stores IDs for the start and end track
        ID2=int(possiblecombos[possiblecombos.index==i].ID2)#stores IDs for the start and end track
        lengths[i,:]=[len(tracksdf[tracksdf.ID==ID1]),len(tracksdf[tracksdf.ID==ID2])] #stores the lengths of each track
        
        #finds the difference between the last points of ID1
        diff1=(tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end)][["x","y"]].values[0]
               -tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end-1)][["x","y"]].values[0])
        #finds the difference between the first points of ID2
        diff2=(tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start+1)][["x","y"]].values[0]
               -tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start)][["x","y"]].values[0])
        #finds the location of the end of ID1
        ID1end=tracksdf[(tracksdf.ID==ID1)&(tracksdf.time==max(tracksdf[tracksdf.ID==ID1].time))][["x","y"]].values[0]
        
        #finds the location of the start of ID2
        ID2start=tracksdf[(tracksdf.ID==ID2)&(tracksdf.time==min(tracksdf[tracksdf.ID==ID2].time))][["x","y"]].values[0]
        
        #finds the distance between the predicted points
        dist = np.sqrt(np.sum(np.square(ID1end+diff1*(int(possiblecombos[possiblecombos.index==i].start)
                                                  -int(possiblecombos[possiblecombos.index==i].end))/2
                                        -(ID2start-diff2*(int(possiblecombos[possiblecombos.index==i].start)
                                                      -int(possiblecombos[possiblecombos.index==i].end))/2))))
        angle = np.min([np.abs(np.arctan2(diff1[1],diff1[0])
                                -np.arctan2(diff2[1],diff2[0]))*(180/np.pi),
                        360-np.abs(np.arctan2(diff1[1],diff1[0])
                                -np.arctan2(diff2[1],diff2[0]))*(180/np.pi)])
        dists.append(dist)
        angles.append(angle)

    frames=np.nonzero((np.asarray(dists)<10) & (np.sum(lengths,axis=1)>=15) & (lengths[:,0]>=4) & (lengths[:,1]>4) & (np.asarray(angles)<90))[0]
    print(str(len(frames))+", or "+str(len(frames)/len(dists)*100)+"%")
    class MplCanvas(FigureCanvasQTAgg):
        def __init__(self, parent=None, width=10, height=10, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            super(MplCanvas, self).__init__(fig)


    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, *args, **kwargs):
            self.comboiter=0
            self.correctframes=[]
            super(MainWindow, self).__init__(*args, **kwargs)


            self.canvas = MplCanvas(self, width=10, height=10, dpi=100)
            self.setCentralWidget(self.canvas)
            self.right = QPushButton('Right', self)
            self.right.move(50,10)
            self.right.clicked.connect(self.nextright)

            self.wrong = QPushButton('Wrong', self)
            self.wrong.move(200,10)
            self.wrong.clicked.connect(self.nextwrong)

            self.finish = QPushButton('Finish', self)
            self.finish.move(350,10)
            self.finish.clicked.connect(self.returnnumpy)

            self.update_graph()
            self.show()

        @pyqtSlot()
        def nextright(self):
            self.correctframes.append(1)
            self.update_graph()
            self.comboiter+=1


        def nextwrong(self):
            self.correctframes.append(0)
            self.update_graph()
            self.comboiter+=1

        def showDialog(self):
            text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
            if ok:
                combine=[int(s) for s in text.split(' ')]
                for ID in combine:
                    tracksdf.loc[tracksdf.ID==ID,"ID"]=np.min(combine)


        def update_graph(self):
            self.canvas.axes.cla()
                
            ID1=int(possiblecombos[possiblecombos.index==frames[self.comboiter]].ID1)#stores IDs for the start and end track
            ID2=int(possiblecombos[possiblecombos.index==frames[self.comboiter]].ID2)#stores IDs for the start and end track

            #finds the difference between the last points of ID1
            diff1=(tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end)][["x","y"]].values[0]
                   -tracksdf[(tracksdf.ID==ID1) & (tracksdf.time==startend.loc[ID1].end-1)][["x","y"]].values[0])


            #finds the difference between the first points of ID2
            diff2=(tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start+1)][["x","y"]].values[0]
                   -tracksdf[(tracksdf.ID==ID2) & (tracksdf.time==startend.loc[ID2].start)][["x","y"]].values[0])

            #plots the two IDs
            self.canvas.axes.plot(tracksdf[tracksdf.ID==ID1].x.values,
                     tracksdf[tracksdf.ID==ID1].y.values,label=ID1)
            self.canvas.axes.plot(tracksdf[tracksdf.ID==ID2].x.values,
                     tracksdf[tracksdf.ID==ID2].y.values,label=ID2)

            #finds the location of the end of ID1
            ID1end=tracksdf[(tracksdf.ID==ID1)&(tracksdf.time==max(tracksdf[tracksdf.ID==ID1].time))][["x","y"]].values[0]

            #finds the location of the start of ID2
            ID2start=tracksdf[(tracksdf.ID==ID2)&(tracksdf.time==min(tracksdf[tracksdf.ID==ID2].time))][["x","y"]].values[0]


            #predicts where the worm should be (halfway)- gives a starting point of the end of ID1 and an ending point that is predicted
            prediction1=np.stack([ID1end,ID1end+diff1*(int(possiblecombos[possiblecombos.index==frames[self.comboiter]].start)
                                                      -int(possiblecombos[possiblecombos.index==frames[self.comboiter]].end))/2])


            #predicts where the worm should be (halfway)- gives a starting point of the end of ID1 and an ending point that is predicted
            prediction2=np.stack([ID2start,ID2start-diff2*(int(possiblecombos[possiblecombos.index==frames[self.comboiter]].start)
                                                          -int(possiblecombos[possiblecombos.index==frames[self.comboiter]].end))/2])

            #finds the distance between the predicted points
            dist = np.sqrt(np.sum(np.square(prediction1[1]-prediction2[1])))


            angle = np.min([np.abs(np.arctan2(diff1[1],diff1[0])
                                -np.arctan2(diff2[1],diff2[0]))*(180/np.pi),
                        360-np.abs(np.arctan2(diff1[1],diff1[0])
                                -np.arctan2(diff2[1],diff2[0]))*(180/np.pi)])

            #plots the prediction line
            self.canvas.axes.plot(prediction1[:,0],prediction1[:,1],color="black",linestyle="dashed")


            self.canvas.axes.plot(prediction2[:,0],prediction2[:,1],color="black",linestyle="dashed",
                     label="prediction distance = "+str(np.round(dist,2))+
                     ", \n prediction angle = "
                     +str(np.round(angle,2)))
            self.test=QCheckBox(str(1))
            self.test.move(300,20)
            self.canvas.axes.legend()
            self.canvas.draw()

        def returnnumpy(self):
            np.save("correctframes.npy",np.asarray(self.correctframes))


    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()


if __name__ == "__main__":
    path = sys.argv[1]
    combinewormtracks(path)
