# Author: Liuchuyao Xu, 2020
#
# Brief: Implement a class for the automatic focusing and astigmatism correction algorithm.

import time
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import threading

from PIL import Image

from Masker import Masker
from SemImage import SemImage

class SemCorrector(threading.Thread):
    def __init__(self, sem):
        try:
            self.sem = sem
            sv = self.sem.GetState("SV_VERSION")
            print("SemCorrector initialised.")
            print("SEM SV version: ", sv, "\n")
        except:
            raise TypeError("SemCorrector was not initialised with an SEM_API instance.")

        self.sem.UpdateImage_Start()

        self.focusStep = 0.02 # In mm
        self.focusOffset = 0.10 # In mm.
        self.focusThreshold = 0.002
        self.stigmaStep = 0.50
        self.stigmaThreshold = 0.02
        self.stigmaDiffThreshold = 0.05

        self.masker = Masker([1024, 768])

        self.finished = False

        self.focusIters = []
        self.stigmaXIters = []
        self.stigmaYIters = []

    def run(self):
        image = Image.fromarray(np.asarray(self.sem.img_array), 'L')
        image.save("initial.png")

        iters = np.arange(0, 20)
        for i in iters:
            self.start()

        plt.figure()

        plt.subplot(211)
        plt.ylabel('Focus')
        plt.plot(iters, self.focusIters, 'r^')

        plt.subplot(212)
        plt.xlabel('Iteration')
        plt.ylabel('Stigma')
        plt.plot(iters, self.stigmaXIters, 'g^', label='x')
        plt.plot(iters, self.stigmaYIters, 'b^', label='y')
        plt.legend(loc='upper right')

        plt.show()

        image = Image.fromarray(np.asarray(self.sem.img_array), 'L')
        image.save("final.png")

    def start(self):
        print("--------------------")
        print("Start iteration.")
        F = self.sem.GetValue("AP_WD") * 1000   # In mm.
        Sx = self.sem.GetValue("AP_STIG_X")
        Sy = self.sem.GetValue("AP_STIG_Y")
        Ft = self.sem.GetValue("AP_FRAME_TIME")  #added by Bernie & David
        print(" ")
        print("Initial settings:")
        print("Focus: ", F)
        print("Sx: ", Sx)
        print("Sy ", Sy)
        print("Cycle time  ", Ft/1000, "seconds")  #added by Bernie & David
        self.focusIters.append(F)
        self.stigmaXIters.append(Sx)
        self.stigmaYIters.append(Sy)

        self.sem.SetValue("AP_WD", str(F - self.focusOffset))
        time.sleep(Ft/1000)
        imageUF = SemImage.create(np.asarray(self.sem.img_array))
        imageUF.applyHanning()
        Puf, Pr12uf, Pr34uf, Ps12uf, Ps34uf = self.getFftSegments(self.masker, imageUF.fft)
        print(" ")
        print("Underfocus image FFT:")
        print("Puf: ", Puf)
        print("Pr12uf: ", Pr12uf)
        print("Pr34uf: ", Pr34uf)
        print("Ps12uf: ", Ps12uf)
        print("Ps34uf: ", Ps34uf)

        self.sem.SetValue("AP_WD", str(F + self.focusOffset))
        time.sleep(Ft/1000)       
        imageOF = SemImage.create(np.asarray(self.sem.img_array))
        imageOF.applyHanning()
        Pof, Pr12of, Pr34of, Ps12of, Ps34of = self.getFftSegments(self.masker, imageOF.fft)
        print(" ")
        print("Overfocus image FFT:")
        print("Pof: ", Pof)
        print("Pr12of: ", Pr12of)
        print("Pr34of: ", Pr34of)
        print("Ps12of: ", Ps12of)
        print("Ps34of: ", Ps34of)

        dP = (Pof - Puf) / (Pof + Puf)
        dPr12 = (Pr12of - Pr12uf) / (Pr12of + Pr12uf)
        dPr34 = (Pr34of - Pr34uf) / (Pr34of + Pr34uf)
        dPs12 = (Ps12of - Ps12uf) / (Ps12of + Ps12uf)
        dPs34 = (Ps34of - Ps34uf) / (Ps34of + Ps34uf)
        Ax = abs(dPr12 - dPr34)
        Ay = abs(dPs12 - dPs34)
        print(" ")
        print("Differences:")
        print("dP: ", dP)
        print("dPr12: ", dPr12)
        print("dPr34: ", dPr34)
        print("dPs12: ", dPs12)
        print("dPs34: ", dPs34)

        if abs(dP) > self.focusThreshold:
            self.adjustFocus(dP, F)
            return
        
        if abs(dPr12) < self.stigmaThreshold and abs(dPr34) < self.stigmaThreshold and Ax < self.stigmaDiffThreshold:
            stigmaXCorrected = True
        else:
            stigmaXCorrected = False

        if abs(dPs12) < self.stigmaThreshold and abs(dPs34) < self.stigmaThreshold and Ay < self.stigmaDiffThreshold:
            stigmaYCorrected = True
        else:
            stigmaYCorrected = False

        if not stigmaXCorrected:
            if stigmaYCorrected:
                self.adjustStigmaX(dPr12, dPr34, Sx)
                return
            elif Ax >= Ay:
                self.adjustStigmaX(dPr12, dPr34, Sx)
                return
            else:
                self.adjustStigmaY(dPs12, dPs34, Sy)
                return
        elif not stigmaYCorrected:
                self.adjustStigmaY(dPs12, dPs34, Sy)
                return
        else:
            self.sem.SetValue("AP_WD", str(F))
            self.finished = True
            return

    def getFftSegments(self, masker, fft):
        fft = fft > 50000
        P = fft.sum()
        r1 = ma.array(fft, mask=masker.r1).sum()
        r2 = ma.array(fft, mask=masker.r2).sum()
        r3 = ma.array(fft, mask=masker.r3).sum()
        r4 = ma.array(fft, mask=masker.r4).sum()
        s1 = ma.array(fft, mask=masker.s1).sum()
        s2 = ma.array(fft, mask=masker.s2).sum()
        s3 = ma.array(fft, mask=masker.s3).sum()
        s4 = ma.array(fft, mask=masker.s4).sum()
        Pr12 = r1 + r2
        Pr34 = r3 + r4
        Ps12 = s1 + s2
        Ps34 = s3 + s4
        return P, Pr12, Pr34, Ps12, Ps34

    def adjustFocus(self, dP, F):
        print(" ")
        print("Adjust focus.")
        if dP > 0:
            self.sem.SetValue("AP_WD", str(F + self.focusStep))
        else:
            self.sem.SetValue("AP_WD", str(F - self.focusStep))

    def adjustStigmaX(self, dPr12, dPr34, Sx):
        print(" ")
        print("Adjust stigma x.")
        if dPr12 > 0 and dPr34 < 0:
            self.sem.SetValue("AP_STIG_X", str(Sx - self.stigmaStep))
        elif dPr12 < 0 and dPr34 > 0:
            self.sem.SetValue("AP_STIG_X", str(Sx + self.stigmaStep))

    def adjustStigmaY(self, dPs12, dPs34, Sy):
        print(" ")
        print("Adjust stigma y.")
        if dPs12 > 0 and dPs34 < 0:
            self.sem.SetValue("AP_STIG_Y", str(Sy - self.stigmaStep))
        elif dPs12 < 0 and dPs34 > 0:
            self.sem.SetValue("AP_STIG_Y", str(Sy + self.stigmaStep))

if __name__ == "__main__":
    import SEM_API
    
    with SEM_API.SEM_API("remote") as sem:
        semCorrector = SemCorrector(sem)
        start = time.time()
        semCorrector.run()
        end = time.time()
        print("Execution time: ", end - start, "s")
