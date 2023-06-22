import random
import numpy as np
np.set_printoptions(suppress=True)
import pandas as pd
import h5py
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from tqdm import tqdm
from PyQt5.Qt import Qt

images=h5py.File('../data/202304051.h5', 'r')
sumarray=np.load("sumarray.npy")
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        #self.win = pg.GraphicsWindow()
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')

        self.frame=0
        self.currentimg=pg.ImageView(self.graphWidget)
        #self.currentimg.autoLevels()
        self.next_frame()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Space")
            self.next_frame()

    def next_frame(self):
        img=images[str(self.frame)]['frame'][0].max(2)-sumarray/max(np.asarray(list(images.keys()))[:-1].astype(int))
        img=np.vectorize(lambda x: 0 if x < 0 else x)(img)
        img=np.vectorize(lambda x: 100 if x > 10 else x)(img)
        self.frame+=1
        self.currentimg.setImage(img)
        self.currentimg.show()
        #shown=self.ax.imshow(img,cmap="Greys")



#if __name__ == "__main__":
import sys

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.resize(640, 480)
w.show()

sys.exit(app.exec_())
