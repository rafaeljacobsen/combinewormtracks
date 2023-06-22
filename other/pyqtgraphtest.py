import random
import numpy as np

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.subplots()
        self.ax.set_axis_off()

        self.setCentralWidget(self.canvas)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.on_timeout)
        timer.start(100)

    def on_timeout(self):
        x0, y0 = random.uniform(-2, 2), random.uniform(-2, 2)
        delta = 0.025
        x = y = np.arange(-3.0, 3.0, delta)
        X, Y = np.meshgrid(x, y)
        Z1 = np.exp(-(X ** 2) - Y ** 2)
        Z2 = np.exp(-((X - x0) ** 2) - (Y - y0) ** 2)
        Z = (Z1 - Z2) * 2
        self.ax.imshow(Z)
        self.canvas.draw()