# Author: Liuchuyao Xu, 2020
#
# Brief: Implement a class for the automatic focusing and astigmatism correction algorithm.

import time
import numpy as np
import numpy.ma as ma

from Masker import Masker
from SemImage import SemImage

class SemCorrector:
    def __init__(self, sem):
        self.sem = sem
        try:
            version = self.sem.getState("SV_VERSION")
        except:
            raise TypeError("SemCorrector was not initialised with an SEM_API instance.")

        self.focusStep = 0.1
        self.focusOffset = 0.05     # In mm.
        self.focusThreshold = 0.05  # In percentage.
        self.astigmaStep = 0.1
        self.astigmaThreshold = 0.05
        self.astigmaDiffThreshold = 0.05

        self.masker = Masker([1024, 768])

        self.finished = False

    def correct(self):
        for i in range(0, 10):
            self.start()

    def start(self):
        F = self.sem.getValue("AP_WD") * 1000   # In mm.
        Sx = self.sem.getValue("AP_STIG_X")
        Sy = self.sem.getValue("AP_STIG_Y")

        self.sem.setValue("AP_WD", str(F - self.focusOffset))
        time.sleep(3)
        imageUF = SemImage(np.asarray(self.sem.img_array))
        imageUF.applyHanning()
        Puf, Pr12uf, Pr34uf, Ps12uf, Ps34uf = self.getFftSegments(self.masker, imageUF.fft)

        self.sem.setValue("AP_WD", str(F + self.focusOffset))
        time.sleep(3)
        imageOF = SemImage(np.asarray(self.sem.img_array))
        imageOF.applyHanning()
        Pof, Pr12of, Pr34of, Ps12of, Ps34of = self.getFftSegments(self.masker, imageOF.fft)

        R = (Pof - Puf) / (Pof + Puf)
        dr12 = Pr12of - Pr12uf
        dr34 = Pr34of - Pr34uf
        ds12 = Ps12of - Ps12uf
        ds34 = Ps34of - Ps34uf
        Ax = abs(dr12 - dr34) / 2
        Ay = abs(ds12 - ds34) / 2

        if abs(R) > self.focusThreshold:
            self.adjustFocus(R, F)
            return
        
        if abs(dr12) < self.astigmaStep and abs(dr34) < self.astigmaStep and Ax < self.astigmaDiffThreshold:
            astigmaXCorrected = True

        if abs(ds12) < self.astigmaStep and abs(ds34) < self.astigmaStep and Ay < self.astigmaDiffThreshold:
            astigmaYCorrected = True

        if not astigmaXCorrected:
            if astigmaYCorrected:
                self.adjustAstigmaX(dr12, dr34, Sx)
                return
            elif Ax >= Ay:
                self.adjustAstigmaX(dr12, dr34, Sx)
                return
            else:
                self.adjustAstigmaY(ds12, ds34, Sy)
                return
        elif not astigmaYCorrected:
                self.adjustAstigmaY(ds12, ds34, Sy)
                return
        else:
            self.sem.setValue("AP_WD", str(F))
            self.finished = True
            return

    def getFftSegments(self, masker, fft):
        P = fft.sum()
        r1 = ma.array(fft, mask=masker.r1).sum()
        r2 = ma.array(fft, mask=masker.r2).sum()
        r3 = ma.array(fft, mask=masker.r3).sum()
        r4 = ma.array(fft, mask=masker.r4).sum()
        s1 = ma.array(fft, mask=masker.s1).sum()
        s2 = ma.array(fft, mask=masker.s2).sum()
        s3 = ma.array(fft, mask=masker.s3).sum()
        s4 = ma.array(fft, mask=masker.s4).sum()
        Pr12 = (r1 + r2) / P
        Pr34 = (r3 + r4) / P
        Ps12 = (s1 + s2) / P
        Ps34 = (s3 + s4) / P
        return P, Pr12, Pr34, Ps12, Ps34

    def adjustFocus(self, R, F):
        if R > 0:
            self.sem.setValue("AP_WD", str(F + self.focusStep))
        else:
            self.sem.setValue("AP_WD", str(F - self.focusStep))

    def adjustAstigmaX(self, dr12, dr34, Sx):
        if dr12 > 0 and dr34 < 0:
            self.sem.setValue("AP_STIG_X", Sx - self.astigmaStep)
        elif dr12 < 0 and dr34 > 0:
            self.sem.setValue("AP_STIG_X", Sx + self.astigmaStep)

    def adjustAstigmaY(self, ds12, ds34, Sy):
        if ds12 > 0 and ds34 < 0:
            self.sem.setValue("AP_STIG_Y", Sy - self.astigmaStep)
        elif ds12 < 0 and ds34 > 0:
            self.sem.setValue("AP_STIG_Y", Sy + self.astigmaStep)

if __name__ == "__main__":
    import time
    import SEM_API
    
    with SEM_API.SEM_API("remote") as sem:
        semCorrector = SemCorrector(sem)
        start = time.time()
        semCorrector.correct()
        end = time.time()
        print("Execution time: ", end - start, "s")
