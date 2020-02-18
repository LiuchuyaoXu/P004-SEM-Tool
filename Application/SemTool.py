#   File:   SemTool.py
#
#   Brief:  Implement a class for properties and methods related to SEM real-time diagnostic tool GUI.
# 
#   Author: Liuchuyao Xu, 2020

import os
import sys
import time

import numpy as np
import numpy.ma as ma
from PIL import Image
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.colors import LogNorm as MplLogNorm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

from SemImage import SemImage

try:
    import SEM_API
except:
    print("Warning, could not import SEM_API, SEM images will be read from a local folder.")

class SemTool(QtWidgets.QMainWindow):
    def __init__(self, sem=None, dir=None):
        super().__init__()        

        self.setWindowTitle("SEM Real-time Diagnostic Tool")

        self.initCanvas()
        self.initControlPanel()

    def initCanvas(self):
        canvas = MplCanvas(MplFigure())
        self.setCentralWidget(canvas)

        plots = canvas.figure.subplots(1, 3)
        for plot in plots:
            plot.axis("off")

        try:
            image = np.asarray(sem.img_array)
        except:



        self.imagePlot = plots[0][0].imshow(self.image, cmap="gray")
        self.imageFftPlot = plots[0][1].imshow(self.image.getFft(), cmap="gray", norm=MplLogNorm())
        self.imageHistPlot = plots[0][2].bar(self.image.getHist()[1][:-1], self.image.getHist()[0], width=1)

    def initControlPanel(self):
        panel = QtWidgets.QDockWidget("Control Panel", self)
        panel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)

if __name__ == "__main__":
    try:
        with SEM_API.SEM_API("remote") as sem:
            app = QtWidgets.QApplication(sys.argv)
            gui = SemTool(sem=sem)
            gui.show()
            sys.exit(app.exec_())
    except:
            app = QtWidgets.QApplication(sys.argv)
            gui = SemTool(dir="./Images for Testing Correction Algorithm")
            gui.show()
            sys.exit(app.exec_())
