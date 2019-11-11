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
from matplotlib.colors import LogNorm 
from matplotlib.figure import Figure as MPLFigure
from matplotlib.backends.backend_qt5agg import FigureCanvas as MPLCanvas

class SEMToolQt(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.panel          = QtWidgets.QDockWidget()
        self.canvas         = QtWidgets.QWidget()
        self.canvas.grid    = QtWidgets.QGridLayout()

        self.PILImage   = Image.Image()
        self.image      = QtWidgets.QLabel()
        self.imageXFFT  = QtWidgets.QLabel()
        self.imageYFFT  = QtWidgets.QLabel()
        self.imageXYFFT = QtWidgets.QLabel()

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()

        self.initCanvas()
        self.initPanel()

        self.setWindowTitle("SEM Realtime Diagnostic Tool")
        self.setCentralWidget(self.canvas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(100)

    def initCanvas(self):
        self.updateImage()
        self.canvas.setLayout(self.canvas.grid)
        self.canvas.grid.addWidget(self.image,      0, 0, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageXYFFT, 0, 1, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageXFFT,  1, 0, QtCore.Qt.AlignCenter)
        self.canvas.grid.addWidget(self.imageYFFT,  1, 1, QtCore.Qt.AlignCenter)

    def initPanel(self):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.panel)

        grid = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom)
        grid.addWidget(slider)

        self.panel.setLayout(grid)
        self.panel.setWindowTitle("Control Panel")
        self.panel.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            self.PILImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
            qtImage         = ImageQt.ImageQt(self.PILImage)
            qtPixmap        = QtGui.QPixmap.fromImage(qtImage)
            qtPixmap.setDevicePixelRatio(1.5)
            self.image.setPixmap(qtPixmap)
            
            self.updateImageXFFT()
            self.updateImageYFFT()
            self.updateImageXYFFT()

            self.frameCount += 1
            if self.frameCount == 7:
                self.frameCount = 1

            end = time.time()
            print(end - begin)
            self.frameReady = True
        else:
            pass

    def updateImageXFFT(self):
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
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageXFFT.setPixmap(qtPixmap)

    def updateImageYFFT(self):
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
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageYFFT.setPixmap(qtPixmap)

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
        qtPixmap.setDevicePixelRatio(1.5)
        self.imageXYFFT.setPixmap(qtPixmap)

class SEMToolMPL(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.SEMImage   = Image.Image()
        self.canvas     = MPLCanvas(MPLFigure(constrained_layout=True))

        self.initCanvas()

        self.setCentralWidget(self.canvas)

    def initCanvas(self):
        plots = self.canvas.figure.subplots(nrows=2, ncols=2)
        # self.canvas.figure.subplots_adjust(hspace=0, wspace=0)

        self.image      = plots[0, 0]
        self.imageXYFFT = plots[0, 1]
        self.imageXFFT  = plots[1, 0]
        self.imageYFFT  = plots[1, 1]

        self.image.axis('off')
        self.imageXYFFT.axis('off')
        self.imageXFFT.axis('off')
        self.imageYFFT.axis('off')

        self.image.set_title("Original Image")
        self.imageXYFFT.set_title("2D FFT")
        self.imageXFFT.set_title("X-Axis FFT")
        self.imageYFFT.set_title("Y-Axis FFT")

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()

        self.SEMImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
        self.array      = np.asarray(self.SEMImage)
        self.arrayXYFFT = np.fft.fft2(self.array)
        self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
        self.arrayXYFFT = np.abs(self.arrayXYFFT)
        self.img        = self.image.imshow(self.SEMImage, cmap = 'gray')
        self.imgXYFFT   = self.imageXYFFT.imshow(self.arrayXYFFT, norm = LogNorm())
        self.imgXFFT    = self.imageXFFT.imshow(self.arrayXYFFT, norm = LogNorm())
        self.imgYFFT    = self.imageYFFT.imshow(self.arrayXYFFT, norm = LogNorm())

        self.updateImage()

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(100)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            self.SEMImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)

            self.array      = np.asarray(self.SEMImage)
            self.arrayXYFFT = np.fft.fft2(self.array)
            self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
            self.arrayXYFFT = np.abs(self.arrayXYFFT)

            # self.imageXYFFT.set_xlim(-1000, 1000)
            # self.imageXYFFT.set_ylim(-1000, 1000)

            self.img.set_data(self.SEMImage)
            self.imgXYFFT.set_data(self.arrayXYFFT)
            self.imgXFFT.set_data(self.arrayXYFFT)
            self.imgYFFT.set_data(self.arrayXYFFT)
            self.canvas.figure.canvas.draw()

            self.frameCount += 1
            if self.frameCount == 7:
                self.frameCount = 1

            end = time.time()
            print(end - begin)
            self.frameReady = True
        else:
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = SEMToolMPL()
    gui.show()
    sys.exit(app.exec_())
