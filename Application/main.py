#   File:   main.py
#
#   Brief:  Implement the SEM real-time diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2019

import sys
import time
import SEM_API
import numpy as np
from PIL import Image
from PIL import ImageQt
from imageio import imread
# from PySide2 import QtGui
# from PySide2 import QtCore
# from PySide2 import QtWidgets
from qtpy import QtGui
from qtpy import QtCore
from qtpy import QtWidgets
from matplotlib.colors import LogNorm 
from matplotlib.figure import Figure as MPLFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MPLCanvas

class semTool(QtWidgets.QMainWindow):
    def __init__(self, sem):
        super().__init__()

        sem.UpdateImage_Start()

        self.semImage   = Image.Image()
        self.canvas     = MPLCanvas(MPLFigure(constrained_layout=True))

        self.initCanvas()

        self.setCentralWidget(self.canvas)
        self.setWindowTitle("SEM Realtime Diagnostic Tool")

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

        # self.image.set_title("Original Image")
        # self.imageXYFFT.set_title("2D FFT")
        # self.imageXFFT.set_title("X-Axis FFT")
        # self.imageYFFT.set_title("Y-Axis FFT")

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()

        # self.semImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
        # self.array      = np.asarray(self.semImage)
        self.array = np.asarray(sem.img_array)
        self.arrayXYFFT = np.fft.fft2(self.array)
        self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
        self.arrayXYFFT = np.abs(self.arrayXYFFT)

        self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)

        self.img        = self.image.imshow(self.array, cmap = 'gray')
        # self.imgXFFT    = self.imageXFFT.imshow(self.arrayXYFFT, norm = LogNorm())
        self.imgYFFT    = self.imageYFFT.imshow(self.arrayXYFFT, norm = LogNorm())
        self.imgXYFFT   = self.imageXYFFT.imshow(self.arrayXYFFT, norm = LogNorm())

        self.updateImage()

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(100)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            # self.semImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
            # self.array      = np.asarray(self.semImage)
            self.array = np.asarray(sem.img_array)
            self.arrayXYFFT = np.fft.fft2(self.array)
            self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
            self.arrayXYFFT = np.abs(self.arrayXYFFT)

            # self.imageXYFFT.set_xlim(-1000, 1000)
            # self.imageXYFFT.set_ylim(-1000, 1000)

            self.imageXFFT.clear()
            self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)

            self.img.set_data(self.array)
            # self.imgXFFT.set_data(self.arrayXYFFT)
            self.imgYFFT.set_data(self.arrayXYFFT)
            self.imgXYFFT.set_data(self.arrayXYFFT)

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
    with SEM_API.SEM_API("remote") as sem:
        app = QtWidgets.QApplication([])
        gui = semTool(sem)
        gui.show()
        sys.exit(app.exec_())