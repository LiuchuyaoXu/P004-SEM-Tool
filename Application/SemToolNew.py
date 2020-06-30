#   File:   SemTool.py
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement classes related to the GUI of the SEM diagnostic tool.

import sys
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SemTool(QtWidgets.QWidget):
    frameUpdated = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setMinimumSize(320, 240)
        self.setWindowTitle('SEM Real-time Diagnostic Tool')

        self.initImageSourceBox()
        self.initProcessingAlgorithmsBox()
        self.initPlotsBox()

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        layout.insertWidget(0, self.imageSourceBox)
        layout.insertWidget(1, self.processingAlgorithmsBox)
        layout.insertWidget(2, self.plotsBox)

        self.frameUpdated.connect(self.updateFrame, QtCore.Qt.QueuedConnection)
        self.updateFrame()

    def initImageSourceBox(self):
        self.imageSourceBox = QtWidgets.QGroupBox('Image Source')

        folderButton = QtWidgets.QRadioButton('Local Folder')
        folderButton.setChecked(True)
        folderButton.toggled.connect(self.onSelectFolderAsImageSource)
        semButton = QtWidgets.QRadioButton('SEM')
        semButton.toggled.connect(self.onSelectSemAsImageSource)

        self.browseButton = QtWidgets.QPushButton('Browse')
        self.browseButton.clicked.connect(self.browseForImageFolder)
        self.folderText = QtWidgets.QLabel('...')
        self.folderText.setWordWrap(True)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(folderButton, 0, 0)
        layout.addWidget(semButton, 0, 1)
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

        imageBox = QtWidgets.QCheckBox('Image')
        fftBox = QtWidgets.QCheckBox('FFT')
        fftDistributionBox = QtWidgets.QCheckBox('FFT Distribution')
        histogramBox = QtWidgets.QCheckBox('Histogram')
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(imageBox, 0, 0)
        layout.addWidget(histogramBox, 0, 1)
        layout.addWidget(fftBox, 1, 0)
        layout.addWidget(fftDistributionBox, 1, 1)
        self.plotsBox.setLayout(layout)

    def browseForImageFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.folderText.setText(folder)
        self.localImageFolder = QtCore.QDir(folder)
        self.localImages = self.localImageFolder.entryList()
        self.localImagesIndex = 0

    def onSelectFolderAsImageSource(self, checked):
        if checked:
            self.browseButton.setEnabled(True)
            self.folderText.setEnabled(True)

    def onSelectSemAsImageSource(self, checked):
        if checked:
            self.browseButton.setEnabled(False)
            self.folderText.setEnabled(False)

    def updateFrame(self):
        self.frameUpdated.emit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = SemTool()
    gui.show()
    sys.exit(app.exec_())
