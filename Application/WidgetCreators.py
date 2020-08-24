#   File:   WidgetCreator.py
#
#   Author: Liuchuyao Xu, 2020

from PySide2 import QtWidgets

def createForm(obj):
    attrNames = dir(obj)
    formLayout = QtWidgets.QFormLayout()
    for attrName in attrNames:
        if attrName[0] == '_':
            continue
        attr = getattr(obj, attrName)
        if type(attr) is int:
            widget = SpinBox(obj, attrName)
        elif type(attr) is float:
            widget = DoubleSpinBox(obj, attrName)
        elif type(attr) is str:
            widget = LineEdit(obj, attrName)
        elif type(attr) is bool:
            widget = CheckBox(obj, attrName)
        elif callable(attr) and attrName[0:3] == 'gui':
            widget = PushButton(obj, attrName)
        else:
            continue
        formLayout.addRow(attrName, widget)
    return formLayout

class SpinBox(QtWidgets.QSpinBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setRange(0, 9999)
        self.setValue(getattr(obj, attrName))
        self.valueChanged.connect(self.onValueChanged)

    def onValueChanged(self):
        setattr(self.obj, self.attrName, self.value())

class DoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setRange(0, 9999)
        self.setSingleStep(0.01)
        self.setValue(getattr(obj, attrName))
        self.valueChanged.connect(self.onValueChanged)

    def onValueChanged(self):
        setattr(self.obj, self.attrName, self.value())

class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setText(getattr(obj, attrName))
        self.editingFinished.connect(self.onEditingFinished)

    def onEditingFinished(self):
        setattr(self.obj, self.attrName, self.text())

class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setChecked(getattr(obj, attrName))
        self.stateChanged.connect(self.onStateChanged)

    def onStateChanged(self):
        setattr(self.obj, self.attrName, self.isChecked())

class PushButton(QtWidgets.QPushButton):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setText(attrName)
        self.clicked.connect(getattr(self.obj, self.attrName))
