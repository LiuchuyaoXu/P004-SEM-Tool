#   File:   WidgetCreator.py
#
#   Author: Liuchuyao Xu, 2020

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

def createForm(self, dictionary):
    form = QtWidgets.QFormLayout()
    intValidator = QtGui.QIntValidator()
    floatValidator = QtGui.QDoubleValidator()
    names = list(dictionary.keys())
    for name in names:
        value = dictionary[name]
        if type(value) is int:
            widget = QtWidgets.QLineEdit(str(value))
            widget.setValidator(intValidator)
        elif type(value) is float:
            widget = QtWidgets.QLineEdit(str(value))
            widget.setValidator(floatValidator)
        elif type(value) is bool:
            widget = QtWidgets.QCheckBox()
            widget.setChecked(value)
        form.addRow(name, widget)
    return form
    