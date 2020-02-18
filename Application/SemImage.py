#   File:   SemImage.py
#
#   Brief:  Implement a class for properties and methods related to SEM images.
# 
#   Author: Liuchuyao Xu, 2020

import numpy as np

try:
    import cupy as cp
except:
    print("Warning, could not import cupy, CUDA acceleration will be disabled.")

# Each SemImage represents an 8-bit grey-level image.
class SemImage:
    def __init__(self, arr):
        self._fft = None
        self._histogram = None

        self.array = arr

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, arr):
        arr = np.asarray(arr, int)
        if len(arr.shape) != 2:
            raise TypeError("SemImage was not initialised with a 2d array.")
        if arr.max() > 255 or arr.min() < 0:
            raise TypeError("SemImage was not initialised with a grey-level image.")
        self._array = arr
        self._calcFft()
        self._calcHist()

    @property
    def fft(self):
        return self._fft

    @property
    def histogram(self):
        return self._histogram

    def applyHamming(self):
        try:
            col = cp.hamming(self.array.shape[0])
            row = cp.hamming(self.array.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            arr = cp.multiply(window, cp.asarray(self.array))
            self.array = cp.asnumpy(arr)
        except:
            col = np.hamming(self.array.shape[0])
            row = np.hamming(self.array.shape[1])
            window = np.sqrt(np.outer(col, row))
            arr = np.multiply(window, self.array)
            self.array = arr

    def applyHanning(self):
        try:
            col = cp.hanning(self.array.shape[0])
            row = cp.hanning(self.array.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            arr = cp.multiply(window, cp.asarray(self.array))
            self.array = cp.asnumpy(arr)
        except:
            col = np.hanning(self.array.shape[0])
            row = np.hanning(self.array.shape[1])
            window = np.sqrt(np.outer(col, row))
            arr = np.multiply(window, self.array)
            self.array = arr

    def applyHistogramEqualisation(self):
        hist = self.histogram
        histTrans = np.zeros(256)
        numPixels = np.sum(hist)

        total = 0
        for i in range(0, 256):
            total += hist[i]
            histTrans[i] = total
        histTrans /= numPixels
        histTrans *= 255 / histTrans.max()
        histTrans = histTrans.astype(int)    
        arr = np.array(list(map(lambda x: histTrans[x], self.array)))
        self.array = arr

    def _calcFft(self):
        try:
            arr = cp.asarray(self.array)
            fft = cp.fft.fft2(arr)
            fft = cp.fft.fftshift(fft)
            fft = cp.abs(fft)
            self._fft = cp.asnumpy(fft)
        except:
            fft = np.fft.fft2(self.array)
            fft = np.fft.fftshift(fft)
            fft = np.abs(fft)
            self._fft = fft

    def _calcHist(self):
        try:
            arr = cp.asarray(self.array)
            hist = cp.histogram(arr, bins=cp.arange(257))
            self._histogram = cp.asnumpy(hist[0])
        except:
            hist = np.histogram(self.array, bins=np.arange(257))
            self._histogram = hist[0]
