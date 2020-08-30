#   File:   SemImage.py
#
#   Author: Liuchuyao Xu, 2020

try:
    import cupy
except:
    import numpy
    cupy = None
    print('SemImage: could not import cupy, GPU acceleration will be disabled.')

def SemImage(image):
    if cupy:
        return SemImageCupy(image)
    else:
        return SemImageNumpy(image)

class SemImageCupy:

    def __init__(self, image=None):
        self.bitDepth = 8
        
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

    def histogram(self, returnCupy=False):
        if self._histogram is None:
            self.updateHistogram()
        
        if returnCupy:
            return self._histogram
        else:
            return cupy.asnumpy(self._histogram)

    def fft(self, returnCupy=False):
        if self._fft is None:
            self.updateFft()
        
        if returnCupy:
            return self._fft
        else:
            return cupy.asnumpy(self._fft)

    def setImage(self, image):
        self._fft = None
        self._histogram = None
        self._image = cupy.asarray(image)

    def updateHistogram(self):
        binEdges = cupy.arange(2**self.bitDepth + 1)
        self._histogram = cupy.histogram(self._image, bins=binEdges)
        
    def updateFft(self):
        fft = cupy.fft.fft2(self._image)
        fft = cupy.fft.fftshift(fft)
        fft = cupy.abs(fft)
        self._fft = fft

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
        transferMap = transferMap.round().astype(dataType)
        gpuMap = cupy.ElementwiseKernel(
            'T x, raw T y', 'T z',
            'z = y[x]',
            'gpuMap'
        )
        image = gpuMap(self._image, transferMap)
        self.setImage(image)

class SemImageNumpy:

    def __init__(self, image=None):
        self.bitDepth = 8
        
        self._image = None
        self._fft = None
        self._histogram = None

        if image:
            self.setImage(image)

    def image(self):
        return self._image

    def histogram(self):
        if self._histogram is None:
            self.updateHistogram()        
        return self._histogram

    def fft(self):
        if self._fft is None:
            self.updateFft()
        return self._fft

    def setImage(self, image):
        self._image = numpy.asarray(image)
        self._fft = None
        self._histogram = None

    def updateHistogram(self):
        binEdges = numpy.arange(2**self.bitDepth + 1)
        self._histogram = numpy.histogram(self._image, bins=binEdges)
        
    def updateFft(self):
        fft = numpy.fft.fft2(self._image)
        fft = numpy.fft.fftshift(fft)
        fft = numpy.abs(fft, order='C')
        self._fft = fft

    def applyHann(self):
        width = self._image.shape[0]
        height = self._image.shape[1]
        row = numpy.hanning(width)
        col = numpy.hanning(height)
        window = numpy.outer(row, col)
        window = numpy.sqrt(window)
        image = numpy.multiply(window, self._image, order='C')
        self.setImage(image)

    def applyHistogramEqualisation(self):
        if self._histogram is None:
            self.updateHistogram()

        maxLevel = 2**self.bitDepth - 1
        dataType = 'uint{}'.format(self.bitDepth)
        transferMap = numpy.cumsum(self._histogram[0])
        transferMap = transferMap / transferMap.max()
        transferMap = transferMap * maxLevel
        transferMap = transferMap.round().astype(dataType)
        image = numpy.asarray(list(map(lambda x: transferMap[x], self._image)))
        self.setImage(image)
