# File:     ObjectInspector.py
#
# Author:   Liuchuyao Xu, 2020

from PySide2 import QtCore
from PySide2 import QtWidgets

class ObjectInspector(QtWidgets.QWidget):

    def __init__(self, obj):
        super().__init__()

        allPropertyNames = dir(obj)
        allVariableNames = vars(obj).keys()
        allFunctionNames = sorted(set(allPropertyNames) - set(allVariableNames))
        variableNames = filter(ObjectInspector.variableNameFilter, allVariableNames)
        functionNames = filter(ObjectInspector.functionNameFilter, allFunctionNames)

        updateTimer = QtCore.QTimer(self)
        updateTimer.start(500)

        form = QtWidgets.QFormLayout(self)
        for name in variableNames:
            widget = ObjectInspector.createWidget(obj, name)
            if widget:
                updateTimer.timeout.connect(widget.update)
                form.addRow(ObjectInspector.parseCamelCase(name), widget)
        for name in functionNames:
            widget = ObjectInspector.createWidget(obj, name)
            if widget:
                form.addRow(ObjectInspector.parseCamelCase(name[3:]), widget)

    @staticmethod
    def createWidget(obj, propertyName):
        prop = getattr(obj, propertyName)
        if type(prop) is int:
            widget = SpinBox(obj, propertyName)
            return widget
        if type(prop) is float:
            widget = DoubleSpinBox(obj, propertyName)
            return widget
        if type(prop) is bool:
            widget = CheckBox(obj, propertyName)
            return widget
        if type(prop) is str:
            widget = LineEdit(obj, propertyName)
            return widget
        if callable(prop):
            text = ObjectInspector.parseCamelCase(propertyName[3:])
            widget = PushButton(obj, propertyName)
            widget.setText(text)
            return widget
        return None

    @staticmethod
    def parseCamelCase(name):
        newName = name[0].upper()
        for letter in name[1:]:
            if letter.islower():
                newName += letter
            else:
                newName += ' '
                newName += letter
        return newName
        
    @staticmethod
    def variableNameFilter(name):
        if name[0] == '_':
            return False
        return True

    @staticmethod
    def functionNameFilter(name):
        if name[0] == '_':
            return False
        if name[0:3] != 'gui':
            return False
        return True

class SpinBox(QtWidgets.QSpinBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setRange(0, 9999)
        self.update()
        self.valueChanged.connect(self.onValueChanged)

    def update(self):
        self.setValue(getattr(self.obj, self.attrName))

    def onValueChanged(self):
        setattr(self.obj, self.attrName, self.value())

class DoubleSpinBox(QtWidgets.QDoubleSpinBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.setRange(0, 9999)
        self.setSingleStep(0.01)
        self.update()
        self.valueChanged.connect(self.onValueChanged)

    def update(self):
        self.setValue(getattr(self.obj, self.attrName))

    def onValueChanged(self):
        setattr(self.obj, self.attrName, self.value())

class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.update()
        self.editingFinished.connect(self.onEditingFinished)

    def update(self):
        self.setText(getattr(self.obj, self.attrName))

    def onEditingFinished(self):
        setattr(self.obj, self.attrName, self.text())

class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.update()
        self.stateChanged.connect(self.onStateChanged)

    def update(self):
        self.setChecked(getattr(self.obj, self.attrName))

    def onStateChanged(self):
        setattr(self.obj, self.attrName, self.isChecked())

class PushButton(QtWidgets.QPushButton):

    def __init__(self, obj, attrName):
        super().__init__()
        self.obj = obj
        self.attrName = attrName
        self.clicked.connect(getattr(self.obj, self.attrName))
