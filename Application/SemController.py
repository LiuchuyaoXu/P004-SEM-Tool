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

import os
import sys
import mmap
from win32com import client

class SemController:

    def __init__(self):
        ole = 'CZ.EmApiCtrl.1'
        self.sem = client.Dispatch(ole)
        self.sem.Initialise()

        self.sem.Grab(0, 0, 1024, 768, 0, 'CZ.MMF')

    def __call__(self):
        return self.sem

    def __del__(self):
        self.mmf.close()
        os.close(self.file)
        self.sem.Grab(0, 0, 0, 0, 0, 'CZ.MMF')

    def grabImage(self, xOffset=0, yOffset=0, width=1024, height=768, reduction=0):
        self.file = os.open('CZ.MMF')
        self.mmf = mmap.mmap(self.file.fileno(), 0)
        return self.mmf

if __name__ == '__main__':
    sem = SemController()
