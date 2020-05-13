#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement the SemImage class, each SemImage instance represents an 8-bit grey-level image.

import numpy as np

try:
    import cupy as cp
except:
    print("Warning, could not import cupy, CUDA acceleration will be disabled.")

class SemImage:
    def __init__(self, image):
        self._fft = None
        self._histogram = None

        self.image = image
        self.updateAll()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        image = np.asarray(image, int)
        if len(image.shape) != 2:
            raise TypeError("SemImage was not initialised with a 2d array.")
        if image.max() > 255 or image.min() < 0:
            raise TypeError("SemImage was not initialised with a grey-level image.")
        self._image = image

    @property
    def fft(self):
        return self._fft

    @property
    def histogram(self):
        return self._histogram

    def applyHamming(self, updateAll=True):
        try:
            col = cp.hamming(self.image.shape[0])
            row = cp.hamming(self.image.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            image = cp.multiply(window, cp.asarray(self.image))
            self.image = cp.asnumpy(image)
        except:
            col = np.hamming(self.image.shape[0])
            row = np.hamming(self.image.shape[1])
            window = np.sqrt(np.outer(col, row))
            image = np.multiply(window, self.image)
            self.image = image
        finally:
            if updateAll:
                self.updateAll()

    def applyHanning(self, updateAll=True):
        try:
            col = cp.hanning(self.image.shape[0])
            row = cp.hanning(self.image.shape[1])
            window = cp.sqrt(cp.outer(col, row))
            image = cp.multiply(window, cp.asarray(self.image))
            self.image = cp.asnumpy(image)
        except:
            col = np.hanning(self.image.shape[0])
            row = np.hanning(self.image.shape[1])
            window = np.sqrt(np.outer(col, row))
            image = np.multiply(window, self.image)
            self.image = image
        finally:
            if updateAll:
                self.updateAll()

    def applyHistogramEqualisation(self, updateAll=True):
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
        image = np.image(list(map(lambda x: histTrans[x], self.image)))
        self.image = image
        
        if updateAll:
            self.updateAll()

    def updateFft(self):
        try:
            image = cp.asarray(self.image)
            fft = cp.fft.fft2(image)
            fft = cp.fft.fftshift(fft)
            fft = cp.abs(fft)
            self._fft = cp.asnumpy(fft)
        except:
            fft = np.fft.fft2(self.image)
            fft = np.fft.fftshift(fft)
            fft = np.abs(fft)
            self._fft = fft

    def updateHistogram(self):
        try:
            image = cp.asarray(self.image)
            hist = cp.histogram(image, bins=cp.arange(257))
            self._histogram = cp.asnumpy(hist[0])
        except:
            hist = np.histogram(self.image, bins=np.arange(257))
            self._histogram = hist[0]

    def updateAll(self):
        self.updateFft()
        self.updateHistogram()
