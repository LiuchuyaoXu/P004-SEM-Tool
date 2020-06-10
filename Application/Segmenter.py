#   File:   Segmenter.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement a class that helps segment a matrice into 8 regions.
#           Run this script for a demonstration.

import numpy as np

class Segmenter:

    r1 = None
    r2 = None
    r3 = None
    r4 = None
    s1 = None
    s2 = None
    s3 = None
    s4 = None

    def __init__(self, shape):
        self.r1 = np.ones(shape, int)
        self.r2 = np.ones(shape, int)
        self.r3 = np.ones(shape, int)
        self.r4 = np.ones(shape, int)
        self.s1 = np.ones(shape, int)
        self.s2 = np.ones(shape, int)
        self.s3 = np.ones(shape, int)
        self.s4 = np.ones(shape, int)

        xLength = shape[0]
        yLength = shape[1]
        xOrigin = np.floor(xLength / 2)
        yOrigin = np.floor(yLength / 2)
        for i in range(0, xLength):
            for j in range(0, yLength):
                x = i - xOrigin
                y = j - yOrigin
                if x == 0:
                    if y == 0:
                        self.r1[i][j] = 0
                        self.r2[i][j] = 0
                        self.r3[i][j] = 0
                        self.r4[i][j] = 0
                        self.s1[i][j] = 0
                        self.s2[i][j] = 0
                        self.s3[i][j] = 0
                        self.s4[i][j] = 0
                    elif y > 0:
                        self.r1[i][j] = 0
                    else:
                        self.r2[i][j] = 0
                elif x > 0:
                    if y == 0:
                        self.r4[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r2[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s2[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r4[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s4[i][j] = 0
                        else:
                            self.r1[i][j] = 0
                else:
                    if y == 0:
                        self.r3[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self.r1[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self.s1[i][j] = 0
                        elif angle < (np.pi / 8):
                            self.r3[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self.s3[i][j] = 0
                        else:
                            self.r2[i][j] = 0

if __name__ == "__main__":
    segmenter = Segmenter([5, 7])
    print("Region r1:")
    print(segmenter.r1)
    print("Region r2:")
    print(segmenter.r2)
    print("Region r3:")
    print(segmenter.r3)
    print("Region r4:")
    print(segmenter.r4)
    print("Region s1:")
    print(segmenter.s1)
    print("Region s2:")
    print(segmenter.s2)
    print("Region s3:")
    print(segmenter.s3)
    print("Region s4:")
    print(segmenter.s4)
