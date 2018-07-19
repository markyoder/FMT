# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_HMS.ui'
#
# Created: Wed Jul 12 09:02:11 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_HMS(object):
    def setupUi(self, HMS):
        HMS.setObjectName(_fromUtf8("HMS"))
        HMS.resize(296, 210)
        self.yearBox = QtGui.QComboBox(HMS)
        self.yearBox.setGeometry(QtCore.QRect(60, 90, 161, 22))
        self.yearBox.setObjectName(_fromUtf8("yearBox"))
        self.label = QtGui.QLabel(HMS)
        self.label.setGeometry(QtCore.QRect(50, 40, 181, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.okButton = QtGui.QPushButton(HMS)
        self.okButton.setGeometry(QtCore.QRect(40, 150, 93, 28))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.cancelButton = QtGui.QPushButton(HMS)
        self.cancelButton.setGeometry(QtCore.QRect(170, 150, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(HMS)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), HMS.close)
        QtCore.QMetaObject.connectSlotsByName(HMS)

    def retranslateUi(self, HMS):
        HMS.setWindowTitle(_translate("HMS", "HMS Points", None))
        self.label.setText(_translate("HMS", "Display HMS Points", None))
        self.okButton.setText(_translate("HMS", "OK", None))
        self.cancelButton.setText(_translate("HMS", "Cancel", None))

