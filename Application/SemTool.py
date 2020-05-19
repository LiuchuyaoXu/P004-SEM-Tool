#   File:   SemTool.py
#
#   Brief:  Implement classes related to the GUI of the diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2020

import os
import sys
import time
import numpy as np
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.colors import LogNorm as MplLogNorm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

from SemImageGrabber import SemImageGrabber

try:
    import SEM_API
except:
    SEM_API = None
    print("Warning, could not import SEM_API, SEM images will be read from a local folder.")

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
        threshold = 2 * data.sum() / 1024 / 768
        data = data > threshold
        data = data * 255
        self.plot.set_data(data)
        self.figure.canvas.draw()

class HistPlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image Histogram")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.bar(np.arange(256), np.ones(256), width=1)

    def updateData(self, semImage):
        hist = semImage.histogram
        hist = hist / hist.max()
        for bar, h in zip(self.plot, hist):
            bar.set_height(h)
        self.figure.canvas.draw()

class SemTool(QtWidgets.QMainWindow):
    frameUpdated = QtCore.Signal()

    def __init__(self, imageGrabber):
        super().__init__()

        self.imageGrabber = imageGrabber

        self.imagePlot = ImagePlot()
        self.fftPlot = FftPlot()
        self.histPlot = HistPlot()

        self.initPanel()
        self.setWindowTitle("SEM Real-time Diagnostic Tool")

        self.frameUpdated.connect(self.updatePlots, QtCore.Qt.QueuedConnection)
        self.updatePlots()

    def initPanel(self):
        panel = QtWidgets.QWidget(self)
        panel.setWindowTitle("Control Panel")
        self.setCentralWidget(panel)

        imagePlotButton = QtWidgets.QPushButton("Image Plot")
        imagePlotButton.clicked.connect(self.openImagePlot)
        fftPlotButton = QtWidgets.QPushButton("FFT Plot")
        fftPlotButton.clicked.connect(self.openFftPlot)
        histPlotButton = QtWidgets.QPushButton("Histogram Plot")
        histPlotButton.clicked.connect(self.openHistPlot)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(imagePlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(fftPlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(histPlotButton, QtWidgets.QDialogButtonBox.ActionRole)

        self.hanningButton = QtWidgets.QRadioButton("Hanning Window")
        self.hanningButton.setAutoExclusive(False)
        self.histEquButton = QtWidgets.QRadioButton("Histogram Equalisation")
        self.histEquButton.setAutoExclusive(False)

        radioBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        radioBox.addButton(self.hanningButton, QtWidgets.QDialogButtonBox.ActionRole)
        radioBox.addButton(self.histEquButton, QtWidgets.QDialogButtonBox.ActionRole)
        
        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, panel)
        layout.insertWidget(0, buttonBox)
        layout.insertWidget(1, radioBox)

    def openImagePlot(self):
        self.imagePlot.show()

    def openFftPlot(self):
        self.fftPlot.show()

    def openHistPlot(self):
        self.histPlot.show()

    def updatePlots(self):
        if self.imagePlot.isVisible() or self.fftPlot.isVisible() or self.histPlot.isVisible():
            start = time.time()

            image = self.imageGrabber()
            if self.hanningButton.isChecked():
                image.applyHanning(updateAll=False)
            if self.histEquButton.isChecked():
                image.applyHistogramEqualisation(updateAll=False)
            image.updateAll()

            if self.imagePlot.isVisible():
                self.imagePlot.updateData(image)
            if self.fftPlot.isVisible():
                self.fftPlot.updateData(image)
            if self.histPlot.isVisible():
                self.histPlot.updateData(image)

            end = time.time()
            print("Frame update time taken: ", end - start)
        self.frameUpdated.emit()

if __name__ == "__main__":
    if SEM_API:
        with SEM_API.SEM_API("remote") as sem:
            app = QtWidgets.QApplication(sys.argv)
            gui = SemTool(SemImageGrabber(sem=sem))
            gui.show()
            sys.exit(app.exec_())
    else:
        app = QtWidgets.QApplication(sys.argv)
        gui = SemTool(SemImageGrabber(imageDir="./Images - For Testing"))
        gui.show()
        sys.exit(app.exec_())
