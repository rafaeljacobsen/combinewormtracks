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
import pickle
from PyQt5.QtCore import pyqtSlot

def combinewormtracks(path):
    with open(path, 'rb') as handle:
        inputs = pickle.load(handle)


    combos=inputs["combos"]
    tracksdf=inputs["tracksdf"]
    startend=inputs["startend"]

    class MplCanvas(FigureCanvasQTAgg):
        def __init__(self, parent=None, width=10, height=10, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            super(MplCanvas, self).__init__(fig)


    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, *args, **kwargs):
            self.comboiter=0
            super(MainWindow, self).__init__(*args, **kwargs)

            self.canvas = MplCanvas(self, width=10, height=10, dpi=100)
            self.setCentralWidget(self.canvas)
            nextplot = QPushButton('Next Plot', self)
            nextplot.move(50,10)
            nextplot.clicked.connect(self.gotonextplot)

            self.submitlines = QPushButton('Respond', self)
            self.submitlines.move(200,10)
            self.submitlines.clicked.connect(self.showDialog)


            self.finish = QPushButton('Finish', self)
            self.finish.move(350,10)
            self.finish.clicked.connect(self.returndataframe)
            self.show()

        @pyqtSlot()
        def gotonextplot(self):
            self.update_graph(combos[self.comboiter])
            self.comboiter+=1

        def showDialog(self):
            text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter text:')
            if ok:
                combine=[int(s) for s in text.split(' ')]
                for ID in combine:
                    tracksdf.loc[tracksdf.ID==ID,"ID"]=np.min(combine)

        def update_graph(self,points):
            self.canvas.axes.cla()
            iterator=combos[self.comboiter]
            for j in range(len(iterator)):
                ID=iterator[j]

                diffstart=(tracksdf[(tracksdf.ID==ID) & (tracksdf.time==startend.loc[ID].start+1)][["x","y"]].values[0]
                          -tracksdf[(tracksdf.ID==ID) & (tracksdf.time==startend.loc[ID].start)][["x","y"]].values[0])

                diffend=(tracksdf[(tracksdf.ID==ID) & (tracksdf.time==startend.loc[ID].end)][["x","y"]].values[0]
                        -tracksdf[(tracksdf.ID==ID) & (tracksdf.time==startend.loc[ID].end-1)][["x","y"]].values[0])

                IDstart=tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].start)][["x","y"]].values[0]
                IDend=tracksdf[(tracksdf.ID==ID)&(tracksdf.time==startend.loc[ID].end)][["x","y"]].values[0]

                if ID != iterator[0]:
                    predictionstart=np.stack([IDstart,IDstart+diffstart*(startend.loc[iterator[j-1]].end
                                                                         -startend.loc[ID].start)/2])

                    #finds the distance between the predicted points
                    dist = np.sqrt(np.sum(np.square(prevpred-predictionstart[1])))
                    angle = np.min([np.abs(np.arctan2(prevdiff[1],prevdiff[0])
                                           -np.arctan2(diffstart[1],diffstart[0]))*(180/np.pi),
                                    360-np.abs(np.arctan2(prevdiff[1],prevdiff[0])
                                               -np.arctan2(diffstart[1],diffstart[0]))*(180/np.pi)])

                    self.canvas.axes.plot(predictionstart[:,0],predictionstart[:,1],color="grey",linestyle="dashed",
                             label="prediction distance = "+str(np.round(dist,2))+
                             ", \n prediction angle = "+str(np.round(angle)))

                self.canvas.axes.plot(tracksdf[tracksdf.ID==ID].x.values,
                         tracksdf[tracksdf.ID==ID].y.values,label=ID)

                if ID != iterator[-1]:
                    predictionend=np.stack([IDend,IDend-diffend*(startend.loc[ID].end
                                                                 -startend.loc[iterator[j+1]].start)/2])
                    self.canvas.axes.plot(predictionend[:,0],predictionend[:,1],color="black",linestyle="dashed")
                    prevpred = predictionend[1]
                    prevdiff=diffend

            self.test=QCheckBox(str(1))
            self.test.move(300,20)
            self.canvas.axes.legend()
            self.canvas.draw()

        def returndataframe(self):
            tracksdf.to_csv("outputtracks.csv")

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()

if __name__ == "__main__":
    path = sys.argv[1]
    combinewormtracks(path)
