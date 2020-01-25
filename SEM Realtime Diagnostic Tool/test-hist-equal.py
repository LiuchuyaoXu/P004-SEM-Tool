import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from numba import jit

@jit(nopython=True)
def getHistEqualized(image):
        hist = np.zeros(256)
        for i in range(0, image.shape[0]):
            for j in range(0, image.shape[1]):
                hist[image[i, j]] += 1
                
        histTrans   = np.zeros(256)
        numPixels   = np.sum(hist)

        summ = 0
        for i in range(0, 256):
            summ += hist[i]
            histTrans[i] = summ
        histTrans /= numPixels
        histTrans *= 255 / max(histTrans)

        shape       = image.shape
        newHist     = np.zeros(256)
        newImage    = np.zeros(shape)
        for i in range(0, shape[0]):
            for j in range(0, shape[1]):
                newImage[i, j] = histTrans[image[i, j]]
                newHist[int(newImage[i, j])] += 1

        return newImage, newHist

class semImage(np.ndarray):
    def __init__(self):
        super().__init__()

    def getFlat(self):
        return np.matrix.flatten(self)

    def getHist(self):
        hist = np.zeros(256)
        for pixel in self.getFlat():
            hist[pixel] += 1
        return hist

    def getHistEqualized(self):
        hist        = self.getHist()
        histTrans   = np.zeros(256)
        numPixels   = np.sum(hist)

        summ = 0
        for i in range(0, 256):
            summ += hist[i]
            histTrans[i] = summ
        histTrans /= numPixels
        histTrans *= 255 / max(histTrans)
        histTrans = histTrans.astype(int)

        newHist     = np.zeros(256)
        newImage    = np.zeros(self.shape).astype(int)
        for i in range(0, self.shape[0]):
            for j in range(0, self.shape[1]):
                newImage[i, j] = histTrans[self[i, j]]
                newHist[newImage[i, j]] += 1

        return newImage, newHist

if __name__ == "__main__":
    image = Image.open("SEM Images/Armin241.tif")
    image = np.asarray(image)
    image = image.view(semImage)

    imageHist               = image.getHist()
    start = time.time()
    # newImage, newImageHist  = image.getHistEqualized()
    newImage, newImageHist  = getHistEqualized(image)
    end = time.time()
    print(end - start)

    fig, a = plt.subplots(2, 2)
    a[0][0].imshow(image, cmap="gray")
    a[0][1].bar(np.arange(0, imageHist.size), imageHist)
    a[1][0].imshow(newImage, cmap="gray")
    a[1][1].bar(np.arange(0, newImageHist.size), newImageHist)
    plt.show()
