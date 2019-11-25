#   File:   SEMTool.py
#
#   Brief:  Implement the SEM realtime diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2019

import sys
import time
import SEM_API
import numpy as np
from PIL import Image
from PIL import ImageQt
from imageio import imread
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from matplotlib.colors import LogNorm 
from matplotlib.figure import Figure as MPLFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MPLCanvas

class SEMTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.SEMImage   = Image.Image()
        self.canvas     = MPLCanvas(MPLFigure(constrained_layout=True))

        self.initCanvas()

        self.setCentralWidget(self.canvas)
        self.setWindowTitle("SEM Realtime Diagnostic Tool")

    def initCanvas(self):
        plots = self.canvas.figure.subplots(nrows=2, ncols=2)

        self.image      = plots[0, 0]
        self.imageXYFFT = plots[0, 1]
        self.imageXFFT  = plots[1, 0]
        self.imageYFFT  = plots[1, 1]

        self.image.axis('off')
        self.imageXYFFT.axis('off')
        self.imageXFFT.axis('off')
        self.imageYFFT.axis('off')

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()

        with SEM_API.SEM_API("remote") as sem:
            sem.UpdateImage_Start()
            time.sleep(1)
            sem.UpdateImage_Pause()
            self.array = np.asarray(sem.img_array)
            
        self.arrayXYFFT = np.fft.fft2(self.array)
        self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
        self.arrayXYFFT = np.abs(self.arrayXYFFT)

        self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)

        self.img        = self.image.imshow(self.SEMImage, cmap = 'gray')
        self.imgYFFT    = self.imageYFFT.imshow(self.arrayXYFFT, norm = LogNorm())
        self.imgXYFFT   = self.imageXYFFT.imshow(self.arrayXYFFT, norm = LogNorm())

        self.updateImage()

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(100)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            with SEM_API.SEM_API("remote") as sem:
                sem.UpdateImage_Start()
                time.sleep(1)
                sem.UpdateImage_Pause()
                self.array      = np.asarray(sem.img_array)

            self.array      = np.asarray(self.SEMImage)
            self.arrayXYFFT = np.fft.fft2(self.array)
            self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
            self.arrayXYFFT = np.abs(self.arrayXYFFT)

            self.imageXFFT.clear()
            self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)

            self.img.set_data(self.SEMImage)
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
    app = QtWidgets.QApplication([])
    gui = SEMTool()
    gui.show()
    sys.exit(app.exec_())
