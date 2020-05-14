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

class ImageGrabber():
    def __init__(self, sem=None, imageDir=None):
        if sem:
            self.sem = sem
        else:
            self.sem = None
            self.dir = imageDir
            self.list = os.listdir(imageDir)
            self.index = 1

    def __call__(self):
        if self.sem:
            image = np.asarray(self.sem.img_array)
            return SemImage(image)
        else:
            if self.index >= len(self.list):
                self.index = 0
            image = Image.open(os.path.join(self.dir, self.list[self.index]))
            image = np.asarray(image)
            self.index += 1
            return SemImage(image)

class SemTool(QtWidgets.QMainWindow):
    def __init__(self, imageGrabber):
        super().__init__()        

        self.imageGrabber = imageGrabber

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
        # for plot in plots:
        #     plot.axis("off")

        image = self.imageGrabber()

        self.imagePlot = plots[0].imshow(image.array, cmap="gray", vmin=0, vmax=255)
        self.imageFftPlot = plots[1].imshow(image.fft, cmap="gray", vmin=0, vmax=255)
        hist = image.histogram / image.histogram.max()
        self.imageHistPlot = plots[2].bar(np.arange(hist.size), hist, width=1)
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

        image = self.imageGrabber()

        self.imagePlot.set_data(image.array)

        image.applyHanning()
        fft = image.fft
        fft = fft / fft.max()
        fft = fft > 0.001
        fft = fft * 255
        self.imageFftPlot.set_data(fft)

        # image.applyHistogramEqualisation()
        hist = image.histogram / image.histogram.max()
        for bar, h in zip(self.imageHistPlot, hist):
            bar.set_height(h)
        self.canvas.figure.canvas.draw()

        end = time.time()
        print(end - start)

if __name__ == "__main__":
    if SEM_API:
        with SEM_API.SEM_API("remote") as sem:
            app = QtWidgets.QApplication(sys.argv)
            gui = SemTool(ImageGrabber(sem=sem))
            gui.show()
            sys.exit(app.exec_())
    else:
        app = QtWidgets.QApplication(sys.argv)
        gui = SemTool(ImageGrabber(imageDir="./Images - For Testing SemCorrector"))
        gui.show()
        sys.exit(app.exec_())
