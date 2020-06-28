#   File:   SemImage.py   
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement the SemImage class.
#           The class encapsulates data and methods relevant to a monochrome image.

from abc import ABC
from abc import abstractmethod

try:
    import cupy
except:
    import numpy
    cupy = None
    print('Warning, could not import CuPy, GPU acceleration will be disabled.')

class SemImage(ABC):
    _image = None
    bitDepth = None
    maxLevel = None

    _fft = None
    _histogram = None

    def __init__(self, image, bitDepth=8):
        self.image = image
        self.bitDepth = bitDepth
        self.maxLevel = 2**self.bitDepth - 1

    @property
    @abstractmethod
    def image(self):
        ...

    @image.setter
    @abstractmethod
    def image(self, image):
        ...

    @property
    @abstractmethod
    def fft(self):
        ...

    @property
    @abstractmethod
    def histogram(self):
        ...

    @abstractmethod
    def applyHanning(self):
        ...

    @abstractmethod
    def applyHistogramEqualisation(self):
        ...

    @abstractmethod
    def updateFft(self):
        ...
    
    @abstractmethod
    def updateHistogram(self):
        ...

    @classmethod
    def create(cls, image):
        if cupy:
            return SemImageCuPy(image)
        else:
            return SemImageNumPy(image)

class SemImageNumPy(SemImage):

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = numpy.array(image)

    @property
    def fft(self):
        return self._fft

    @property
    def histogram(self):
        return self._histogram

    def applyHanning(self):
        col = numpy.hanning(self._image.shape[0])
        row = numpy.hanning(self._image.shape[1])
        window = numpy.sqrt(numpy.outer(col, row))
        self._image = numpy.multiply(window, self._image)

    def applyHistogramEqualisation(self):
        transFunc = numpy.cumsum(self._histogram)
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        self._image = numpy.array(map(lambda x: transFunc[x], self._image))

    def updateFft(self):
        fft = numpy.fft.fft2(self._image)
        fft = numpy.fft.fftshift(fft)
        fft = numpy.abs(fft)
        self._fft = fft

    def updateHistogram(self):
        self._histogram = numpy.histogram(self._image, bins=numpy.arange(self.maxLevel+2))

class SemImageCuPy(SemImage):

    @property
    def image(self):
        return cupy.asnumpy(self._image)

    @image.setter
    def image(self, image):
        self._image = cupy.array(image)

    @property
    def fft(self):
        return cupy.asnumpy(self._fft)

    @property
    def histogram(self):
        return (cupy.asnumpy(self._histogram[0]), cupy.asnumpy(self._histogram[1]))

    def applyHanning(self):
        col = cupy.hanning(self._image.shape[0])
        row = cupy.hanning(self._image.shape[1])
        window = cupy.sqrt(cupy.outer(col, row))
        self._image = cupy.multiply(window, self._image)

    def applyHistogramEqualisation(self):
        transFunc = cupy.cumsum(self._histogram)
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        gpuMap = cupy.ElementwiseKernel(
            'T x, raw T y', 'T z',
            'z = y[x]',
            'gpuMap'
        )
        self._image = cupy.array(gpuMap(self._image, transFunc))

    def updateFft(self):
        fft = cupy.fft.fft2(self._image)
        fft = cupy.fft.fftshift(fft)
        fft = cupy.abs(fft)
        self._fft = fft

    def updateHistogram(self):
        self._histogram = cupy.histogram(self._image, bins=cupy.arange(self.maxLevel+2))
