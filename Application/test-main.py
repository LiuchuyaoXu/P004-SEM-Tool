import sys
import time
import numpy as np
from PIL import Image
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.colors import LogNorm as MplLogNorm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

class semTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.semImage   = Image.Image()
        self.canvas     = MplCanvas(MplFigure(constrained_layout=True))

        self.initCanvas()

        self.setCentralWidget(self.canvas)
        self.setWindowTitle("SEM Real-time Diagnostic Tool")

    def get_histogram(self, image, bins):
        # array with size of bins, set to zeros
        histogram = np.zeros(bins)
        
        # loop through pixels and sum up counts of pixels
        for pixel in image:
            histogram[pixel] += 1
        
        # return our final result
        return histogram

    def cumsum(self, a):
        a = iter(a)
        b = [next(a)]
        for i in a:
            b.append(b[-1] + i)
        return np.array(b)

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

        self.semImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
        self.array      = np.asarray(self.semImage)
        self.arrayXYFFT = np.fft.fft2(self.array)
        self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
        self.arrayXYFFT = np.abs(self.arrayXYFFT)

        self.arrayFlat  = self.array.flatten()
        hist            = self.get_histogram(self.arrayFlat, 256)
        cs              = self.cumsum(hist)
        nj              = (cs - cs.min()) * 255
        N               = cs.max() - cs.min()
        cs              = nj / N
        cs              = cs.astype('uint8')
        self.arrayNew   = cs[self.arrayFlat]
        self.arrayNew   = np.reshape(self.arrayNew, self.array.shape)

        self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)

        self.img        = self.image.imshow(self.array, cmap = 'gray')
        # self.imgXFFT    = self.imageXFFT.imshow(self.arrayXYFFT, norm = MplLogNorm())
        self.imgYFFT   = self.imageYFFT.imshow(self.arrayXYFFT, norm = MplLogNorm())
        self.imgXYFFT    = self.imageXYFFT.imshow(self.arrayNew, cmap='gray')

        self.updateImage()

        self.frameTimer.timeout.connect(self.updateImage)
        self.frameTimer.start(100)

    def updateImage(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            self.semImage   = Image.open("../SEM Images/Armin24%d.tif" % self.frameCount)
            self.array      = np.asarray(self.semImage)
            self.arrayXYFFT = np.fft.fft2(self.array)
            self.arrayXYFFT = np.fft.fftshift(self.arrayXYFFT)
            self.arrayXYFFT = np.abs(self.arrayXYFFT)

            self.arrayFlat  = self.array.flatten()
            hist            = self.get_histogram(self.arrayFlat, 256)
            cs              = self.cumsum(hist)
            nj              = (cs - cs.min()) * 255
            N               = cs.max() - cs.min()
            cs              = nj / N
            cs              = cs.astype('uint8')
            self.arrayNew   = cs[self.arrayFlat]
            self.arrayNew   = np.reshape(self.arrayNew, self.array.shape)

            # self.imageXYFFT.set_xlim(-1000, 1000)
            # self.imageXYFFT.set_ylim(-1000, 1000)

            begin = time.time()
            self.imageXFFT.clear()
            self.imageXFFT.hist(np.matrix.flatten(self.array), bins=10)
            end = time.time()
            print(end - begin)

            self.img.set_data(self.array)
            # self.imgXFFT.set_data(self.arrayXYFFT)
            self.imgYFFT.set_data(self.arrayXYFFT)
            self.imgXYFFT.set_data(self.arrayNew)

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
    gui = semTool()
    gui.show()
    sys.exit(app.exec_())