#   File:   SemCorrector.py
# 
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement an algorithm for automatically correcting the focusing and astigmatism of an SEM.

import time
import numpy
import threading
import matplotlib.pyplot as plt

import MatrixWindows
from SemImage import SemImage

class SemCorrector:

    def __init__(self, semController):
        self.sem = semController

        self.rasterX = 0
        self.rasterY = 0
        self.rasterWidth = 1024
        self.rasterHeight = 768

        self.stigmatorStep = 5 # In per cent.
        self.workingDistanceStep = 0.02 # In mm.
        self.workingDistanceOffset = 0.02 # In mm.

        self.frameWaitTimeFactor = 1.5

        self.applyHann = True
        self.applyDiscMask = False

        self.discMaskRadius = 100

        self.defocusingThreshold = 0.05
        self.astigmatismThreshold = 0.002

        self.numberOfIterations = 1
        self.wdIterations = None
        self.sxIterations = None
        self.syIterations = None

        self.stigmatorCorrected = False
        self.workingDistanceCorrected = False

    def iterate(self):
        wd = self.sem.sem().Get("AP_WD", 0.0)[1] * 1000 # In mm.
        sx = self.sem.sem().Get("AP_STIG_X", 0.0)[1] # In per cent.
        sy = self.sem.sem().Get("AP_STIG_Y", 0.0)[1] # In per cent.

        self.wdIterations = [wd]
        self.sxIterations = [sx]
        self.syIterations = [sy]

        for _ in range(self.numberOfIterations):
            print("--------------------")
            
            self.sem.imageX = self.rasterX
            self.sem.imageY = self.rasterY
            self.sem.imageWidth = self.rasterWidth
            self.sem.imageHeight = self.rasterHeight

            wd = self.sem.sem().Get("AP_WD", 0.0)[1] * 1000 # In mm.
            sx = self.sem.sem().Get("AP_STIG_X", 0.0)[1] # In per cent.
            sy = self.sem.sem().Get("AP_STIG_Y", 0.0)[1] # In per cent.
            ft = self.sem.sem().Get("AP_FRAME_TIME", 0.0)[1] / 1000 # In s.
            print("SemCorrector: start iteration.")
            print("Initial settings: ")
            print("Working distance {} mm.".format(wd))
            print("Stigmator X      {}.".format(sx))
            print("Stigmator Y      {}.".format(sy))
            print("Frame time       {} s.".format(ft))

            segmentMasks = MatrixWindows.segmentMasks(self.rasterWidth, self.rasterHeight)
            r12 = segmentMasks[0]
            s12 = segmentMasks[1]
            r34 = segmentMasks[2]
            s34 = segmentMasks[3]

            self.sem.sem().Set("AP_WD", str(wd - self.workingDistanceOffset))
            time.sleep(self.frameWaitTimeFactor * ft)
            image = self.sem.grabImage()
            imageUf = SemImage(image)
            if self.applyHann:
                imageUf.applyHann()
            fft = imageUf.fft()
            if self.applyDiscMask:
                discMask = MatrixWindows.discMask(self.rasterWidth, self.rasterHeight, self.discMaskRadius)
                fft = numpy.multiply(fft, discMask)
            P_uf = fft.sum()
            P_uf_r12 = numpy.multiply(fft, r12).sum()
            P_uf_r34 = numpy.multiply(fft, r34).sum()
            P_uf_s12 = numpy.multiply(fft, s12).sum()
            P_uf_s34 = numpy.multiply(fft, s34).sum()
            print("FFT of the underfocused image:")
            print("P_uf     {}.".format(P_uf))
            print("P_uf_r12 {}.".format(P_uf_r12))
            print("P_uf_r34 {}.".format(P_uf_r34))
            print("P_uf_s12 {}.".format(P_uf_s12))
            print("P_uf_s34 {}.".format(P_uf_s34))

            self.sem.sem().Set("AP_WD", str(wd + self.workingDistanceOffset))
            time.sleep(self.frameWaitTimeFactor * ft)
            image = self.sem.grabImage()
            imageOf = SemImage(image)
            if self.applyHann:
                imageOf.applyHann()
            fft = imageOf.fft()
            if self.applyDiscMask:
                discMask = MatrixWindows.discMask(self.rasterWidth, self.rasterHeight, self.discMaskRadius)
                fft = numpy.multiply(fft, discMask)
            P_of = fft.sum()
            P_of_r12 = numpy.multiply(fft, r12).sum()
            P_of_r34 = numpy.multiply(fft, r34).sum()
            P_of_s12 = numpy.multiply(fft, s12).sum()
            P_of_s34 = numpy.multiply(fft, s34).sum()
            print("FFT of the overfocused image:")
            print("P_of     {}.".format(P_of))
            print("P_of_r12 {}.".format(P_of_r12))
            print("P_of_r34 {}.".format(P_of_r34))
            print("P_of_s12 {}.".format(P_of_s12))
            print("P_of_s34 {}.".format(P_of_s34))

            dP = (P_of - P_uf)
            dP_r12 = (P_of_r12 - P_uf_r12)
            dP_r34 = (P_of_r34 - P_uf_r34)
            dP_s12 = (P_of_s12 - P_uf_s12)
            dP_s34 = (P_of_s34 - P_uf_s34)
            print("Differences in FFT of the images:")
            print("dP:     {}.".format(dP))
            print("dP_r12: {}.".format(dP_r12))
            print("dP_r34: {}.".format(dP_r34))
            print("dP_s12: {}.".format(dP_s12))
            print("dP_s34: {}.".format(dP_s34))

            self.sem.sem().Set("AP_WD", str(wd))

            if not self.workingDistanceCorrected:
                if abs(dP) > self.defocusingThreshold:
                    self.adjustWorkingDistance(dP, wd)        
                else:
                    self.workingDistanceCorrected = True

            if not self.stigmatorCorrected:
                if abs(dP_r12) > self.astigmatismThreshold or abs(dP_r34) > self.astigmatismThreshold:
                    self.adjustStigmatorX(dP_r12, dP_r34, sx)
                elif abs(dP_s12) > self.astigmatismThreshold or abs(dP_s34) > self.astigmatismThreshold:
                    self.adjustStigmatorY(dP_s12, dP_s34, sy)
                else:
                    self.stigmatorCorrected = True

            wd = self.sem.sem().Get("AP_WD", 0.0)[1] * 1000 # In mm.
            sx = self.sem.sem().Get("AP_STIG_X", 0.0)[1] # In per cent.
            sy = self.sem.sem().Get("AP_STIG_Y", 0.0)[1] # In per cent.
            ft = self.sem.sem().Get("AP_FRAME_TIME", 0.0)[1] / 1000 # In s.
            print("Final settings: ")
            print("Working distance {} mm.".format(wd))
            print("Stigmator X      {}.".format(sx))
            print("Stigmator Y      {}.".format(sy))
            print("Frame time       {} s.".format(ft))

            self.wdIterations.append(wd)
            self.sxIterations.append(sx)
            self.syIterations.append(sy)
            
    def adjustWorkingDistance(self, dP, wd):
        if dP > 0:
            self.sem.sem().Set("AP_WD", str(wd + self.workingDistanceStep))
            print("Increased working distance.")
        else:
            self.sem.sem().Set("AP_WD", str(wd - self.workingDistanceStep))
            print("Decreased working distance.")

    def adjustStigmatorX(self, dP_r12, dP_r34, sx):
        if dP_r12 - dP_r34 > self.astigmatismThreshold:
            self.sem.sem().Set("AP_STIG_X", str(sx - self.stigmatorStep))
            print("Decreased stigmator X.")
        elif dP_r34 - dP_r12 > self.astigmatismThreshold:
            self.sem.sem().Set("AP_STIG_X", str(sx + self.stigmatorStep))
            print("Increased stigmator X.")

    def adjustStigmatorY(self, dP_s12, dP_s34, sy):
        if dP_s12 - dP_s34 > self.astigmatismThreshold:
            self.sem.sem().Set("AP_STIG_Y", str(sy - self.stigmatorStep))
            print("Decreased stigmator Y.")
        elif dP_s34 - dP_s12 > self.astigmatismThreshold:
            self.sem.sem().Set("AP_STIG_Y", str(sy + self.stigmatorStep))
            print("Increased stigmator Y.")

    def guiRun(self):
        thread = threading.Thread(target=self.iterate)
        thread.start()

    def guiPlotSettings(self):
        if self.wdIterations is None:
            print('SemCorrector: run a few iterations first.')
            return
        plt.figure()
        plt.subplot(211)
        plt.plot(range(self.numberOfIterations + 1), self.wdIterations, 'r^')
        plt.ylabel('Working Distance')
        plt.subplot(212)
        plt.plot(range(self.numberOfIterations + 1), self.sxIterations, 'g^', label='Stigmator X')
        plt.plot(range(self.numberOfIterations + 1), self.syIterations, 'b^', label='Stigmator Y')
        plt.xlabel('Iteration')
        plt.ylabel('Stigmator Setting')
        plt.legend(loc='upper right')
        plt.show()

if __name__ == '__main__':
    import sys
    from PySide2 import QtWidgets
    from SemController import SemController
    from ObjectInspector import ObjectInspector

    app = QtWidgets.QApplication(sys.argv)
    semc = ObjectInspector(SemCorrector(SemController()))
    semc.show()
    sys.exit(app.exec_())
    