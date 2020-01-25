import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

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
        start = time.time()
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

        shape = self.shape
        newImage = np.zeros(shape).astype(int)
        for i in range(0, shape[0]):
            for j in range(0, shape[1]):
                newImage[i, j] = histTrans[self[i, j]]

        newHist = np.zeros(256)
        for pixel in np.matrix.flatten(newImage):
            newHist[pixel] += 1
        end = time.time()
        print(end - start)
        return newImage, newHist

if __name__ == "__main__":
    image = Image.open("SEM Images/Armin241.tif")
    image = np.asarray(image)
    image = image.view(semImage)

    imageHist               = image.getHist()
    newImage, newImageHist  = image.getHistEqualized()

    fig, a = plt.subplots(2, 2)
    a[0][0].imshow(image, cmap="gray")
    a[0][1].bar(np.arange(0, imageHist.size), imageHist)
    a[1][0].imshow(newImage, cmap="gray")
    a[1][1].bar(np.arange(0, newImageHist.size), newImageHist)
    plt.show()
