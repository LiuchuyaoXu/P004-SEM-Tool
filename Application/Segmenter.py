#   File:   Segmenter.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement a class that helps segment matrices.
#           Run the script for a demonstration.

import numpy as np
import numpy.ma as ma

class Segmenter:

    def __init__(self, shape):
        self.r1 = np.ones(shape, int)
        self.r2 = np.ones(shape, int)
        self.r3 = np.ones(shape, int)
        self.r4 = np.ones(shape, int)
        self.s1 = np.ones(shape, int)
        self.s2 = np.ones(shape, int)
        self.s3 = np.ones(shape, int)
        self.s4 = np.ones(shape, int)

        width = shape[0]
        height = shape[1]
        xOrigin = np.floor(width/2)
        yOrigin = np.floor(height/2)
        for i in range(0, width):
            for j in range(0, height):
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

    def calculateSums(self, matrix):
        sum_ = matrix.sum()
        sum_r1 = ma.array(matrix, mask=self.r1).sum()
        sum_r2 = ma.array(matrix, mask=self.r2).sum()
        sum_r3 = ma.array(matrix, mask=self.r3).sum()
        sum_r4 = ma.array(matrix, mask=self.r4).sum()
        sum_s1 = ma.array(matrix, mask=self.s1).sum()
        sum_s2 = ma.array(matrix, mask=self.s2).sum()
        sum_s3 = ma.array(matrix, mask=self.s3).sum()
        sum_s4 = ma.array(matrix, mask=self.s4).sum()
        sum_r12 = sum_r1 + sum_r2
        sum_r34 = sum_r3 + sum_r4
        sum_s12 = sum_s1 + sum_s2
        sum_s34 = sum_s3 + sum_s4
        return sum_, sum_r12, sum_r34, sum_s12, sum_s34

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
