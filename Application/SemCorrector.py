#   File:   SemCorrector.py
# 
#   Author: Liuchuyao Xu, 2020
#
#   Brief: Implement an automatic focusing and astigmatism correction algorithm.

import time
import numpy.ma as ma
import matplotlib.pyplot as plt

import SEM_API
from Segmenter import Segmenter
from SemImage import SemImage

class SemCorrector():

    sem = None
    segmenter = None

    wdIters = []
    sxIters = []
    syIters = []

    wdStep = 0.02 # In mm
    wdOffset = 0.10 # In mm.
    dP_threshold = 0.002
    sxyStep = 0.50
    dP_rs_threshold = 0.02

    def __init__(self, sem):
        self.sem = sem
        self.sem.UpdateImage_Start()
        self.segmenter = Segmenter([1024, 768])

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
        wd = self.sem.GetValue("AP_WD") * 1000   # In mm.
        sx = self.sem.GetValue("AP_STIG_X")
        sy = self.sem.GetValue("AP_STIG_Y")
        ft = self.sem.GetValue("AP_FRAME_TIME") / 1000 # In seconds.
        print(" ")
        print("Initial settings: ")
        print("Working distance: ", wd, "mm")
        print("Stigmator X:      ", sx)
        print("Stigmator Y:      ", sy)
        print("Frame time:       ", ft, "seconds")
        self.wdIters.append(wd)
        self.sxIters.append(sx)
        self.syIters.append(sy)

        self.sem.SetValue("AP_WD", wd-self.wdOffset)
        time.sleep(ft)
        imageUf = SemImage.create(self.sem.img_array)
        imageUf.applyHanning()
        imageUf.updateFft()
        P_uf, P_r12_uf, P_r34_uf, P_s12_uf, P_s34_uf = self.segmentFft(self.segmenter, imageUf.fft)
        print(" ")
        print("Underfocused image FFT:")
        print("P_uf:     ", P_uf)
        print("P_r12_uf: ", P_r12_uf)
        print("P_r34_uf: ", P_r34_uf)
        print("P_s12_uf: ", P_s12_uf)
        print("P_s34_uf: ", P_s34_uf)

        self.sem.SetValue("AP_WD", wd+self.wdOffset)
        time.sleep(ft)       
        imageOf = SemImage.create(self.sem.img_array)
        imageOf.applyHanning()
        imageOf.updateFft()
        P_of, P_r12_of, P_r34_of, P_s12_of, P_s34_of = self.segmentFft(self.segmenter, imageOf.fft)
        print(" ")
        print("Overfocused image FFT:")
        print("P_of:     ", P_of)
        print("P_r12_of: ", P_r12_of)
        print("P_r34_of: ", P_r34_of)
        print("P_s12_of: ", P_s12_of)
        print("P_s34_of: ", P_s34_of)

        self.sem.SetValue("AP_WD", wd)

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

        if abs(dP) > self.dP_threshold:
            self.adjustFocus(dP, wd)        
        elif abs(dP_r12) > self.dP_rs_threshold and abs(dP_r34) > self.dP_rs_threshold:
            self.adjustStigmaX(dP_r12, dP_r34, sx)
        elif abs(dP_s12) > self.dP_rs_threshold and abs(dP_s34) > self.dP_rs_threshold:
            self.adjustStigmaX(dP_s12, dP_s34, sy)

    def segmentFft(self, segmenter, fft):
        fft = fft > 50000
        P = fft.sum()
        P_r1 = ma.array(fft, segmenter.r1).sum()
        P_r2 = ma.array(fft, segmenter.r2).sum()
        P_r3 = ma.array(fft, segmenter.r3).sum()
        P_r4 = ma.array(fft, segmenter.r4).sum()
        P_s1 = ma.array(fft, segmenter.s1).sum()
        P_s2 = ma.array(fft, segmenter.s2).sum()
        P_s3 = ma.array(fft, segmenter.s3).sum()
        P_s4 = ma.array(fft, segmenter.s4).sum()
        P_r12 = P_r1 + P_r2
        P_r34 = P_r3 + P_r4
        P_s12 = P_s1 + P_s2
        P_s34 = P_s3 + P_s4
        return P, P_r12, P_r34, P_s12, P_s34

    def adjustFocus(self, dP, wd):
        print(" ")
        if dP > 0:
            self.sem.SetValue("AP_WD", wd+self.wdStep)
            print("Increased working distance.")
        else:
            self.sem.SetValue("AP_WD", wd-self.wdStep)
            print("Decreased working distance.")

    def adjustStigmaX(self, dP_r12, dP_r34, sx):
        if dP_r12 > 0 and dP_r34 < 0:
            self.sem.SetValue("AP_STIG_X", sx-self.sxyStep)
            print(" ")
            print("Decreased stigmator X.")
        elif dP_r12 < 0 and dP_r34 > 0:
            self.sem.SetValue("AP_STIG_X", sx+self.sxyStep)
            print(" ")
            print("Increased stigmator X.")

    def adjustStigmaY(self, dP_s12, dP_s34, sy):
        if dP_s12 > 0 and dP_s34 < 0:
            self.sem.SetValue("AP_STIG_Y", sy-self.sxyStep)
            print(" ")
            print("Decreased stigmator Y.")
        elif dP_s12 < 0 and dP_s34 > 0:
            self.sem.SetValue("AP_STIG_Y", sy+self.sxyStep)
            print(" ")
            print("Increased stigmator Y.")

if __name__ == "__main__":
    with SEM_API.SEM_API("remote") as sem:
        semCorrector = SemCorrector(sem)
        semCorrector.start()
