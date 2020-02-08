import sys
import time
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.colors import LogNorm

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

class semImage(np.ndarray):
    def __array_finalize__(self, obj):
        self.fft = np.array([])
        self.fftSegments = np.array([])

    def getFft(self):
        fft = np.fft.fft2(self)
        fft = np.fft.fftshift(fft)
        fft = np.abs(fft)
        self.fft = fft
        return self.fft

    def segmentFft(self, masker):
        if self.fftSegments.size != 0:
            return self.fftSegments
        if self.fft.size == 0:
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

if __name__ == "__main__":
    # image1 = Image.open("./Images for FFT Testing/xy2.tif").convert('L')
    image1 = Image.open("./Images from SEM/astig1.tif").convert('L')
    image1 = np.asarray(image1)
    image1 = image1.view(semImage)

    # image2 = Image.open("./Images for FFT Testing/xy3.tif").convert('L')
    image2 = Image.open("./Images from SEM/astig2.tif").convert('L')
    image2 = np.asarray(image2)
    image2 = image2.view(semImage)

    # image3 = Image.open("./Images for FFT Testing/xy3.tif").convert('L')
    image3 = Image.open("./Images from SEM/astig3.tif").convert('L')
    image3 = np.asarray(image3)
    image3 = image3.view(semImage)

    image1Fft = image1.getFft()
    # image1Fft = image1Fft / image1Fft.max()
    # image1Fft = image1Fft * 255
    # image1Fft = image1Fft.astype(int)
    image2Fft = image2.getFft()
    # image2Fft = image2Fft / image2Fft.max()
    # image2Fft = image2Fft * 255
    # image2Fft = image2Fft.astype(int)
    image3Fft = image3.getFft()

    # print("The maximum value in image1Fft is: ", image1Fft.max())
    # print("The maximum value in image2Fft is: ", image2Fft.max())
    # difference = image1Fft - np.rot90(image2Fft)
    # print("The sum of difference in image1Fft and rotated image2Fft is: ", difference.sum())

    # print(image1Fft)
    # print(image1Fft.sum())
    # start = time.time()
    masker = Masker(image1.shape)
    # mid = time.time()
    print("Image 1 sums of FFT segments: ", image1.segmentFft(masker).astype(int))
    print("Image 2 sums of FFT segments: ", image2.segmentFft(masker).astype(int))
    print("Image 3 sums of FFT segments: ", image3.segmentFft(masker).astype(int))
    # end = time.time()
    # print(mid - start)
    # print(end - mid)
    # print(image1.segmentFft().sum())

    fig, axis = plt.subplots(3, 2)
    axis[0][0].imshow(image1, cmap="gray")
    axis[0][1].imshow(image1Fft, cmap="gray", norm=LogNorm())
    axis[1][0].imshow(image2, cmap="gray")
    axis[1][1].imshow(image2Fft, cmap="gray", norm=LogNorm())
    axis[2][0].imshow(image3, cmap="gray")
    axis[2][1].imshow(image3Fft, cmap="gray", norm=LogNorm())
    plt.tight_layout()
    plt.show()

    # masker = Masker(image1.shape)
    # masker = Masker([20, 20])
    # print(masker.r1)
    # print(masker.r2)
    # print(masker.r3)
    # print(masker.r4)
    # print(masker.s1)
    # print(masker.s2)
    # print(masker.s3)
    # print(masker.s4)
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
