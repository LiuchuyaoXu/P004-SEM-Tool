# File:     SemCorrectorGui.py
#
# Author:   Liuchuyao Xu, 2020

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

class SemCorrectorGui(QtWidgets.QWidget):
    
    def __init__(self, semCorrector):
        super().__init__()

        self.semCorrector = semCorrector
        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
    
        self.setMinimumSize(320, 240)
        self.setWindowTitle('SemCorrector')

        self.initCorrectorForm()

    def initCorrectorForm(self):
        intValidator = QtGui.QIntValidator()
        doubleValidator = QtGui.QDoubleValidator()

        self.rasterX = QtWidgets.QLineEdit(str(self.semCorrector.rasterX))
        self.rasterX.setValidator(intValidator)
        self.rasterX.textChanged.connect(self.updateRasterX)
        self.rasterY = QtWidgets.QLineEdit(str(self.semCorrector.rasterY))
        self.rasterY.setValidator(intValidator)
        self.rasterY.textChanged.connect(self.updateRasterY)
        self.rasterWidth = QtWidgets.QLineEdit(str(self.semCorrector.rasterWidth))
        self.rasterWidth.setValidator(intValidator)
        self.rasterWidth.textChanged.connect(self.updateRasterWidth)
        self.rasterHeight = QtWidgets.QLineEdit(str(self.semCorrector.rasterHeight))
        self.rasterHeight.setValidator(intValidator)
        self.rasterHeight.textChanged.connect(self.updateRasterHeight)

        self.stigmatorStep = QtWidgets.QLineEdit(str(self.semCorrector.stigmatorStep))
        self.stigmatorStep.setValidator(doubleValidator)
        self.stigmatorStep.textChanged.connect(self.updateStigmatorStep)
        self.workingDistanceStep = QtWidgets.QLineEdit(str(self.semCorrector.workingDistanceStep))
        self.workingDistanceStep.setValidator(doubleValidator)
        self.workingDistanceStep.textChanged.connect(self.updateWorkingDistanceStep)
        self.workingDistanceOffset = QtWidgets.QLineEdit(str(self.semCorrector.workingDistanceOffset))
        self.workingDistanceOffset.setValidator(doubleValidator)
        self.workingDistanceOffset.textChanged.connect(self.updateWorkingDistanceOffset)

        self.frameWaitTimeFactor = QtWidgets.QLineEdit(str(self.semCorrector.frameWaitTimeFactor))
        self.frameWaitTimeFactor.setValidator(doubleValidator)
        self.frameWaitTimeFactor.textChanged.connect(self.updateFrameWaitTimeFactor)

        self.applyHann = QtWidgets.QCheckBox()
        self.applyHann.setChecked(self.semCorrector.applyHann)
        self.applyHann.stateChanged.connect(self.updateApplyHann)
        self.applyDiscMask = QtWidgets.QCheckBox()
        self.applyDiscMask.setChecked(self.semCorrector.applyDiscMask)
        self.applyDiscMask.stateChanged.connect(self.updateApplyDiscMask)

        self.discMaskRadius = QtWidgets.QLineEdit(str(self.semCorrector.discMaskRadius))
        self.discMaskRadius.setValidator(intValidator)
        self.discMaskRadius.textChanged.connect(self.updateDiscMaskRadius)

        self.defocusingThreshold = QtWidgets.QLineEdit(str(self.semCorrector.defocusingThreshold))
        self.defocusingThreshold.setValidator(doubleValidator)
        self.defocusingThreshold.textChanged.connect(self.updateDefocusingThreshold)
        self.astigmatismThreshold = QtWidgets.QLineEdit(str(self.semCorrector.astigmatismThreshold))
        self.astigmatismThreshold.setValidator(doubleValidator)
        self.astigmatismThreshold.textChanged.connect(self.updateAstigmatismThreshold)

        self.stigmatorCorrected = QtWidgets.QLabel('False')
        self.workingDistanceCorrected = QtWidgets.QLabel('False')

        self.numberOfIterations = QtWidgets.QLineEdit('1')
        self.numberOfIterations.setValidator(intValidator)
        correctorButton = QtWidgets.QPushButton('Correct')
        correctorButton.clicked.connect(self.correct)

        layout = QtWidgets.QFormLayout()
        layout.addRow('Raster X', self.rasterX)
        layout.addRow('Raster Y', self.rasterY)
        layout.addRow('Raster width', self.rasterWidth)
        layout.addRow('Raster height', self.rasterHeight)
        layout.addRow('Stigmator step', self.stigmatorStep)
        layout.addRow('Working distance step', self.workingDistanceStep)
        layout.addRow('Working distance offset', self.workingDistanceOffset)
        layout.addRow('Frame wait time factor', self.frameWaitTimeFactor)
        layout.addRow('Apply Hann window', self.applyHann)
        layout.addRow('Apply disc mask', self.applyDiscMask)
        layout.addRow('Disc mask radius', self.discMaskRadius)
        layout.addRow('Defocusing threshold', self.defocusingThreshold)
        layout.addRow('Astigmatism threshold', self.astigmatismThreshold)
        layout.addRow('Stigmator corrected', self.stigmatorCorrected)
        layout.addRow('Working distance corrected', self.workingDistanceCorrected)
        layout.addRow('Number of iterations', self.numberOfIterations)
        layout.addRow(correctorButton)

        correctorForm = QtWidgets.QGroupBox('SemCorrector')
        correctorForm.setLayout(layout)
        self.layout.addWidget(correctorForm)

    def correct(self):
        for _ in range(int(self.numberOfIterations.text())):
            self.semCorrector.iterate()
        self.stigmatorCorrected.setText('{}'.format(self.semCorrector.stigmatorCorrected))
        self.workingDistanceCorrected.setText('{}'.format(self.semCorrector.workingDistanceCorrected))

    def updateRasterX(self):
        self.semCorrector.rasterX = int(self.rasterX.text())
    
    def updateRasterY(self):
        self.semCorrector.rasterY = int(self.rasterY.text())

    def updateRasterWidth(self):
        self.semCorrector.rasterWidth = int(self.rasterWidth.text())

    def updateRasterHeight(self):
        self.semCorrector.rasterHeight = int(self.rasterHeight.text())

    def updateStigmatorStep(self):
        self.semCorrector.stigmatorStep = self.stigmatorStep.text()

    def updateWorkingDistanceStep(self):
        self.semCorrector.workingDistanceStep = self.workingDistanceStep.text()

    def updateWorkingDistanceOffset(self):
        self.semCorrector.workingDistanceOffset = self.workingDistanceOffset.text()

    def updateFrameWaitTimeFactor(self):
        self.semCorrector.frameWaitTimeFactor = self.frameWaitTimeFactor.text()

    def updateApplyHann(self):
        self.semCorrector.applyHann = self.applyHann.isChecked()

    def updateApplyDiscMask(self):
        self.semCorrector.applyDiscMask = self.applyDiscMask.isChecked()

    def updateDiscMaskRadius(self):
        self.semCorrector.discMaskRadius = int(self.discMaskRadius.text())

    def updateDefocusingThreshold(self):
        self.semCorrector.defocusingThreshold = self.defocusingThreshold.text()

    def updateAstigmatismThreshold(self):
        self.semCorrector.astigmatismThreshold = self.astigmatismThreshold.text()

if __name__ == '__main__':
    import sys
    from SemCorrector import SemCorrector

    app = QtWidgets.QApplication(sys.argv)
    semc = SemCorrectorGui(SemCorrector(None))
    semc.show()
    sys.exit(app.exec_())
