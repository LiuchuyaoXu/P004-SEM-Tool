# File:     SemImageViewer.py
#
# Author:   Liuchuyao Xu, 2020

import os
from functools import partial
from PIL import Image
from PySide2 import QtCharts
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from SemImage import SemImage

class SemImageViewer(QtWidgets.QWidget):

    _updated = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.sem = None
        self._image = None
        self.continuouslyUpdating = False

        self.usingLocalImages = True
        self._localImages = None
        self._localImagesIndex = 0
        self.localImagesFolder = '...'

        self.imagePlotOn = True
        self.fftPlotOn = False
        self.histogramPlotOn = False

        self.imagePlot = ImagePlot()
        self.imagePlot.closed.connect(partial(setattr, self, 'imagePlotOn', False))
        self.fftPlot = FftPlot()
        self.fftPlot.closed.connect(partial(setattr, self, 'fftPlotOn', False))
        self.histogramPlot = HistogramPlot()
        self.histogramPlot.closed.connect(partial(setattr, self, 'histogramPlotOn', False))

        self._updated.connect(self.grabAndUpdate, QtCore.Qt.QueuedConnection)

    def grabAndUpdate(self):
        self.grabImage()
        self.updatePlots()
        if self.continuouslyUpdating:
            self._updated.emit()

    def grabImage(self):
        if self.usingLocalImages:
            if self._localImages is None:
                print('SemImageViewer: no local images.')
                return
            if self._localImagesIndex >= len(self._localImages):
                self._localImagesIndex = 0
            path = os.path.join(self.localImagesFolder, self._localImages[self._localImagesIndex])
            self._image = SemImage(Image.open(path))
            self._localImagesIndex += 1
        else:
            if self.sem is None:
                print('SemImageViewer: no SEM.')
                return
            self._image = SemImage(self.sem.grabImage())

    def updatePlots(self):
        if self._image is None:
            print('SemImageViewer: no image.')
            return
        if self.imagePlotOn:
            self.imagePlot.updateFrame(self._image)
            self.imagePlot.show()
        if self.fftPlotOn:
            self.fftPlot.updateFrame(self._image)
            self.fftPlot.show()
        if self.histogramPlotOn:
            self.histogramPlot.updateFrame(self._image)
            self.histogramPlot.show()

    def guiUpdatePlots(self):
        self.updatePlots()

    def guiUpdatePlotsContinuously(self):
        if not self.continuouslyUpdating:
            self.continuouslyUpdating = True
            self._updated.emit()
        else:
            self.continuouslyUpdating = False

    def guiBrowseForLocalImage(self):
        if self.continuouslyUpdating:
            print('SemImageViewer: stop the continuous updating first.')
            return
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        if path:
            image = Image.open(path)
            self._image = SemImage(image)
            self.updatePlots()

    def guiBrowseForLocalImagesFolder(self):
        if self.continuouslyUpdating:
            print('SemImageViewer: stop the continuous updating first.')
            return
        path = QtWidgets.QFileDialog.getExistingDirectory()
        if path:
            self._localImages = QtCore.QDir(path).entryList(['*.tif'])
            self._localImagesIndex = 0
            self.localImagesFolder = path

    def closeEvent(self, event):
        self.imagePlot.destroy()
        self.fftPlot.destroy()
        self.histogramPlot.destroy()
        event.accept()

class ImagePlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('Image')

    def updateFrame(self, semImage):
        image = semImage.image()
        width = image.shape[1]
        height = image.shape[0]
        qtImage = QtGui.QImage(image, width, height, QtGui.QImage.Format_Grayscale8)
        qtPixmap = QtGui.QPixmap(qtImage)
        self.setPixmap(qtPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio))

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class FftPlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(512, 384)
        self.setWindowTitle('FFT')

    def updateFrame(self, semImage):
        fft = semImage.fft().clip(0, 65535).astype('uint16')
        width = fft.shape[1]
        height = fft.shape[0]
        qtImage = QtGui.QImage(fft, width, height, QtGui.QImage.Format_Grayscale16)
        qtPixmap = QtGui.QPixmap(qtImage)
        self.setPixmap(qtPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio))

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class HistogramPlot(QtCharts.QtCharts.QChartView):
    closed = QtCore.Signal()

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

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

if __name__ == '__main__':
    from ObjectInspector import ObjectInspector

    app = QtWidgets.QApplication()
    gui = ObjectInspector(SemImageViewer())
    gui.show()
    app.exec_()
