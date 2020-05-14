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

class ImagePlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.imshow(np.zeros([768, 1024]), cmap="gray", vmin=0, vmax=255)

    def updateData(self, semImage):
        data = semImage.array
        self.plot.set_data(data)
        self.figure.canvas.draw()

class FftPlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image FFT")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.imshow(np.zeros([768, 1024]), cmap="gray", vmin=0, vmax=255)
    
    def updateData(self, semImage):
        data = semImage.fft
        self.plot.set_data(data)
        self.figure.canvas.draw()

class HistPlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image Histogram")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.bar(np.arange(256), np.zeros(256), width=1)

    def updateData(self, semImage):
        hist = semImage.histogram
        for bar, h in zip(self.plot, hist):
            bar.set_height(h)
        self.figure.canvas.draw()

class SemTool(QtWidgets.QMainWindow):
    def __init__(self, imageGrabber):
        super().__init__()

        self.imageGrabber = imageGrabber

        self.imagePlot = ImagePlot()
        self.fftPlot = FftPlot()
        self.histPlot = HistPlot()

        self.frameTimer = QtCore.QTimer()
        self.frameTimer.timeout.connect(self.updatePlots)
        self.frameTimer.start(1000)

        self.setWindowTitle("SEM Real-time Diagnostic Tool")

        self.initPanel()

    def initPanel(self):
        panel = QtWidgets.QWidget(self)
        panel.setWindowTitle("Control Panel")
        
        imagePlotButton = QtWidgets.QPushButton("Image Plot", panel)
        imagePlotButton.clicked.connect(self.openImagePlot)
        fftPlotButton = QtWidgets.QPushButton("FFT Plot", panel)
        fftPlotButton.clicked.connect(self.openFftPlot)
        histPlotButton = QtWidgets.QPushButton("Histogram Plot", panel)
        histPlotButton.clicked.connect(self.openHistPlot)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(imagePlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(fftPlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(histPlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.setParent(panel)

        self.setCentralWidget(panel)

    def openImagePlot(self):
        self.imagePlot.show()

    def openFftPlot(self):
        self.fftPlot.show()

    def openHistPlot(self):
        self.histPlot.show()

    def updatePlots(self):
        image = self.imageGrabber()
        if self.imagePlot.isVisible():
            self.imagePlot.updateData(image)
        if self.fftPlot.isVisible():
            self.fftPlot.updateData(image)
        if self.histPlot.isVisible():
            self.histPlot.updateData(image)

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
