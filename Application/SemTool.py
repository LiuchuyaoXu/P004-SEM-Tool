#   File:   SemTool.py
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement classes related to the GUI of the SEM diagnostic tool.

import os
import sys
import time
import numpy as np
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

from SemImage import SemImage
from SemController import SemController

class ImagePlot(MplCanvas):
    def __init__(self, size):
        super().__init__(MplFigure())

        self.setWindowTitle("Image")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.imshow(np.zeros(size), cmap="gray", vmin=0, vmax=255)

    def updateData(self, semImage):
        data = semImage.image
        self.plot.set_data(data)
        self.figure.canvas.draw()

class FftPlot(MplCanvas):
    def __init__(self, size):
        super().__init__(MplFigure())

        self.setWindowTitle("Image FFT")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.imshow(np.zeros(size), cmap="gray", vmin=0, vmax=255)
    
    def updateData(self, semImage):
        data = semImage.fft
        data = data > 50000
        data = data * 255
        self.plot.set_data(data)
        self.figure.canvas.draw()

class FftDistPlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image FFT Distribution")

        self.axes = self.figure.add_subplot()

    def updateData(self, semImage):
        data = semImage.fft.flatten()
        print(data.max())
        self.axes.clear()
        self.plot = self.axes.hist(data, bins=1000, range=(0, 100000))
        self.axes.set_xlabel("FFT Magnitude")
        self.axes.set_ylabel("Number of pixels")
        self.figure.canvas.draw()

class HistPlot(MplCanvas):
    def __init__(self):
        super().__init__(MplFigure())

        self.setWindowTitle("Image Histogram")

        self.axes = self.figure.add_subplot()
        self.plot = self.axes.bar(np.arange(256), np.ones(256), width=1)

    def updateData(self, semImage):
        hist = semImage.histogram[0]
        hist = hist / hist.max()
        for bar, h in zip(self.plot, hist):
            bar.set_height(h)
        self.figure.canvas.draw()

class SemTool(QtWidgets.QMainWindow):
    frameUpdated = QtCore.Signal()
    semCorrectorRan = QtCore.Signal()

    xOffset = 512
    yOffset = 256
    width = 256
    height = 256

    def __init__(self):
        super().__init__()

        self.sem = SemController()

        self.sem().Execute("CMD_MODE_REDUCED")
        self.sem().Set("AP_RED_RASTER_POSN_X", str(self.xOffset))
        self.sem().Set("AP_RED_RASTER_POSN_Y", str(self.yOffset))
        self.sem().Set("AP_RED_RASTER_W", str(self.width))
        self.sem().Set("AP_RED_RASTER_H", str(self.height))

        self.imagePlot = ImagePlot([self.width, self.height])
        self.fftPlot = FftPlot([self.width, self.height])
        self.fftDistPlot = FftDistPlot()
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
        fftDistPlotButton = QtWidgets.QPushButton("FFT Distribution Plot")
        fftDistPlotButton.clicked.connect(self.openFftDistPlot)
        histPlotButton = QtWidgets.QPushButton("Histogram Plot")
        histPlotButton.clicked.connect(self.openHistPlot)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(imagePlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(fftPlotButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(fftDistPlotButton, QtWidgets.QDialogButtonBox.ActionRole)
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

    def openFftDistPlot(self):
        self.fftDistPlot.show()

    def openHistPlot(self):
        self.histPlot.show()

    def updatePlots(self):
        if self.imagePlot.isVisible() or self.fftPlot.isVisible() or self.histPlot.isVisible() or self.fftDistPlot.isVisible():
            start = time.time()

            image = SemImage.create(self.sem.grabImage(self.xOffset, self.yOffset, self.width, self.height))
            if self.hanningButton.isChecked():
                image.applyHanning()
            if self.histEquButton.isChecked():
                image.applyHistogramEqualisation()

            if self.imagePlot.isVisible():
                self.imagePlot.updateData(image)
            if self.fftPlot.isVisible():
                image.updateFft()
                self.fftPlot.updateData(image)
            if self.fftDistPlot.isVisible():
                image.updateFft()
                self.fftDistPlot.updateData(image)
            if self.histPlot.isVisible():
                image.updateHistogram()
                self.histPlot.updateData(image)

            end = time.time()
            print("Frame update time taken: ", end - start)
        self.frameUpdated.emit()

if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        gui = SemTool()
        gui.show()
        sys.exit(app.exec_())
