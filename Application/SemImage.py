#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement the SemImage class, each SemImage encapsulates all data and methods relevant to an 8-bit greyscale image.

import time
import numpy as np

try:
    import cupy as cp
except:
    print("Warning, could not import cupy, GPU acceleration will be disabled.")

class SemImage:
    def __init__(self, array):
        self._fft = None
        self._histogram = None

        self.array = array
        self.updateAll()

    @property
    def array(self):
        return self._array

    @array.setter
    def array(self, array):
        array = np.asarray(array, int)
        if len(array.shape) != 2:
            raise TypeError("SemImage was initialised with a wrong data type.")
        if array.max() > 255 or array.min() < 0:
            raise TypeError("SemImage was initialised with a wrong data type.")
        self._array = array

    @property
    def fft(self):
        return self._fft

    @property
    def histogram(self):
        return self._histogram

    def applyHamming(self, updateAll=True):
        try:
            col = cp.hamming(self.array.shape[0])
            row = cp.hamming(self.array.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            array = cp.multiply(window, cp.asarray(self.array))
            self.array = cp.asnumpy(array)
        except:
            col = np.hamming(self.array.shape[0])
            row = np.hamming(self.array.shape[1])
            window = np.sqrt(np.outer(col, row))
            array = np.multiply(window, self.array)
            self.array = array
        finally:
            if updateAll:
                self.updateAll()

    def applyHanning(self, updateAll=True):
        try:
            col = cp.hanning(self.array.shape[0])
            row = cp.hanning(self.array.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            array = cp.multiply(window, cp.asarray(self.array))
            self.array = cp.asnumpy(array)
        except:
            col = np.hanning(self.array.shape[0])
            row = np.hanning(self.array.shape[1])
            window = np.sqrt(np.outer(col, row))
            array = np.multiply(window, self.array)
            self.array = array
        finally:
            if updateAll:
                self.updateAll()

    def applyHistogramEqualisation(self, updateAll=True):
        try:
            transFunc = cp.cumsum(self.histogram)
            transFunc = transFunc * 255 / transFunc.max()
            transFunc = transFunc.astype(int)
            gpuMap = cp.ElementwiseKernel(
                'T x, raw T y', 'T z',
                'z = y[x]',
                'gpuMap'
            )
            array = cp.array(gpuMap(cp.asarray(self.array), transFunc))
            self.array = cp.asnumpy(array)
        except:
            transFunc = np.cumsum(self.histogram)
            transFunc = transFunc * 255 / transFunc.max()
            transFunc = transFunc.astype(int)
            array = np.array(list(map(lambda x: transFunc[x], self.array)))
            self.array = array
        finally:
            if updateAll:
                self.updateAll()

    def updateFft(self):
        try:
            array = cp.asarray(self.array)
            fft = cp.fft.fft2(array)
            fft = cp.fft.fftshift(fft)
            fft = cp.abs(fft)
            threshold = 2 * fft.sum() / 1024 / 768
            fft = fft > threshold
            fft = fft * 255
            self._fft = cp.asnumpy(fft)
        except:
            fft = np.fft.fft2(self.array)
            fft = np.fft.fftshift(fft)
            fft = np.abs(fft)
            threshold = 2 * fft.sum() / 1024 / 768
            fft = fft > threshold
            fft = fft * 255
            self._fft = fft

    def updateHistogram(self):
        try:
            array = cp.asarray(self.array)
            hist = cp.histogram(array, bins=cp.arange(257))
            self._histogram = cp.asnumpy(hist[0])
        except:
            hist = np.histogram(self.array, bins=np.arange(257))
            self._histogram = hist[0]

    def updateAll(self):
        self.updateFft()
        self.updateHistogram()
