#   File:   main.py
#
#   Brief:  Implement the SEM real-time diagnostic tool.
# 
#   Author: Liuchuyao Xu, 2019

import sys
import time
import numpy as np
import numpy.ma as ma
from PIL import Image
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from matplotlib.figure import Figure as MplFigure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as MplCanvas

try:
    import cupy as cp
except:
    CUDA_ENABLED = False
    print("Could not import cupy, CUDA acceleration will be disabled.")
else:
    CUDA_ENABLED = True
    print("Successfully imported cupy, CUDA acceleration will be enabled.")

try:
    import SEM_API
except:
    TESTING_MODE = True
    print("Could not import SEM_API, running in testing mode, SEM images will be read from local folder.")
else:
    TESTING_MODE = False
    print("Successfully imported SEM_API, running in normal mode, SEM images will be read from the SEM.")

# Each SemImage represents an 8-bit grey-level image.
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
        newImage  = np.array(list(map(lambda x: histTrans[x], self)))

        self.histEqualised = newImage.view(SemImage)
        return self.histEqualised
