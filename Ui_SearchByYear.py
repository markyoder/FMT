# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SearchByYear.ui'
#
# Created: Wed Oct 21 08:54:49 2015
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

class Ui_SearchByYear(object):
    def setupUi(self, SearchByYear):
        SearchByYear.setObjectName(_fromUtf8("SearchByYear"))
        SearchByYear.resize(534, 234)
        self.label = QtGui.QLabel(SearchByYear)
        self.label.setGeometry(QtCore.QRect(40, 40, 201, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(SearchByYear)
        self.label_2.setGeometry(QtCore.QRect(50, 110, 91, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.yearComboBox = QtGui.QComboBox(SearchByYear)
        self.yearComboBox.setGeometry(QtCore.QRect(220, 110, 131, 22))
        self.yearComboBox.setObjectName(_fromUtf8("yearComboBox"))
        self.searchButton = QtGui.QPushButton(SearchByYear)
        self.searchButton.setGeometry(QtCore.QRect(210, 170, 93, 28))
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.cancelButton = QtGui.QPushButton(SearchByYear)
        self.cancelButton.setGeometry(QtCore.QRect(360, 170, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(SearchByYear)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SearchByYear.close)
        QtCore.QMetaObject.connectSlotsByName(SearchByYear)

    def retranslateUi(self, SearchByYear):
        SearchByYear.setWindowTitle(_translate("SearchByYear", "Search By Year", None))
        self.label.setText(_translate("SearchByYear", "Search By Year", None))
        self.label_2.setText(_translate("SearchByYear", "Year Field", None))
        self.searchButton.setText(_translate("SearchByYear", "Search", None))
        self.cancelButton.setText(_translate("SearchByYear", "Cancel", None))

