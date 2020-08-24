# File:     SemCorrectorGui.py
#
# Author:   Liuchuyao Xu, 2020

from PySide2 import QtWidgets

from WidgetCreators import createForm

class SemCorrectorGui(QtWidgets.QWidget):
    
    def __init__(self, semCorrector):
        super().__init__()

        self.semCorrector = semCorrector
    
        self.setMinimumSize(320, 240)
        self.setWindowTitle('SEM Corrector')

        box = QtWidgets.QGroupBox()
        box.setLayout(createForm(self.semCorrector))
        direction = QtWidgets.QBoxLayout.TopToBottom
        self.layout = QtWidgets.QBoxLayout(direction, self)
        self.layout.addWidget(box)

if __name__ == '__main__':
    import sys
    from SemController import SemController
    from SemCorrector import SemCorrector

    app = QtWidgets.QApplication(sys.argv)
    semc = SemCorrectorGui(SemCorrector(SemController()))
    semc.show()
    sys.exit(app.exec_())
