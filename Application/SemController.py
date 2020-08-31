#   File:   SemController.py
#
#   Author: Liuchuyao Xu, 2020
#
#   Brief:  Implement the SemController class.
#           The class gives direct access to the API of the SEM
#           The class provides functions that the API does not directly support.
#
#   Abbreviations:
#           ole     Microsoft Object Linking and Embedding document

import tempfile
from PIL import Image
from win32com import client

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

        self.initSem()

    def initSem(self):
        if self.semInitialised:
            return
        self._sem = client.Dispatch(self.ole)
        self._sem.InitialiseRemoting()
        self.semInitialised = True

    def sem(self):
        if not self.semInitialised:
            self.initSem()
        return self._sem

    def grabImage(self):
        filename = tempfile.TemporaryFile(suffix='.bmp').name
        self.sem().Grab(self.imageX, self.imageY, self.imageWidth, self.imageHeight, self.imageReduction, filename)
        return Image.open(filename)

    def guiGrabAndSaveImage(self):
        image = self.grabImage()
        image.save('image.PNG', format='PNG')

if __name__ == '__main__':
    import sys
    from PySide2 import QtWidgets
    from ObjectInspector import ObjectInspector

    app = QtWidgets.QApplication(sys.argv)
    semc = ObjectInspector(SemController())
    semc.show()
    sys.exit(app.exec_())
