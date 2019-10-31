#   File:   SEMTool.py
#
#   Brief:  Implement the SEM realtime diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2019

import sys
import time
import numpy as np
from PIL import Image
from PIL import ImageQt
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SEMTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.PILImage   = Image.open("../SEM Images/Armin241.tif")
        self.image      = QtWidgets.QLabel()
        self.imageXFFT  = QtWidgets.QLabel()
        self.imageYFFT  = QtWidgets.QLabel()
        self.imageXYFFT = QtWidgets.QLabel()
        self.panel      = QtWidgets.QDockWidget()
        self.count = 0

        self.updateImage()
        self.updateImageXFFT()
        self.updateImageYFFT()
        self.updateImageXYFFT()
        self.initPanel()

        self.setWindowTitle("SEM Realtime Diagnostic Tool")
        self.setCentralWidget(self.imageXYFFT)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateImage)
        self.timer.start(1000)

    def initPanel(self):
        self.panel.setWindowTitle("Control Panel")
        self.panel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | 
                                   QtCore.Qt.LeftDockWidgetArea)

    def updateImage(self):
        begin = time.time()
        if self.count == 0:
            self.PILImage = Image.open("../SEM Images/Armin241.tif")
            self.count = 1
        elif self.count == 1:
            self.PILImage = Image.open("../SEM Images/Armin242.tif")
            self.count = 0
        qtImage     = ImageQt.ImageQt(self.PILImage)
        qtPixmap    = QtGui.QPixmap.fromImage(qtImage)
        self.image.setPixmap(qtPixmap)
        self.updateImageXFFT()
        self.updateImageYFFT()
        self.updateImageXYFFT()
        end = time.time()
        print(end - begin)

    def updateImageXFFT(self):
        pass

    def updateImageYFFT(self):
        pass

    def updateImageXYFFT(self):
        array       = np.asarray(self.PILImage)
        arrayFFT    = np.fft.fft2(array)
        arrayFFT    = np.fft.fftshift(arrayFFT)
        arrayFFT    = np.abs(arrayFFT)
        arrayFFT    = np.log(arrayFFT)
        arrayFFT    = arrayFFT / np.max(arrayFFT)
        arrayFFT    = 255 * arrayFFT
        arrayFFT    = np.require(arrayFFT, np.uint8, 'C')
        qtImage     = QtGui.QImage(arrayFFT.data, 
                                   arrayFFT.shape[1],
                                   arrayFFT.shape[0],
                                   QtGui.QImage.Format_Indexed8)
        qtPixmap    = QtGui.QPixmap.fromImage(qtImage)
        self.imageXYFFT.setPixmap(qtPixmap)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = SEMTool()
    gui.show()
    sys.exit(app.exec_())