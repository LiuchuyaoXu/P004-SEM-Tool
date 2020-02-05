import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.colors import LogNorm

class masker:
    def __init__(self, shape):
        xLen    = shape[0]
        yLen    = shape[1]
        origin  = np.array([xLen / 2, yLen / 2])
        origin  = origin.astype(int)

        self.r1 = np.zeros(shape)
        self.r2 = np.zeros(shape)
        self.r3 = np.zeros(shape)
        self.r4 = np.zeros(shape)
        self.s1 = np.zeros(shape)
        self.s2 = np.zeros(shape)
        self.s3 = np.zeros(shape)
        self.s4 = np.zeros(shape)

        for i in range(0, xLen):
            for j in range(0, yLen):
                x = i - origin[0]
                y = j - origin[1]
                if x == 0:
                    if y == 0:
                        pass
                    elif y > 0:
                        self.r1[i][j] = 1
                    else:
                        self.r3[i][j] = 1
                elif x > 0:
                    if y == 0:
                        self.r4[i][j] = 1
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r3[i][j] = 1
                        elif angle < (- np.pi / 8):
                            self.s3[i][j] = 1
                        elif angle < (np.pi / 8):
                            self.r4[i][j] = 1
                        elif angle < (3 * np.pi / 8):
                            self.s4[i][j] = 1
                        else:
                            self.r1[i][j] = 1
                else:
                    if y == 0:
                        self.r2[i][j] = 1
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r1[i][j] = 1
                        elif angle < (- np.pi / 8):
                            self.s1[i][j] = 1
                        elif angle < (np.pi / 8):
                            self.r2[i][j] = 1
                        elif angle < (3 * np.pi / 8):
                            self.s2[i][j] = 1
                        else:
                            self.r3[i][j] = 1

class semImage(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return super(semImage, cls).__new__(cls, *args, **kwargs)

    def __array_finalize__(self, obj):
        self.fft = np.array([])
        self.fftSegments = np.array([])

    def getFft(self):
        fft = np.fft.fft2(self)
        fft = np.fft.fftshift(fft)
        fft = np.abs(fft)
        self.fft = fft
        return self.fft

    def segmentFft(self):
        if self.fftSegments.size:
            return self.fftSegments

        if not self.fft.size:
            self.getFft()

        xLen    = self.fft.shape[0]
        yLen    = self.fft.shape[1]
        origin  = np.array([xLen / 2, yLen / 2])
        origin  = origin.astype(int)

        r1 = r2 = r3 = r4 = s1 = s2 = s3 = s4 = 0
        for i in range(0, xLen):
            for j in range(0, yLen):
                value = self.fft[i][j]
                x = i - origin[0]
                y = j - origin[1]
                if x == 0:
                    if y == 0:
                        pass
                    elif y > 0:
                        r3 += value
                    else:
                        r4 += value
                elif x > 0:
                    if y == 0:
                        r1 += value
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            r4 += value
                        elif angle < (- np.pi / 8):
                            s4 += value
                        elif angle < (np.pi / 8):
                            r1 += value
                        elif angle < (3 * np.pi / 8):
                            s1 += value
                        else:
                            r3 += value
                else:
                    if y == 0:
                        r2 += value
                    else:
                        angle = np.arctan(y/x)
                        if angle <= (- 3 * np.pi / 8):
                            r4 += value
                        elif angle <= (- np.pi / 8):
                            s2 += value
                        elif angle <= (np.pi / 8):
                            r2 += value
                        elif angle <= (3 * np.pi / 8):
                            s3 += value
                        else:
                            r3 += value

        self.fftSegments = np.array([r1, r2, r3, r4, s1, s2, s3, s4])
        return self.fftSegments

if __name__ == "__main__":
    image1 = Image.open("./Images for FFT Testing/xy2.tif").convert('L')
    # image1 = Image.open("./Images from SEM/Armin241.tif").convert('L')
    image1 = np.asarray(image1)
    image1 = image1.view(semImage)

    image2 = Image.open("./Images for FFT Testing/xy3.tif").convert('L')
    # image2 = Image.open("./Images from SEM/Armin241b.tif").convert('L')
    image2 = np.asarray(image2)
    image2 = image2.view(semImage)

    image1Fft = image1.getFft()
    # image1Fft = image1Fft / image1Fft.max()
    # image1Fft = image1Fft * 255
    # image1Fft = image1Fft.astype(int)
    image2Fft = image2.getFft()
    # image2Fft = image2Fft / image2Fft.max()
    # image2Fft = image2Fft * 255
    # image2Fft = image2Fft.astype(int)

    # print("The maximum value in image1Fft is: ", image1Fft.max())
    # print("The maximum value in image2Fft is: ", image2Fft.max())
    # difference = image1Fft - np.rot90(image2Fft)
    # print("The sum of difference in image1Fft and rotated image2Fft is: ", difference.sum())

    # print(image1Fft)
    # print(image1Fft.sum())
    # print(image1.segmentFft())
    # print(image2.segmentFft())
    # print(image1.segmentFft().sum())

    # fig, axis = plt.subplots(2, 2)
    # axis[0][0].imshow(image1, cmap="gray")
    # # axis[1][0].imshow(image1Fft, cmap="gray")
    # axis[1][0].imshow(image1Fft, cmap="gray", norm=LogNorm())
    # axis[0][1].imshow(image2, cmap="gray")
    # # axis[1][1].imshow(image2Fft, cmap="gray")
    # axis[1][1].imshow(image2Fft, cmap="gray", norm=LogNorm())
    # plt.tight_layout()
    # plt.show()


    mask = masker(image1.shape)
    # mask = masker([20, 20])
    # print(mask.r1)
    # print(mask.r2)
    # print(mask.r3)
    # print(mask.r4)
    # print(mask.s1)
    # print(mask.s2)
    # print(mask.s3)
    # print(mask.s4)
    fig, axis = plt.subplots(8)
    axis[0].imshow(mask.r1 * 255, cmap="gray")
    axis[1].imshow(mask.r2 * 255, cmap="gray")
    axis[2].imshow(mask.r3 * 255, cmap="gray")
    axis[3].imshow(mask.r4 * 255, cmap="gray")
    axis[4].imshow(mask.s1 * 255, cmap="gray")
    axis[5].imshow(mask.s2 * 255, cmap="gray")
    axis[6].imshow(mask.s3 * 255, cmap="gray")
    axis[7].imshow(mask.s4 * 255, cmap="gray")
    plt.show()
