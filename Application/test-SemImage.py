import os
import sys
import time
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImagePalette
from matplotlib.colors import LogNorm

# Divides the 2d shape into 8 non-overlapping regions by angle.
class Masker:
    def __init__(self, shape):
        self.r1 = np.ones(shape)
        self.r2 = np.ones(shape)
        self.r3 = np.ones(shape)
        self.r4 = np.ones(shape)
        self.s1 = np.ones(shape)
        self.s2 = np.ones(shape)
        self.s3 = np.ones(shape)
        self.s4 = np.ones(shape)

        xLen = shape[0]
        yLen = shape[1]
        xOri = np.floor(xLen / 2)
        yOri = np.floor(yLen / 2)
        for i in range(0, xLen):
            for j in range(0, yLen):
                x = i - xOri
                y = j - yOri
                if x == 0:
                    if y == 0:
                        pass
                    elif y > 0:
                        self.r1[i][j] = 0
                    else:
                        self.r3[i][j] = 0
                elif x > 0:
                    if y == 0:
                        self.r4[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r3[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s3[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r4[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s4[i][j] = 0
                        else:
                            self.r1[i][j] = 0
                else:
                    if y == 0:
                        self.r2[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r1[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s1[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r2[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s2[i][j] = 0
                        else:
                            self.r3[i][j] = 0

# Each SemImage represents a 8-bit grey-level image.
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

if __name__ == "__main__":
    imageFolder = "./Images for Testing Correction Algorithm/"

    image1 = Image.open(imageFolder + "richard1.tif").convert('L')
    # image1 = Image.open("./Images from SEM/Armin241.tif").convert('L')
    image1 = np.asarray(image1)
    image1 = image1.view(SemImage)

    image2 = Image.open(imageFolder + "richard2.tif").convert('L')
    # image2 = Image.open("./Images from SEM/novstig2.tif").convert('L')
    image2 = np.asarray(image2)
    image2 = image2.view(SemImage)

    image3 = Image.open(imageFolder + "richard3.tif").convert('L')
    # image3 = Image.open("./Images from SEM/novstig3.tif").convert('L')
    image3 = np.asarray(image3)
    image3 = image3.view(SemImage)

    image4 = Image.open(imageFolder + "richard4.tif").convert('L')
    # image4 = Image.open("./Images from SEM/novstig3.tif").convert('L')
    image4 = np.asarray(image4)
    image4 = image3.view(SemImage)

    image5 = Image.open(imageFolder + "richard5.tif").convert('L')
    # image5 = Image.open("./Images from SEM/novstig3.tif").convert('L')
    image5 = np.asarray(image5)
    image5 = image3.view(SemImage)

    masker = Masker(image1.shape)

    image1.getFft()
    image2.getFft()
    image3.getFft()
    image4.getFft()
    image5.getFft()
    # image1.getFftSegments(masker)
    # image1.getHist()
    # start = time.time()
    # image1.getHistEqualised()
    # end = time.time()
    # print(end - start)
    # image1.histEqualised.getFft()
    # image1.histEqualised.getFftSegments(masker)
    # image1.histEqualised.getHist()

    fig, axis = plt.subplots(2, 5, constrained_layout=True)
    axis[0][0].imshow(image1, cmap="gray")
    axis[1][0].imshow(image1.fft, cmap="gray", norm=LogNorm())
    axis[1][0].set_xlim(400, 600)
    axis[1][0].set_ylim(300, 500)

    axis[0][1].imshow(image2, cmap="gray")
    axis[1][1].imshow(image2.fft, cmap="gray", norm=LogNorm())
    axis[1][1].set_xlim(400, 600)
    axis[1][1].set_ylim(300, 500)

    axis[0][2].imshow(image3, cmap="gray")
    axis[1][2].imshow(image3.fft, cmap="gray", norm=LogNorm())
    axis[1][2].set_xlim(400, 600)
    axis[1][2].set_ylim(300, 500)

    axis[0][3].imshow(image4, cmap="gray")
    axis[1][3].imshow(image4.fft, cmap="gray", norm=LogNorm())
    axis[1][3].set_xlim(400, 600)
    axis[1][3].set_ylim(300, 500)

    axis[0][4].imshow(image5, cmap="gray")
    axis[1][4].imshow(image5.fft, cmap="gray", norm=LogNorm())
    axis[1][4].set_xlim(400, 600)
    axis[1][4].set_ylim(300, 500)
    plt.tight_layout()
    plt.show()

    # print("Image 1 sums of FFT segments: ", image1.getFftSegments(masker).astype(int))
    # print("Image 2 sums of FFT segments: ", image2.getFftSegments(masker).astype(int))
    # print("Image 3 sums of FFT segments: ", image3.getFftSegments(masker).astype(int))

    # fig, axis = plt.subplots(3, 2)
    # axis[0][0].imshow(image1, cmap="gray")
    # axis[0][1].imshow(image1.fft, cmap="gray", norm=LogNorm())
    # axis[0][2].bar(image1.hist[1][:-1], image1.hist[0], width=1)
    # axis[1][0].imshow(image1.histEqualised, cmap="gray")
    # axis[1][1].imshow(image1.histEqualised.fft, cmap="gray", norm=LogNorm())
    # axis[1][2].bar(image1.histEqualised.hist[1][:-1], image1.histEqualised.hist[0], width=1)
    # plt.tight_layout()
    # plt.show()

    # masker = Masker(image1.shape)
    # masker = Masker([20, 20])
    # fig, axis = plt.subplots(8)
    # axis[0].imshow(masker.r1 * 255, cmap="gray")
    # axis[1].imshow(masker.r2 * 255, cmap="gray")
    # axis[2].imshow(masker.r3 * 255, cmap="gray")
    # axis[3].imshow(masker.r4 * 255, cmap="gray")
    # axis[4].imshow(masker.s1 * 255, cmap="gray")
    # axis[5].imshow(masker.s2 * 255, cmap="gray")
    # axis[6].imshow(masker.s3 * 255, cmap="gray")
    # axis[7].imshow(masker.s4 * 255, cmap="gray")
    # plt.show()

    # imageFolder = "./Images for Testing Correction Algorithm/"
    # for imageName in os.listdir(imageFolder):
    #     image = Image.open(os.path.join(imageFolder, imageName))
    #     image = np.asarray(image)
    #     image = image.view(SemImage)

    #     fig, axis = plt.subplots(1, 2)
    #     axis[0].imshow(image, cmap="gray")
    #     axis[1].imshow(image.getFft(), cmap="gray", norm=LogNorm())
    #     plt.tight_layout()
    #     plt.savefig(os.path.join("./Test Outputs/", os.path.splitext(imageName)[0]))

    #     print(imageName)
