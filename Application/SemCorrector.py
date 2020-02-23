# Brief: Implement a class for the automatic focusing and astigmatism correction algorithm.
#
# Author: Liuchuyao Xu, 2020

import numpy as np

from SemImage import SemImage

class SemCorrector:
    def __init__(self, sem, focusStep=0.000001):
        self.sem = sem
        try:
            version = self.sem.getState("SV_VERSION")
        except:
            raise TypeError("SemCorrector was not initialised with an SEM_API instance.")

        self.focusStep = focusStep

    def start(self):
        self.focus = self.sem.getValue("AP_WD")
        self.stigX = self.sem.getValue("AP_STIG_X")
        self.stigY = self.sem.getValue("AP_STIG_Y")

        self.sem.setValue("AP_WD", self.focus - self.focusStep)
        self.imageUnderFocus = SemImage(np.asarray(sem.img_array))
        self.sem.setValue("AP_WD", self.focus + self.focusStep)
        self.imageOverFocus  = SemImage(np.asarray(sem.img_array))

    def adjustFocus(self):
        pass
    
    def adjustStigmaX(self):
        pass

    def adjustStigmasY(self):
        pass

if __name__ == "__main__":
    import time
    import SEM_API
    
    with SEM_API.SEM_API("remote") as sem:
        semCorrector = SemCorrector(sem)
        start = time.time()
        semCorrector.start()
        end = time.time()
        print("Execution time: ", end - start, "s")
        print("SEM focus: ", semCorrector.focus)
        print("SEM X stigma: ", semCorrector.stigX)
        print("SEM Y stigma: ", semCorrector.stigY)
