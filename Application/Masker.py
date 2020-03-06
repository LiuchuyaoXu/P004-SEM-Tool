# Author:   Liuchuyao Xu, 2020
#
# Brief:    Implement the Masker class, which Provides 8 masks dividing a 2d shape into 8 non-overlapping regions, as specified in K.H. ONG, J.C.H. PHANG, J.T.L. THONG, 1997, A Robust Focusing and Astigmatism Correction Method for the Scanning Electron Microscope.

import numpy as np

class Masker:
    @property
    def r1(self):
        return self._r1

    @property
    def r2(self):
        return self._r2

    @property
    def r3(self):
        return self._r3

    @property
    def r4(self):
        return self._r4

    @property
    def s1(self):
        return self._s1

    @property
    def s2(self):
        return self._s2

    @property
    def s3(self):
        return self._s3

    @property
    def s4(self):
        return self._s4

    def __init__(self, shape):
        self._r1 = np.ones(shape=shape, dtype=int)
        self._r2 = np.ones(shape=shape, dtype=int)
        self._r3 = np.ones(shape=shape, dtype=int)
        self._r4 = np.ones(shape=shape, dtype=int)
        self._s1 = np.ones(shape=shape, dtype=int)
        self._s2 = np.ones(shape=shape, dtype=int)
        self._s3 = np.ones(shape=shape, dtype=int)
        self._s4 = np.ones(shape=shape, dtype=int)

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
                        self._r1[i][j] = 0
                    else:
                        self._r2[i][j] = 0
                elif x > 0:
                    if y == 0:
                        self._r4[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self._r2[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self._s2[i][j] = 0
                        elif angle < (np.pi / 8):
                            self._r4[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self._s4[i][j] = 0
                        else:
                            self._r1[i][j] = 0
                else:
                    if y == 0:
                        self._r3[i][j] = 0
                    else:
                        angle = np.arctan(y/x)
                        if angle < (- 3 * np.pi / 8):
                            self._r1[i][j] = 0
                        elif angle < (- np.pi / 8):
                            self._s1[i][j] = 0
                        elif angle < (np.pi / 8):
                            self._r3[i][j] = 0
                        elif angle < (3 * np.pi / 8):
                            self._s3[i][j] = 0
                        else:
                            self._r2[i][j] = 0

if __name__ == "__main__":
    masker = Masker([5, 7])
    print("Region r1:")
    print(masker.r1)
    print("Region r2:")
    print(masker.r2)
    print("Region r3:")
    print(masker.r3)
    print("Region r4:")
    print(masker.r4)
    print("Region s1:")
    print(masker.s1)
    print("Region s2:")
    print(masker.s2)
    print("Region s3:")
    print(masker.s3)
    print("Region s4:")
    print(masker.s4)
