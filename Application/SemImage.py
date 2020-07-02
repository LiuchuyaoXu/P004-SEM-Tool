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
    print('Could not import CuPy, GPU acceleration will be disabled.')

class SemImage(ABC):
    _image = None
    bitDepth = None
    dataType = None
    maxLevel = None

    _fft = None
    _histogram = None

    def __init__(self, image, bitDepth=8):
        self.bitDepth = bitDepth
        self.dataType = 'uint{}'.format(self.bitDepth)
        self.maxLevel = 2**self.bitDepth - 1

        self.image = image

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
        self._image = numpy.array(image, dtype=numpy.dtype(self.dataType))

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
        self._image = self._image.astype(self.dataType)

    def applyHistogramEqualisation(self):
        transFunc = numpy.cumsum(self._histogram[0])
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        self._image = numpy.array(list(map(lambda x: transFunc[x], self._image)))
        self._image = self._image.astype(self.dataType)

    def thresholdFft(self):
        noiseLevel = numpy.sum(self._fft[0][0:10]) / 10
        self._fft = self._fft > noiseLevel
        self._fft = self._fft.astype('uint8')

    def updateFft(self):
        fft = numpy.fft.fft2(self._image)
        fft = numpy.fft.fftshift(fft)
        fft = numpy.abs(fft, order='C')
        self._fft = fft

    def updateHistogram(self):
        self._histogram = numpy.histogram(self._image, bins=numpy.arange(self.maxLevel+2))

class SemImageCuPy(SemImage):

    @property
    def image(self):
        return cupy.asnumpy(self._image)

    @image.setter
    def image(self, image):
        self._image = cupy.array(image, dtype=cupy.dtype(self.dataType))

    @property
    def fft(self):
        return cupy.asnumpy(self._fft, order=u'C')

    @property
    def histogram(self):
        return (cupy.asnumpy(self._histogram[0]), cupy.asnumpy(self._histogram[1]))

    def applyHanning(self):
        col = cupy.hanning(self._image.shape[0])
        row = cupy.hanning(self._image.shape[1])
        window = cupy.sqrt(cupy.outer(col, row))
        self._image = cupy.multiply(window, self._image)
        self._image = self._image.astype(self.dataType)

    def applyHistogramEqualisation(self):
        transFunc = cupy.cumsum(self._histogram[0])
        transFunc = transFunc / transFunc.max()
        transFunc = transFunc * self.maxLevel
        transFunc = transFunc.round()
        transFunc = transFunc.astype(self.dataType)
        gpuMap = cupy.ElementwiseKernel(
            'T x, raw T y', 'T z',
            'z = y[x]',
            'gpuMap'
        )
        self._image = cupy.array(gpuMap(self._image, transFunc))
        self._image = self._image.astype(self.dataType)

    def thresholdFft(self):
        noiseLevel = cupy.sum(self._fft[0][0:100]) / 100
        self._fft = self._fft > noiseLevel
        self._fft = self._fft.astype('uint8')

    def updateFft(self):
        fft = cupy.fft.fft2(self._image)
        fft = cupy.fft.fftshift(fft)
        fft = cupy.abs(fft)
        self._fft = fft

    def updateHistogram(self):
        self._histogram = cupy.histogram(self._image, bins=cupy.arange(self.maxLevel+2))
