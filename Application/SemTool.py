#   File:   SemTool.py
#
#   Brief:  Implement classes related to the GUI of the diagnostic tool.
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
    SEM_API = None
    print("Warning, could not import SEM_API, SEM images will be read from a local folder.")

class SemTool(QtWidgets.QMainWindow):
    def __init__(self, imageDir=None):
        super().__init__()        

        if SEM_API:
            sem.UpdateImage_Start()
        else:
            self.imageDir = imageDir
            self.images = os.listdir(self.imageDir)
            self.imageIndex = 1

        self.setWindowTitle("SEM Real-time Diagnostic Tool")

        self.initCanvas()
        # self.initControlPanel()

        self.frameTimer = QtCore.QTimer()
        self.frameTimer.timeout.connect(self.updateCanvas)
        self.frameTimer.start(1000)

    def initCanvas(self):
        self.canvas = MplCanvas(MplFigure())
        self.setCentralWidget(self.canvas)

        plots = self.canvas.figure.subplots(1, 3)
        for plot in plots:
            plot.axis("off")

        if SEM_API:
            image = SemImage(np.asarray(sem.img_array))
        else:
            image = Image.open(os.path.join(self.imageDir, self.images[self.imageIndex]))
            image = SemImage(np.asarray(image))

        self.imagePlot = plots[0].imshow(image.array, cmap="gray", vmin=0, vmax=255)
        self.imageFftPlot = plots[1].imshow(image.fft, cmap="gray", vmin=0, vmax=255)
        self.imageHistPlot = plots[2].bar(np.arange(image.histogram.size), image.histogram, width=1)
        self.canvas.figure.canvas.draw()

    def initControlPanel(self):
        panel = QtWidgets.QDockWidget("Control Panel", self)
        panel.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.zoom = QtWidgets.QSlider(QtCore.Qt.Horizontal, panel)
        self.zoom.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.zoom.setTickInterval(10)
        self.zoom.setSingleStep(1)
        self.zoom.setMinimum(1)
        self.zoom.setMaximum(100)
        self.zoom.valueChanged.connect(self.updateZoom)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)

    def updateZoom(self, value):
        self.zoom.setValue(value)

    def updateCanvas(self):
        start = time.time()

        if SEM_API:
            image = SemImage(np.asarray(sem.img_array))
        else:
            image = Image.open(os.path.join(self.imageDir, self.images[self.imageIndex]))
            image = SemImage(np.asarray(image))
            self.imageIndex += 1
            if self.imageIndex == len(self.images):
                self.imageIndex = 0

        self.imagePlot.set_data(image.array)

        image.applyHanning()
        fft = image.fft
        fft = fft / fft.max()
        fft = fft > 0.001
        fft = fft * 255
        self.imageFftPlot.set_data(fft)

        for bar, h in zip(self.imageHistPlot, image.histogram):
            bar.set_height(h)
        self.canvas.figure.canvas.draw()

        end = time.time()
        print(end - start)

if __name__ == "__main__":
    if SEM_API:
        with SEM_API.SEM_API("remote") as sem:
            app = QtWidgets.QApplication(sys.argv)
            gui = SemTool()
            gui.show()
            sys.exit(app.exec_())
    else:
        app = QtWidgets.QApplication(sys.argv)
        gui = SemTool("./Images - For Testing SemCorrector")
        gui.show()
        sys.exit(app.exec_())
