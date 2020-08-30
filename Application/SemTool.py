#   File:   SemTool.py
#
#   Author: Liuchuyao Xu, 2020
# 
#   Brief:  Implement classes related to the GUI of the SEM diagnostic tool.

from PySide2 import QtGui
from PySide2 import QtWidgets

from ObjectInspector import ObjectInspector
from SemController import SemController
from SemCorrector import SemCorrector
from SemImageViewer import SemImageViewer

class SemTool(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        controller = SemController()
        corrector = SemCorrector(controller)
        imageViewer = SemImageViewer()
        imageViewer.sem = controller

        tab = QtWidgets.QTabWidget()
        tab.addTab(ObjectInspector(controller), 'Controller')
        tab.addTab(ObjectInspector(corrector), 'Corrector')
        tab.addTab(ObjectInspector(imageViewer), 'Image Viewer')

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        layout.addWidget(tab)

        self.setMinimumSize(512, 512)
        self.setWindowTitle('SemTool')

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    gui = SemTool()
    gui.show()
    app.exec_()
