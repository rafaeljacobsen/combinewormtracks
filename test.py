import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import numpy as np

app = pg.mkQApp()

win = pg.GraphicsLayoutWidget(show=True)

p1 = win.addPlot()
data1 = np.arange(0,300)
connected = np.round(np.random.rand(300))
print(connected)
curve1 = p1.plot(data1, connect=connected, pen=pg.mkPen(['red','blue'],width=5,style=QtCore.Qt.SolidLine))

app.exec_()
