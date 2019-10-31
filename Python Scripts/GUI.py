#   File:   GUI.py
#
#   Brief:  Implement a GUI using Qt for Python (PySide2).
# 
#   Author: Liuchuyao Xu, 2019

import sys

import matplotlib.figure as mpl_fig
import matplotlib.backends.backend_qt5agg as mpl_qt5agg

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SEMTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SEM Realtime Diagnostic Tool")

        # self.initCanvas()
        # self.setCentralWidget(self.canvas)

        self.initPlots()
        self.setCentralWidget(self.image)

        # self.initPanel()
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)

    def initCanvas(self):
        figure = mpl_fig.Figure()
        self.canvas = mpl_qt5agg.FigureCanvas(figure)
        self.canvas.plots = figure.subplots(nrows=2, ncols=2)
        self.canvas.plots[0,0].set_title("Original Image")
        self.canvas.plots[0,1].set_title("2D FFT")
        self.canvas.plots[1,0].set_title("X-Axis FFT")
        self.canvas.plots[1,1].set_title("Y-Axis FFT")

    def initPlots(self):
        pixmap = QtGui.QPixmap("../SEM Images/Armin241.tif")

        self.image = QtWidgets.QLabel()
        self.image.setPixmap(pixmap)

    def initPanel(self):
        self.panel = QtWidgets.QDockWidget()
        self.panel.setWindowTitle("Control Panel")
        self.panel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                                   QtCore.Qt.LeftDockWidgetArea)

        # slider = QtWidgets.QSlider(parent=self.panel, 
        #                            orientation=QtCore.Qt.Orientation.Horizontal)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = SEMTool()
    gui.show()
    sys.exit(app.exec_())
    