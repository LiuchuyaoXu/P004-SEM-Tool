import sys
import time
import cupy as cp
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

        image = cp.asarray(self)
        fft = cp.fft.fft2(image)
        fft = cp.fft.fftshift(fft)
        fft = cp.abs(fft)

        self.fft = cp.asnumpy(fft)
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

        hist = cp.histogram(cp.asarray(self), bins=cp.arange(257))
        self.hist = ([cp.asnumpy(hist[0]), cp.asnumpy(hist[1])])
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
        newImage  = np.array(list(map(lambda x: histTrans[x], self)))

        self.histEqualised = newImage.view(SemImage)
        return self.histEqualised

class SemTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.image  = None
        self.table  = QtWidgets.QTableWidget(9, 3)
        self.canvas = MplCanvas(MplFigure())

        self.dock1 = QtWidgets.QDockWidget()

        self.plots = self.canvas.figure.subplots(2, 3)
        self.imagePlot = None
        self.imageFftPlot = None
        self.imageHistPlot = None
        self.imageHistEqualisedPlot = None
        self.imageHistEqualisedFftPlot = None
        self.imageHistEqualisedHistPlot = None

        self.masker = None

        self.dock1.setWidget(self.table)

        self.setCentralWidget(self.canvas)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock1)
        self.setWindowTitle("SEM Real-time Diagnostic Tool")

        self.initTable()
        self.initCanvas()

        self.frameCount = 1
        self.frameReady = True
        self.frameTimer = QtCore.QTimer()
        self.frameTimer.timeout.connect(self.mainLoop)
        self.frameTimer.start(2000)

    def mainLoop(self):
        self.updateCanvas()
        self.updateTable()

    def initTable(self):
        for i in range(0, self.table.rowCount()):
            for j in range(1, self.table.columnCount()):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(""))
        self.table.setItem(1, 0, QtWidgets.QTableWidgetItem("r1"))
        self.table.setItem(2, 0, QtWidgets.QTableWidgetItem("r2"))
        self.table.setItem(3, 0, QtWidgets.QTableWidgetItem("r3"))
        self.table.setItem(4, 0, QtWidgets.QTableWidgetItem("r4"))
        self.table.setItem(5, 0, QtWidgets.QTableWidgetItem("s1"))
        self.table.setItem(6, 0, QtWidgets.QTableWidgetItem("s2"))
        self.table.setItem(7, 0, QtWidgets.QTableWidgetItem("s3"))
        self.table.setItem(8, 0, QtWidgets.QTableWidgetItem("s4"))

    def initCanvas(self):
        for row in self.plots:
            for plot in row:
                plot.axis("off")

        self.image = Image.open("Images from SEM/Armin241.tif")
        self.image = np.asarray(self.image)
        self.image = self.image.view(SemImage)

        self.masker = Masker(self.image.shape)

        self.imagePlot = self.plots[0][0].imshow(self.image, cmap="gray")
        self.imageFftPlot = self.plots[0][1].imshow(self.image.getFft(), cmap="gray", norm=MplLogNorm())
        self.imageHistPlot = self.plots[0][2].bar(self.image.getHist()[1][:-1], self.image.getHist()[0], width=1)
        self.imageHistEqualisedPlot = self.plots[1][0].imshow(self.image.getHistEqualised(), cmap="gray")
        self.imageHistEqualisedFftPlot = self.plots[1][1].imshow(self.image.getHistEqualised().getFft(), cmap="gray", norm=MplLogNorm())
        self.imageHistEqualisedHistPlot = self.plots[1][2].bar(self.image.getHistEqualised().getHist()[1][:-1], self.image.getHistEqualised().getHist()[0], width=1)

        self.canvas.figure.canvas.draw()

        self.image.getFftSegments(self.masker)
        self.image.getHistEqualised().getFftSegments(self.masker)

    def updateTable(self):
        for i in range(1, 9):
            self.table.item(i, 1).setText(str(int(self.image.fftSegments[i-1])))
            self.table.item(i, 2).setText(str(int(self.image.histEqualised.fftSegments[i-1])))

    def updateCanvas(self):
        if self.frameReady:
            self.frameReady = False
            begin = time.time()

            self.image = Image.open("Images from SEM/Armin24%d.tif" % self.frameCount)
            self.image = np.asarray(self.image)
            self.image = self.image.view(SemImage)

            self.imagePlot.set_data(self.image)
            self.imageFftPlot.set_data(self.image.getFft())
            for bar, h in zip(self.imageHistPlot, self.image.getHist()[0]):
                bar.set_height(h)
            self.imageHistEqualisedPlot.set_data(self.image.getHistEqualised())
            self.imageHistEqualisedFftPlot.set_data(self.image.getHistEqualised().getFft())
            for bar, h in zip(self.imageHistEqualisedHistPlot, self.image.getHistEqualised().getHist()[0]):
                bar.set_height(h)

            self.canvas.figure.canvas.draw()

            self.image.getFftSegments(self.masker)
            self.image.getHistEqualised().getFftSegments(self.masker)

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
    gui = SemTool()
    gui.show()
    sys.exit(app.exec_())
