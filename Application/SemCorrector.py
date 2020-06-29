#   File:   SemCorrector.py
# 
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement an automatic focusing and astigmatism correction algorithm.

import time
import numpy.ma as ma
import matplotlib.pyplot as plt

from Segmenter import Segmenter
from SemController import SemController
from SemImage import SemImage

class SemCorrector():

    segmenter = None

    wdIters = []
    sxIters = []
    syIters = []

    wdStep = 0.02 # In mm
    wdOffset = 0.10 # In mm.
    dP_threshold = 0.05
    sxyStep = 5
    dP_rs_threshold = 0.002

    xOffset = 512
    yOffset = 256
    width = 256
    height = 256

    focusCorrected = False
    stigmaCorrected = False

    def __init__(self):
        self.sem = SemController()
        self.segmenter = Segmenter([self.width, self.height])

        self.sem().Execute("CMD_MODE_REDUCED")
        self.sem().Set("AP_RED_RASTER_POSN_X", str(self.xOffset))
        self.sem().Set("AP_RED_RASTER_POSN_Y", str(self.yOffset))
        self.sem().Set("AP_RED_RASTER_W", str(self.width))
        self.sem().Set("AP_RED_RASTER_H", str(self.height))

    def start(self):
        iters = range(20)
        for _ in iters:
            self.iterate()

        plt.figure()
        plt.subplot(211)
        plt.plot(iters, self.wdIters, 'r^')
        plt.ylabel('Working Distance')
        plt.subplot(212)
        plt.plot(iters, self.sxIters, 'g^', label='Stigmator X')
        plt.plot(iters, self.syIters, 'b^', label='Stigmator Y')
        plt.xlabel('Iteration')
        plt.ylabel('Stigmator Setting')
        plt.legend(loc='upper right')
        plt.show()

    def iterate(self):
        print("--------------------")
        print(" ")
        print("Start iteration.")
        wd = self.sem().Get("AP_WD", 0.0)[1] * 1000   # In mm.
        sx = self.sem().Get("AP_STIG_X", 0.0)[1]
        sy = self.sem().Get("AP_STIG_Y", 0.0)[1]
        ft = self.sem().Get("AP_FRAME_TIME", 0.0)[1] / 1000 # In seconds.
        print(" ")
        print("Initial settings: ")
        print("Working distance: ", wd, "mm")
        print("Stigmator X:      ", sx)
        print("Stigmator Y:      ", sy)
        print("Frame time:       ", ft, "seconds")
        self.wdIters.append(wd)
        self.sxIters.append(sx)
        self.syIters.append(sy)

        self.sem().Set("AP_WD", str(wd-self.wdOffset))
        time.sleep(3*ft)
        imageUf = SemImage.create(self.sem.grabImage(self.xOffset, self.yOffset, self.width, self.height))
        imageUf.applyHanning()
        imageUf.updateFft()
        P_uf, P_r12_uf, P_r34_uf, P_s12_uf, P_s34_uf = self.segmentFft(imageUf.fft)
        print(" ")
        print("Underfocused image FFT:")
        print("P_uf:     ", P_uf)
        print("P_r12_uf: ", P_r12_uf)
        print("P_r34_uf: ", P_r34_uf)
        print("P_s12_uf: ", P_s12_uf)
        print("P_s34_uf: ", P_s34_uf)

        self.sem().Set("AP_WD", str(wd+self.wdOffset))
        time.sleep(3*ft)       
        imageOf = SemImage.create(self.sem.grabImage(self.xOffset, self.yOffset, self.width, self.height))
        imageOf.applyHanning()
        imageOf.updateFft()
        P_of, P_r12_of, P_r34_of, P_s12_of, P_s34_of = self.segmentFft(imageOf.fft)
        print(" ")
        print("Overfocused image FFT:")
        print("P_of:     ", P_of)
        print("P_r12_of: ", P_r12_of)
        print("P_r34_of: ", P_r34_of)
        print("P_s12_of: ", P_s12_of)
        print("P_s34_of: ", P_s34_of)

        self.sem().Set("AP_WD", str(wd))

        dP = (P_of - P_uf) / (P_of + P_uf)
        dP_r12 = (P_r12_of - P_r12_uf) / (P_r12_of + P_r12_uf)
        dP_r34 = (P_r34_of - P_r34_uf) / (P_r34_of + P_r34_uf)
        dP_s12 = (P_s12_of - P_s12_uf) / (P_s12_of + P_s12_uf)
        dP_s34 = (P_s34_of - P_s34_uf) / (P_s34_of + P_s34_uf)
        print(" ")
        print("Image FFT differences:")
        print("dP:     ", dP)
        print("dP_r12: ", dP_r12)
        print("dP_r34: ", dP_r34)
        print("dP_s12: ", dP_s12)
        print("dP_s34: ", dP_s34)

        if not self.focusCorrected:
            if abs(dP) > self.dP_threshold:
                self.adjustFocus(dP, wd)        
            else:
                self.focusCorrected = True

        if self.focusCorrected:
            if abs(dP_r12) > self.dP_rs_threshold or abs(dP_r34) > self.dP_rs_threshold:
                self.adjustStigmaX(dP_r12, dP_r34, sx)
            # elif abs(dP_s12) > self.dP_rs_threshold or abs(dP_s34) > self.dP_rs_threshold:
            #     self.adjustStigmaY(dP_s12, dP_s34, sy)

        time.sleep(3 * ft)

    def segmentFft(self, fft):
        fft = fft > 3000
        P = fft.sum()
        P_r1 = ma.array(fft, mask=self.segmenter.r1).sum()
        P_r2 = ma.array(fft, mask=self.segmenter.r2).sum()
        P_r3 = ma.array(fft, mask=self.segmenter.r3).sum()
        P_r4 = ma.array(fft, mask=self.segmenter.r4).sum()
        P_s1 = ma.array(fft, mask=self.segmenter.s1).sum()
        P_s2 = ma.array(fft, mask=self.segmenter.s2).sum()
        P_s3 = ma.array(fft, mask=self.segmenter.s3).sum()
        P_s4 = ma.array(fft, mask=self.segmenter.s4).sum()
        P_r12 = P_r1 + P_r2
        P_r34 = P_r3 + P_r4
        P_s12 = P_s1 + P_s2
        P_s34 = P_s3 + P_s4
        return P, P_r12, P_r34, P_s12, P_s34

    def adjustFocus(self, dP, wd):
        print(" ")
        if dP > 0:
            self.sem().Set("AP_WD", str(wd+self.wdStep))
            print("Increased working distance.")
        else:
            self.sem().Set("AP_WD", str(wd-self.wdStep))
            print("Decreased working distance.")

    def adjustStigmaX(self, dP_r12, dP_r34, sx):
        # if dP_r12 > 0 and dP_r34 < 0:
        if dP_r12 - dP_r34 > self.dP_rs_threshold:
            self.sem().Set("AP_STIG_X", str(sx-self.sxyStep))
            print(" ")
            print("Decreased stigmator X.")
        # elif dP_r12 < 0 and dP_r34 > 0:
        elif dP_r34 - dP_r12 > self.dP_rs_threshold:
            self.sem().Set("AP_STIG_X", str(sx+self.sxyStep))
            print(" ")
            print("Increased stigmator X.")

    def adjustStigmaY(self, dP_s12, dP_s34, sy):
        # if dP_s12 > 0 and dP_s34 < 0:
        if dP_s12 - dP_s34 > self.dP_rs_threshold:
            self.sem().Set("AP_STIG_Y", str(sy-self.sxyStep))
            print(" ")
            print("Decreased stigmator Y.")
        # elif dP_s12 < 0 and dP_s34 > 0:
        elif dP_s34 - dP_s12 > self.dP_rs_threshold:
            self.sem().Set("AP_STIG_Y", str(sy+self.sxyStep))
            print(" ")
            print("Increased stigmator Y.")

if __name__ == "__main__":
    semCorrector = SemCorrector()
    semCorrector.start()
