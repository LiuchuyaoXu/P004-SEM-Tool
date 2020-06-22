#   File:   SemController.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Provides an interface for controlling the SEM.

import sys
import tempfile
from win32com import client
from PIL import Image

class SemController:

    def __init__(self):
        ole = 'CZ.EmApiCtrl.1'
        # sys.argv = ['makepy', ole]
        # client.makepy.main()

        self.mic = client.Dispatch(ole)
        self.mic.InitialiseRemoting()

    def getValue(self, name):
        return self.mic.Get(name, 0.0)

    def setValue(self, name, value):
        return self.mic.Set(name, str(value))

    def grabImage(self):
        filename = tempfile.TemporaryFile(suffix='.bmp').name
        self.mic.Grab(0, 0, 1024, 768, 0, filename)
        image = Image.open(filename)
        return image

    # @property
    # def AP_WD(self):
    #     return self.mic.Get('AP_WD', 0.0)

    # @property
    # def AP_STIG_X(self):
    #     return self.mic.Get('AP_STIG_X', 0.0)

    # @property
    # def AP_STIG_Y(self):
    #     return self.mic.Get('AP_STIG_Y', 0.0)

    # @AP_WD.setter
    # def AP_WD(self, value):
    #     return self.mic.Set('AP_WD', str(value))

    # @AP_STIG_X.setter
    # def AP_STIG_X(self, value):
    #     return self.mic.Set('AP_STIG_X', str(value))

    # @AP_STIG_Y.setter
    # def AP_STIG_Y(self, value):
    #     return self.mic.Set('AP_STIG_Y', str(value))

if __name__ == '__main__':
    sem = SemController()

    res = sem.setValue("AP_RED_RASTER_POSN_X", 256)
    res = sem.setValue("AP_RED_RASTER_POSN_Y", 128)
    res = sem.setValue("AP_RED_RASTER_W", 512)
    res = sem.setValue("AP_RED_RASTER_H", 512)
