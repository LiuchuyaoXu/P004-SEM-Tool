# File:     SemControllerGui.py
#
# Author:   Liuchuyao Xu, 2020

from PySide2 import QtWidgets

from WidgetCreators import createForm

class SemControllerGui(QtWidgets.QWidget):

    def __init__(self, semController):
        super().__init__()

        self.semController = semController

        self.setMinimumSize(320, 240)
        self.setWindowTitle('SEM Controller')

        box = QtWidgets.QGroupBox()
        box.setLayout(createForm(self.semController))
        direction = QtWidgets.QBoxLayout.TopToBottom
        self.layout = QtWidgets.QBoxLayout(direction, self)
        self.layout.addWidget(box)

if __name__ == '__main__':
    import sys
    from SemController import SemController

    app = QtWidgets.QApplication(sys.argv)
    semc = SemControllerGui(SemController())
    semc.show()
    sys.exit(app.exec_())
