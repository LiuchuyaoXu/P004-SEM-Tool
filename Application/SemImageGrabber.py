#   File:   SemImageGrabber.py
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement the SemImageGrabber class.
#           The class helps grab images from either the SEM or a local folder.

import os
from PIL import Image
from SemImage import SemImage

class SemImageGrabber():
    def __init__(self, sem=None, imageDir=None):
        if sem:
            self.sem = sem
            self.sem.UpdateImage_Start()
        else:
            self.sem = None
            self.dir = imageDir
            self.items = os.listdir(imageDir)
            self.index = 0

    def __call__(self):
        if self.sem:
            return SemImage.create(self.sem.img_array)
        else:
            image = Image.open(os.path.join(self.dir, self.items[self.index]))
            self.index += 1
            if self.index >= len(self.items):
                self.index = 0
            return SemImage.create(image)
            