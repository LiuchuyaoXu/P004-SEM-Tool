# File:     SemImageGui.py
#
# Author:   Liuchuyao Xu, 2020

import numpy
from PIL import Image
from PySide2 import QtCharts
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from SemImage import SemImage

class ImagePlot(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('Image')

    def updateFrame(self, semImage):
        image = semImage.image()
        width = image.shape[0]
        height = image.shape[1]
        qtImage = QtGui.QImage(image, width, height, QtGui.QImage.Format_Grayscale8)
        qtPixmap = QtGui.QPixmap(qtImage)
        self.setPixmap(qtPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio))

class FftPlot(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('FFT')

    def updateFrame(self, semImage):
        fft = semImage.fft().clip(0, 65535).astype('uint16')
        width = fft.shape[0]
        height = fft.shape[1]
        qtImage = QtGui.QImage(fft, width, height, QtGui.QImage.Format_Grayscale16)
        qtPixmap = QtGui.QPixmap(qtImage)
        self.setPixmap(qtPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio))

class HistogramPlot(QtCharts.QtCharts.QChartView):

    def __init__(self):
        super().__init__()

        self.reduction = 8

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('Histogram')

        self.chart = QtCharts.QtCharts.QChart()
        self.setChart(self.chart)

    def updateFrame(self, semImage):
        histogram = semImage.histogram()
        series = QtCharts.QtCharts.QLineSeries()
        for i in range(round(2**semImage.bitDepth / self.reduction)):
            series.append(histogram[1][self.reduction*i], histogram[0][self.reduction*i])
        self.chart.removeAllSeries()
        self.chart.addSeries(series)

class FftDistributionPlot(QtCharts.QtCharts.QChartView):

    def __init__(self):
        super().__init__()

        self.reduction = 8

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('FFT Distribution')

        self.chart = QtCharts.QtCharts.QChart()
        self.setChart(self.chart)

    def updateFrame(self, semImage):
        fft = semImage.fft().clip(0, 65535).astype('uint16')
        binEdges = numpy.arange(65537)
        fftDistribution = numpy.histogram(fft, bins=binEdges)
        series = QtCharts.QtCharts.QLineSeries()
        for i in range(round(65536 / self.reduction)):
            series.append(fftDistribution[1][self.reduction*i], fftDistribution[0][self.reduction*i])
        self.chart.removeAllSeries()
        self.chart.addSeries(series)

class SemImageGui(QtWidgets.QWidget):
    
    def __init__(self, semController):
        super().__init__()

        self.sem = semController

        self.setMinimumSize(320, 240)
        self.setWindowTitle('SemImage')

        self.initImageSourceForm()
        self.initPlotsForm()

    def initImageSourceForm(self):
        self.localImage = None
        self.localImagePath = QtWidgets.QLabel('...')
        self.useLocalImage = QtWidgets.QCheckBox()
        self.browseButton = QtWidgets.QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseForLocalImage)

    def initPlotsForm(self):
        self.imagePlotOn = QtWidgets.QCheckBox()
        self.fftPlotOn = QtWidgets.QCheckBox()
        self.histogramPlotOn = QtWidgets.QCheckBox()
        self.fftDistributionPlotOn = QtWidgets.QCheckBox()

        self.imagePlot = ImagePlot()
        self.fftPlot = FftPlot()
        self.histogramPlot = HistogramPlot()
        self.fftDistributionPlot = FftDistributionPlot()

        self.updateButton = QtWidgets.QPushButton('Update')
        self.updateButton.clicked.connect(self.update)

    def update(self):
        if self.useLocalImage.isChecked():
            if self.localImage is None:
                self.browseForLocalImage()
            image = self.localImage
        else:
            image = self.sem.grabImage()

        if self.imagePlotOn.isChecked():
            self.imagePlot.updateFrame(image)
        if self.fftPlotOn.isChecked():
            self.fftPlot.updateFrame(image)
        if self.histogramPlotOn.isChecked():
            self.histogramPlot.updateFrame(image)
        if self.fftDistributionPlotOn.isChecked():
            self.fftDistributionPlot.updateFrame(image)

    def browseForLocalImage(self):
        imagePath = QtWidgets.QFileDialog.getOpenFileName()[0]
        if imagePath:
            self.localImagePath.setText(imagePath)
        self.localImage = SemImage(Image.open(imagePath))
