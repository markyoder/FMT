# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SearchByName.ui'
#
# Created: Mon Oct 26 08:58:56 2015
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

class Ui_SearchByName(object):
    def setupUi(self, SearchByName):
        SearchByName.setObjectName(_fromUtf8("SearchByName"))
        SearchByName.resize(440, 200)
        self.label = QtGui.QLabel(SearchByName)
        self.label.setGeometry(QtCore.QRect(20, 30, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(SearchByName)
        self.label_2.setGeometry(QtCore.QRect(20, 90, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.incidentLineEdit = QtGui.QLineEdit(SearchByName)
        self.incidentLineEdit.setGeometry(QtCore.QRect(140, 90, 261, 22))
        self.incidentLineEdit.setObjectName(_fromUtf8("incidentLineEdit"))
        self.searchButton = QtGui.QPushButton(SearchByName)
        self.searchButton.setGeometry(QtCore.QRect(130, 140, 93, 28))
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.cancelPushButton = QtGui.QPushButton(SearchByName)
        self.cancelPushButton.setGeometry(QtCore.QRect(290, 140, 93, 28))
        self.cancelPushButton.setObjectName(_fromUtf8("cancelPushButton"))

        self.retranslateUi(SearchByName)
        QtCore.QObject.connect(self.cancelPushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SearchByName.close)
        QtCore.QMetaObject.connectSlotsByName(SearchByName)

    def retranslateUi(self, SearchByName):
        SearchByName.setWindowTitle(_translate("SearchByName", "Search By Name", None))
        self.label.setText(_translate("SearchByName", "Search By Incident Name", None))
        self.label_2.setText(_translate("SearchByName", "Incident Name", None))
        self.searchButton.setText(_translate("SearchByName", "Search", None))
        self.cancelPushButton.setText(_translate("SearchByName", "Cancel", None))

