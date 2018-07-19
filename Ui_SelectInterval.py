# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SelectInterval.ui'
#
# Created: Mon Feb 22 16:33:51 2016
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

class Ui_SelectInterval(object):
    def setupUi(self, SelectInterval):
        SelectInterval.setObjectName(_fromUtf8("SelectInterval"))
        SelectInterval.resize(467, 256)
        self.okButton = QtGui.QPushButton(SelectInterval)
        self.okButton.setGeometry(QtCore.QRect(100, 210, 93, 28))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.closeButton = QtGui.QPushButton(SelectInterval)
        self.closeButton.setGeometry(QtCore.QRect(270, 210, 93, 28))
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.preFireBox = QtGui.QComboBox(SelectInterval)
        self.preFireBox.setGeometry(QtCore.QRect(60, 140, 111, 22))
        self.preFireBox.setObjectName(_fromUtf8("preFireBox"))
        self.postFireBox = QtGui.QComboBox(SelectInterval)
        self.postFireBox.setGeometry(QtCore.QRect(290, 140, 111, 22))
        self.postFireBox.setObjectName(_fromUtf8("postFireBox"))
        self.label_2 = QtGui.QLabel(SelectInterval)
        self.label_2.setGeometry(QtCore.QRect(60, 110, 111, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(SelectInterval)
        self.label_3.setGeometry(QtCore.QRect(290, 110, 91, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.imageBox = QtGui.QComboBox(SelectInterval)
        self.imageBox.setGeometry(QtCore.QRect(150, 60, 161, 22))
        self.imageBox.setObjectName(_fromUtf8("imageBox"))
        self.label = QtGui.QLabel(SelectInterval)
        self.label.setGeometry(QtCore.QRect(150, 20, 121, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(SelectInterval)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SelectInterval.close)
        QtCore.QMetaObject.connectSlotsByName(SelectInterval)

    def retranslateUi(self, SelectInterval):
        SelectInterval.setWindowTitle(_translate("SelectInterval", "Load Images", None))
        self.okButton.setText(_translate("SelectInterval", "OK", None))
        self.closeButton.setText(_translate("SelectInterval", "Cancel", None))
        self.label_2.setText(_translate("SelectInterval", "Start Year", None))
        self.label_3.setText(_translate("SelectInterval", "End Year", None))
        self.label.setText(_translate("SelectInterval", "Image Selection", None))

