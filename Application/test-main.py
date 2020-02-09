import sys
import time
import numpy as np
import numpy.ma as ma
from PIL import Image
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.colors import LogNorm as MplLogNorm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

# Divides the 2d shape into 8 non-overlapping regions by angle.
class Masker:
    def __init__(self, shape):
        self.r1 = np.ones(shape)
        self.r2 = np.ones(shape)
        self.r3 = np.ones(shape)
        self.r4 = np.ones(shape)
        self.s1 = np.ones(shape)
        self.s2 = np.ones(shape)
        self.s3 = np.ones(shape)
        self.s4 = np.ones(shape)

        xLen = shape[0]
        yLen = shape[1]
        xOri = np.floor(xLen / 2)
        yOri = np.floor(yLen / 2)
        for i in range(0, xLen):
            for j in range(0, yLen):
                x = i - xOri
                y = j - yOri
                if x == 0:
                    if y == 0:
                        pass
                    elif y > 0:
                        self.r1[i][j] = 0
                    else:
                        self.r3[i][j] = 0
                elif x > 0:
                    if y == 0:
                        self.r4[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r3[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s3[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r4[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s4[i][j] = 0
                        else:
                            self.r1[i][j] = 0
                else:
                    if y == 0:
                        self.r2[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r1[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s1[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r2[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s2[i][j] = 0
                        else:
                            self.r3[i][j] = 0

# Each SemImage represents a 8-bit grey-level image.
class SemImage(np.ndarray):
    def __array_finalize__(self, obj):
        self.fft            = None
        self.fftSegments    = None
        self.hist           = None
        self.histEqualised  = None

    def getFft(self):
        if self.fft is not None:
            return self.fft

        fft = np.fft.fft2(self)
        fft = np.fft.fftshift(fft)
        fft = np.abs(fft)

        self.fft = fft
        return self.fft

    def getFftSegments(self, masker):
        if self.fftSegments is not None:
            return self.fftSegments
        if self.fft is None:
            self.getFft()

        r1 = ma.array(self.fft, mask=masker.r1).sum()
        r2 = ma.array(self.fft, mask=masker.r2).sum()
        r3 = ma.array(self.fft, mask=masker.r3).sum()
        r4 = ma.array(self.fft, mask=masker.r4).sum()
        s1 = ma.array(self.fft, mask=masker.s1).sum()
        s2 = ma.array(self.fft, mask=masker.s2).sum()
        s3 = ma.array(self.fft, mask=masker.s3).sum()
        s4 = ma.array(self.fft, mask=masker.s4).sum()

        self.fftSegments = np.array([r1, r2, r3, r4, s1, s2, s3, s4])
        return self.fftSegments

    def getHist(self):
        if self.hist is not None:
            return self.hist

        self.hist = np.histogram(self, bins=np.arange(257))
        return self.hist

    def getHistEqualised(self):
        if self.histEqualised is not None:
            return self.histEqualised
        if self.hist is None:
            self.getHist()

        hist        = self.hist[0] 
        histTrans   = np.zeros(256)
        numPixels   = np.sum(hist)

        total = 0
        for i in range(0, 256):
            total += hist[i]
            histTrans[i] = total
        histTrans /= numPixels
        histTrans *= 255 / histTrans.max()
        histTrans = histTrans.astype(int)    

        newImage = np.zeros(self.shape)
        newImage = newImage.astype(int)
        for i in range(0, self.shape[0]):
            for j in range(0, self.shape[1]):
                newImage[i, j] = histTrans[self[i, j]]

        self.histEqualised = newImage.view(SemImage)
        return self.histEqualised

class SemTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        





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

        self.semImage   = Image.open("Images from SEM/Armin24%d.tif" % self.frameCount)
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

            self.semImage   = Image.open("Images from SEM/Armin24%d.tif" % self.frameCount)
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