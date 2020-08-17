#   File:   SemController.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement the SemController class.
#           The class gives access to the API of the SEM
#           The class provides functions that the API does not directly support.
#
#   Abbreviations:
#           ole     Microsoft Object Linking and Embedding document

import tempfile
from PIL import Image
from win32com import client

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SemController:

    def __init__(self):
        self._sem = None
        self.ole = 'CZ.EmApiCtrl.1'
        self.semInitialised = False

        self.imageX = 0
        self.imageY = 0
        self.imageWidth = 1024
        self.imageHeight = 768
        self.imageReduction = 0

    def sem(self):
        if not self._sem:
            self.initSem()
        return self._sem

    def initSem(self):
        if self.semInitialised:
            return
        self._sem = client.Dispatch(self.ole)
        self._sem.InitialiseRemoting()

    def grabImage(self):
        filename = tempfile.TemporaryFile(suffix='.bmp').name
        self._sem.Grab(self.imageX, self.imageY, self.imageWidth, self.imageHeight, self.imageReduction, filename)
        return Image.open(filename)

class SemControllerGui(QtWidgets.QWidget):
    ...

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    gui = SemControllerGui(SemController())
    gui.show()
    sys.exit(app.exec_())
