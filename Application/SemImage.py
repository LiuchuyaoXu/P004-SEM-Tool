#   File:   SemImage.py
#
#   Author: Liuchuyao Xu, 2020

import cupy

class SemImage:

    def __init__(self, bitDepth=8, image=None):
        self.bitDepth = bitDepth

        self._image = None
        self._fft = None
        self._histogram = None

        if image:
            self.setImage(image)

    def image(self, returnCupy=False):
        if returnCupy:
            return self._image
        else:
            return cupy.asnumpy(self._image)

    def fft(self, returnCupy=False):
        if self._fft is None:
            self.updateFft()
        
        if returnCupy:
            return self._fft
        else:
            return cupy.asnumpy(self._fft)

    def histogram(self, returnCupy=False):
        if self._histogram is None:
            self.updateHistogram()
        
        if returnCupy:
            return self._histogram
        else:
            return cupy.asnumpy(self._histogram)

    def setImage(self, image):
        self._fft = None
        self._histogram = None
        self._image = cupy.asarray(image)
        
    def updateFft(self):
        fft = cupy.fft.fft2(self._image)
        fft = cupy.fft.fftshift(fft)
        fft = cupy.abs(fft)
        self._fft = fft

    def updateHistogram(self):
        binEdges = cupy.arange(2**self.bitDepth + 1)
        self._histogram = cupy.histogram(self._image, bins=binEdges)

    def applyHann(self):
        width = self._image.shape[0]
        height = self._image.shape[1]
        row = cupy.hanning(width)
        col = cupy.hanning(height)
        window = cupy.outer(row, col)
        window = cupy.sqrt(window)
        image = cupy.multiply(window, self._image)
        self.setImage(image)

    def applyHistogramEqualisation(self):
        if self._histogram is None:
            self.updateHistogram()

        maxLevel = 2**self.bitDepth - 1
        dataType = 'uint{}'.format(self.bitDepth)
        transferMap = cupy.cumsum(self._histogram[0])
        transferMap = transferMap / transferMap.max()
        transferMap = transferMap * maxLevel
        transferMap = transferMap.round()
        transferMap = transferMap.astype(dataType)
        gpuMap = cupy.ElementwiseKernel(
            'T x, raw T y', 'T z',
            'z = y[x]',
            'gpuMap'
        )
        image = gpuMap(self._image, transferMap)
        self.setImage(image)
