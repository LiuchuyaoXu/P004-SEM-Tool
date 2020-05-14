#   File:   SemImageGrabber.py
#
#   Brief:  Implement the SemImageGrabber class which helps grab images from the SEM.
# 
#   Author: Liuchuyao Xu, 2020

import os
import numpy as np
from PIL import Image
from SemImage import SemImage

class SemImageGrabber():
    def __init__(self, sem=None, imageDir=None):
        if sem:
            self.sem = sem
        else:
            self.sem = None
            self.dir = imageDir
            self.list = os.listdir(imageDir)
            self.index = 1

    def __call__(self):
        if self.sem:
            image = np.asarray(self.sem.img_array)
            return SemImage(image)
        else:
            if self.index >= len(self.list):
                self.index = 0
            image = Image.open(os.path.join(self.dir, self.list[self.index]))
            image = np.asarray(image)
            self.index += 1
            return SemImage(image)