#   File:   SemController.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement the SemController class.
#           The class gives access to the API of the SEM
#           The class provides functions that the API does not support directly.
#
#   Abbreviations:
#           ole     Microsoft Object Linking and Embedding document

import sys
import tempfile
from win32com import client
from PIL import Image

class SemController:

    def __init__(self):
        ole = 'CZ.EmApiCtrl.1'
        self.sem = client.Dispatch(ole)
        self.sem.InitialiseRemoting()

    def __call__(self):
        return self.sem

    def grabImage(self, xOffset=0, yOffset=0, width=1024, height=768, reduction=0):
        filename = tempfile.TemporaryFile(suffix='.bmp').name
        self.sem.Grab(xOffset, yOffset, width, height, reduction, filename)
        image = Image.open(filename)
        return image

if __name__ == '__main__':
    sem = SemController()
