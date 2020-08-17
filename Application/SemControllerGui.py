# File:     SemControllerGui.py
#
# Author:   Liuchuyao Xu, 2020

import time
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SemControllerGui(QtWidgets.QWidget):

    def __init__(self, semController):
        super().__init__()

        self.semController = semController
        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)

        self.setMinimumSize(320, 240)
        self.setWindowTitle('SemController')

        self.initGrabImageForm()

    def initGrabImageForm(self):
        validator = QtGui.QIntValidator()
        self.imageX = QtWidgets.QLineEdit('0')
        self.imageX.setValidator(validator)
        self.imageY = QtWidgets.QLineEdit('0')
        self.imageY.setValidator(validator)
        self.imageWidth = QtWidgets.QLineEdit('1024')
        self.imageWidth.setValidator(validator)
        self.imageHeight = QtWidgets.QLineEdit('768')
        self.imageHeight.setValidator(validator)
        self.imageReduction = QtWidgets.QLineEdit('0')
        self.imageReduction.setValidator(validator)

        self.numberOfImagesToGrab = QtWidgets.QLineEdit('1')
        self.numberOfImagesToGrab.setValidator(validator)

        self.imageSaveFolder = QtWidgets.QLabel('...')
        self.imageSaveFolder.setWordWrap(True)
        browseButton = QtWidgets.QPushButton('Folder to save images in')
        browseButton.clicked.connect(self.updateImageSaveFolder)

        grabImageButton = QtWidgets.QPushButton('Grab Image')
        grabImageButton.clicked.connect(self.grabImages)

        layout = QtWidgets.QFormLayout()
        layout.addRow('Image x', self.imageX)
        layout.addRow('Image y', self.imageY)
        layout.addRow('Image width', self.imageWidth)
        layout.addRow('Image height', self.imageHeight)
        layout.addRow('Image reduction', self.imageReduction)
        layout.addRow('Number of images to grab', self.numberOfImagesToGrab)
        layout.addRow(browseButton, self.imageSaveFolder)
        layout.addRow(grabImageButton)

        grabImageForm = QtWidgets.QGroupBox('Grab Images')
        grabImageForm.setLayout(layout)
        self.layout.addWidget(grabImageForm)

    def updateImageSaveFolder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder:
            self.imageSaveFolder.setText(folder)

    def grabImages(self):
        path = self.imageSaveFolder.text()
        if path == '...':
            print('Error, SemController: please specify a folder to save images in.')
            return
        for i in range(int(self.numberOfImagesToGrab.text())):
            x = int(self.imageX.text())
            y = int(self.imageY.text())
            width = int(self.imageWidth.text())
            height = int(self.imageHeight.text())
            reduction = int(self.imageReduction.text())
            filename = '/{} {}.png'.format(time.asctime(), i + 1)
            filepath = path.join(filename)
            image = self.semController.grabImage(x, y, width, height, reduction)
            image.save(filepath)

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    semc = SemControllerGui(None)
    semc.show()
    sys.exit(app.exec_())
