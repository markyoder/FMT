# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SetStatus.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_SetStatus(object):
    def setupUi(self, SetStatus):
        SetStatus.setObjectName(_fromUtf8("SetStatus"))
        SetStatus.resize(342, 324)
        self.label_2 = QtGui.QLabel(SetStatus)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.statusComboBox = QtGui.QComboBox(SetStatus)
        self.statusComboBox.setGeometry(QtCore.QRect(140, 30, 161, 22))
        self.statusComboBox.setObjectName(_fromUtf8("statusComboBox"))
        self.label_3 = QtGui.QLabel(SetStatus)
        self.label_3.setGeometry(QtCore.QRect(20, 90, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.reasonComboBox = QtGui.QComboBox(SetStatus)
        self.reasonComboBox.setGeometry(QtCore.QRect(140, 90, 161, 22))
        self.reasonComboBox.setObjectName(_fromUtf8("reasonComboBox"))
        self.label_4 = QtGui.QLabel(SetStatus)
        self.label_4.setGeometry(QtCore.QRect(20, 180, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.commentTextEdit = QtGui.QTextEdit(SetStatus)
        self.commentTextEdit.setGeometry(QtCore.QRect(140, 140, 161, 91))
        self.commentTextEdit.setObjectName(_fromUtf8("commentTextEdit"))
        self.setstatusButton = QtGui.QPushButton(SetStatus)
        self.setstatusButton.setGeometry(QtCore.QRect(40, 260, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.setstatusButton.setFont(font)
        self.setstatusButton.setObjectName(_fromUtf8("setstatusButton"))
        self.cancelButton = QtGui.QPushButton(SetStatus)
        self.cancelButton.setGeometry(QtCore.QRect(200, 260, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(SetStatus)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SetStatus.close)
        QtCore.QMetaObject.connectSlotsByName(SetStatus)

    def retranslateUi(self, SetStatus):
        SetStatus.setWindowTitle(_translate("SetStatus", "Set Status", None))
        self.label_2.setText(_translate("SetStatus", "Status", None))
        self.label_3.setText(_translate("SetStatus", "Reason", None))
        self.label_4.setText(_translate("SetStatus", "Comment", None))
        self.setstatusButton.setText(_translate("SetStatus", "Set Status", None))
        self.cancelButton.setText(_translate("SetStatus", "Cancel", None))

