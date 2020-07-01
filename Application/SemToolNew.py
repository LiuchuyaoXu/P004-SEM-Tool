#   File:   SemTool.py
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement classes related to the GUI of the SEM diagnostic tool.

import os
import sys
from PIL import Image
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from SemImage import SemImage
from SemController import SemController

class ImagePlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Image')

    def update(self, semImage):
        width = semImage.image.shape[1]
        height = semImage.image.shape[0]
        image = QtGui.QImage(semImage.image, width, height, QtGui.QImage.Format_Grayscale8)
        self.setPixmap(QtGui.QPixmap(image))

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class HistogramPlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Histogram')

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()
    
class FftPlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('FFT')

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class FftDistributionPlot(QtWidgets.QLabel):
    closed = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle('FFT Distribution')

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()

class SemTool(QtWidgets.QWidget):
    localImageFolder = None
    
    frameUpdated = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setMinimumSize(320, 240)
        self.setWindowTitle('SEM Real-time Diagnostic Tool')

        self.initImageSourceBox()
        self.initProcessingAlgorithmsBox()
        self.initPlotsBox()
        self.initCommandBox()

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        layout.insertWidget(0, self.imageSourceBox)
        layout.insertWidget(1, self.processingAlgorithmsBox)
        layout.insertWidget(2, self.plotsBox)
        layout.insertWidget(3, self.commandBox)

        self.imagePlot = ImagePlot()
        self.imagePlot.closed.connect(self.onImagePlotClose)
        self.histogramPlot = HistogramPlot()
        self.histogramPlot.closed.connect(self.onHistogramPlotClose)
        self.fftPlot = FftPlot()
        self.fftPlot.closed.connect(self.onFftPlotClose)
        self.fftDistributionPlot = FftDistributionPlot()
        self.fftDistributionPlot.closed.connect(self.onFftDistributionPlotClose)

        try:
            self.sem = SemController()
        except:
            self.semButton.setEnabled(False)
            print('Could not initialise communication with the SEM, using it as the image source will not be available.')

    def initImageSourceBox(self):
        self.imageSourceBox = QtWidgets.QGroupBox('Image Source')

        self.folderButton = QtWidgets.QRadioButton('Local Folder')
        self.folderButton.setChecked(True)
        self.folderButton.toggled.connect(self.onSelectFolderAsImageSource)
        self.semButton = QtWidgets.QRadioButton('SEM')
        self.semButton.toggled.connect(self.onSelectSemAsImageSource)

        self.browseButton = QtWidgets.QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseForImageFolder)
        self.folderText = QtWidgets.QLabel('...')
        self.folderText.setWordWrap(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.folderButton, 0, 0)
        layout.addWidget(self.semButton, 0, 1)
        layout.addWidget(self.browseButton, 1, 0)
        layout.addWidget(self.folderText, 1, 1)
        self.imageSourceBox.setLayout(layout)

    def initProcessingAlgorithmsBox(self):
        self.processingAlgorithmsBox = QtWidgets.QGroupBox('Image Processing Algorithms')

        hannWindowBox = QtWidgets.QCheckBox('Hann Window')
        histogramEqualisationBox = QtWidgets.QCheckBox('Histogram Equalisation')

        layout = QtWidgets.QGridLayout()
        layout.addWidget(hannWindowBox, 0, 0)
        layout.addWidget(histogramEqualisationBox, 0, 1)
        self.processingAlgorithmsBox.setLayout(layout)

    def initPlotsBox(self):
        self.plotsBox = QtWidgets.QGroupBox('Plots')

        self.imageBox = QtWidgets.QCheckBox('Image')
        self.imageBox.stateChanged.connect(self.onImageBoxToggle)
        self.fftBox = QtWidgets.QCheckBox('FFT')
        self.fftBox.stateChanged.connect(self.onFftBoxToggle)
        self.fftDistributionBox = QtWidgets.QCheckBox('FFT Distribution')
        self.fftDistributionBox.stateChanged.connect(self.onFftDistributionBoxToggle)
        self.histogramBox = QtWidgets.QCheckBox('Histogram')
        self.histogramBox.stateChanged.connect(self.onHistogramBoxToggle)
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.imageBox, 0, 0)
        layout.addWidget(self.histogramBox, 0, 1)
        layout.addWidget(self.fftBox, 1, 0)
        layout.addWidget(self.fftDistributionBox, 1, 1)
        self.plotsBox.setLayout(layout)

    def initCommandBox(self):
        self.commandBox = QtWidgets.QGroupBox('')

        self.toggleFrameUpdateButton = QtWidgets.QPushButton('Start Updating Frames')
        self.toggleFrameUpdateButton.clicked.connect(self.startFrameUpdate)
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.toggleFrameUpdateButton, 0, 0, alignment=QtCore.Qt.AlignCenter)
        self.commandBox.setLayout(layout)

    def browseForImageFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder:
            self.folderText.setText(folder)
            self.localImageFolder = QtCore.QDir(folder)
            self.localImages = self.localImageFolder.entryList(['*.tif'])
            self.localImagesIndex = 0

    def onSelectFolderAsImageSource(self, checked):
        if checked:
            self.browseButton.setEnabled(True)
            self.folderText.setEnabled(True)

    def onSelectSemAsImageSource(self, checked):
        if checked:
            self.browseButton.setEnabled(False)
            self.folderText.setEnabled(False)

    def onImageBoxToggle(self, checked):
        if checked:
            self.imagePlot.show()
        else:
            self.imagePlot.hide()

    def onHistogramBoxToggle(self, checked):
        if checked:
            self.histogramPlot.show()
        else:
            self.histogramPlot.hide()
    
    def onFftBoxToggle(self, checked):
        if checked:
            self.fftPlot.show()
        else:
            self.fftPlot.hide()

    def onFftDistributionBoxToggle(self, checked):
        if checked:
            self.fftDistributionPlot.show()
        else:
            self.fftDistributionPlot.hide()

    def onImagePlotClose(self):
        self.imageBox.setChecked(False)

    def onHistogramPlotClose(self):
        self.histogramBox.setChecked(False)

    def onFftPlotClose(self):
        self.fftBox.setChecked(False)

    def onFftDistributionPlotClose(self):
        self.fftDistributionBox.setChecked(False)

    def startFrameUpdate(self):
        if not self.localImageFolder:
            print('Please specify the local folder.')
            return

        self.imageSourceBox.setEnabled(False)
        self.toggleFrameUpdateButton.setText('Stop Updating Frames')
        self.toggleFrameUpdateButton.clicked.disconnect(self.startFrameUpdate)
        self.toggleFrameUpdateButton.clicked.connect(self.stopFrameUpdate)
        self.frameUpdated.connect(self.updateFrame, QtCore.Qt.QueuedConnection)
        self.updateFrame()

    def stopFrameUpdate(self):
        self.imageSourceBox.setEnabled(True)
        self.toggleFrameUpdateButton.setText('Start Updating Frames')
        self.toggleFrameUpdateButton.clicked.disconnect(self.stopFrameUpdate)
        self.toggleFrameUpdateButton.clicked.connect(self.startFrameUpdate)
        self.frameUpdated.disconnect(self.updateFrame)

    def updateFrame(self):
        if self.folderButton.isChecked():
            path = os.path.join(self.localImageFolder.path(), self.localImages[self.localImagesIndex])
            image = SemImage.create(Image.open(path))
            self.localImagesIndex += 1
            if self.localImagesIndex >= len(self.localImages):
                self.localImagesIndex = 0
        else:
            image = SemImage.create(self.sem.grabImage())

        if self.imagePlot.isVisible():
            self.imagePlot.update(image)

        self.frameUpdated.emit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = SemTool()
    gui.show()
    sys.exit(app.exec_())
