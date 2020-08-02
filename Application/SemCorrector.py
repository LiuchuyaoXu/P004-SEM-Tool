#   File:   SemCorrector.py
# 
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement an algorithm for automatically correcting the focusing and astigmatism of an SEM.

import time

from SemImage import SemImage
from Segmenter import Segmenter

class SemCorrector:

    rasterX = 512
    rasterY = 256
    rasterWidth = 256
    rasterHeight = 256

    stigmatorStep = 5 # In per cent.
    workingDistanceStep = 0.02 # In mm.
    workingDistanceOffset = 0.02 # In mm.

    stigmatorIterationsX = []
    stigmatorIterationsY = []
    workingDistanceIterations = []

    dP_threshold = 0.05
    dP_r_s_threshold = 0.002

    stigmatorCorrected = False
    workingDistanceCorrected = False

    def __init__(self, semController, validFftRegion):
        self.sem = semController
        self.validFftRegion = validFftRegion
        self.segmenter = Segmenter([validFftRegion.width, validFftRegion.height])

        self.sem().Execute("CMD_MODE_REDUCED")
        self.sem().Set("AP_RED_RASTER_POSN_X", str(self.rasterX))
        self.sem().Set("AP_RED_RASTER_POSN_Y", str(self.rasterY))
        self.sem().Set("AP_RED_RASTER_W", str(self.rasterWidth))
        self.sem().Set("AP_RED_RASTER_H", str(self.rasterHeight))

    def iterate(self):
        print("--------------------")

        print(" ")
        print("Start a new iteration.")
        wd = self.sem().Get("AP_WD", 0.0)[1] * 1000 # In mm.
        sx = self.sem().Get("AP_STIG_X", 0.0)[1] # In per cent.
        sy = self.sem().Get("AP_STIG_Y", 0.0)[1] # In per cent.
        ft = self.sem().Get("AP_FRAME_TIME", 0.0)[1] / 1000 # In s.
        self.workingDistanceIterations.append(wd)
        self.stigmatorIterationsX.append(sx)
        self.stigmatorIterationsY.append(sy)
        print("Initial settings: ")
        print("Working distance: ${} mm.".format(wd))
        print("Stigmator X:      ${}.".format(sx))
        print("Stigmator Y:      ${}.".format(sy))
        print("Frame time:       ${} s.".format(ft))

        self.sem().Set("AP_WD", str(wd-self.workingDistanceOffset))
        time.sleep(2*ft)
        imageUf = SemImage.create(self.sem.grabImage(self.rasterX, self.rasterY, self.rasterWidth, self.rasterHeight))
        imageUf.applyHanning()
        imageUf.updateFft()
        imageUf.clipFft(min=0, max=65535)
        x = self.validFftRegion.x
        y = self.validFftRegion.y
        width = self.validFftRegion.width
        height = self.validFftRegion.height
        fft = imageUf.fft[x:x+width, y:y+height]
        P_uf, P_uf_r12, P_uf_r34, P_uf_s12, P_uf_s34 = self.segmenter.calculateSums(fft)
        print(" ")
        print("FFT of the underfocused image:")
        print("P_uf:     ", P_uf)
        print("P_uf_r12: ", P_uf_r12)
        print("P_uf_r34: ", P_uf_r34)
        print("P_uf_s12: ", P_uf_s12)
        print("P_uf_s34: ", P_uf_s34)

        self.sem().Set("AP_WD", str(wd+self.workingDistanceOffset))
        time.sleep(2*ft)       
        imageOf = SemImage.create(self.sem.grabImage(self.rasterX, self.rasterY, self.rasterWidth, self.rasterHeight))
        imageOf.applyHanning()
        imageOf.updateFft()
        imageOf.clipFft(min=0, max=65535)
        x = self.validFftRegion.x
        y = self.validFftRegion.y
        width = self.validFftRegion.width
        height = self.validFftRegion.height
        fft = imageOf.fft[x:x+width, y:y+height]
        P_of, P_of_r12, P_of_r34, P_of_s12, P_of_s34 = self.segmenter.calculateSums(fft)
        print(" ")
        print("FFT of the overfocused image:")
        print("P_of:     ", P_of)
        print("P_of_r12: ", P_of_r12)
        print("P_of_r34: ", P_of_r34)
        print("P_of_s12: ", P_of_s12)
        print("P_of_s34: ", P_of_s34)

        dP = (P_of - P_uf)
        dP_r12 = (P_of_r12 - P_uf_r12)
        dP_r34 = (P_of_r34 - P_uf_r34)
        dP_s12 = (P_of_s12 - P_uf_s12)
        dP_s34 = (P_of_s34 - P_uf_s34)
        print(" ")
        print("Differences in FFT of the images:")
        print("dP:     ", dP)
        print("dP_r12: ", dP_r12)
        print("dP_r34: ", dP_r34)
        print("dP_s12: ", dP_s12)
        print("dP_s34: ", dP_s34)
        self.sem().Set("AP_WD", str(wd))

        if not self.workingDistanceCorrected:
            if abs(dP) > self.dP_threshold:
                self.adjustWorkingDistance(dP, wd)        
            else:
                self.workingDistanceCorrected = True

        if not self.stigmatorCorrected:
            if abs(dP_r12) > self.dP_r_s_threshold or abs(dP_r34) > self.dP_r_s_threshold:
                self.adjustStigmatorX(dP_r12, dP_r34, sx)
            elif abs(dP_s12) > self.dP_r_s_threshold or abs(dP_s34) > self.dP_r_s_threshold:
                self.adjustStigmatorY(dP_s12, dP_s34, sy)
            else:
                self.stigmatorCorrected = True

        time.sleep(2*ft)

    def adjustWorkingDistance(self, dP, wd):
        print(" ")
        if dP > 0:
            self.sem().Set("AP_WD", str(wd+self.workingDistanceStep))
            print("Increased working distance.")
        else:
            self.sem().Set("AP_WD", str(wd-self.workingDistanceStep))
            print("Decreased working distance.")

    def adjustStigmatorX(self, dP_r12, dP_r34, sx):
        print(" ")
        if dP_r12 - dP_r34 > self.dP_r_s_threshold:
            self.sem().Set("AP_STIG_X", str(sx-self.stigmatorStep))
            print("Decreased stigmator X.")
        elif dP_r34 - dP_r12 > self.dP_r_s_threshold:
            self.sem().Set("AP_STIG_X", str(sx+self.stigmatorStep))
            print("Increased stigmator X.")

    def adjustStigmatorY(self, dP_s12, dP_s34, sy):
        print(" ")
        if dP_s12 - dP_s34 > self.dP_r_s_threshold:
            self.sem().Set("AP_STIG_Y", str(sy-self.stigmatorStep))
            print("Decreased stigmator Y.")
        elif dP_s34 - dP_s12 > self.dP_r_s_threshold:
            self.sem().Set("AP_STIG_Y", str(sy+self.stigmatorStep))
            print("Increased stigmator Y.")

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from SemController import SemController

    corrector = SemCorrector(SemController(), [0, 0, 1024, 768])
    iterations = range(10)
    for _ in iterations:
        corrector.iterate()

    plt.figure()

    plt.subplot(211)
    plt.plot(iterations, corrector.workingDistanceIterations, 'r^')
    plt.ylabel('Working Distance')

    plt.subplot(212)
    plt.plot(iterations, corrector.stigmatorIterationsX, 'g^', label='Stigmator X')
    plt.plot(iterations, corrector.stigmatorIterationsY, 'b^', label='Stigmator Y')
    plt.xlabel('Iteration')
    plt.ylabel('Stigmator Setting')

    plt.legend(loc='upper right')
    plt.show()
