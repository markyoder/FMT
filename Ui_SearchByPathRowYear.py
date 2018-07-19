# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SearchByPathRowYear.ui'
#
# Created: Mon Oct 26 09:47:23 2015
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

class Ui_SearchByPathRowYear(object):
    def setupUi(self, SearchByPathRowYear):
        SearchByPathRowYear.setObjectName(_fromUtf8("SearchByPathRowYear"))
        SearchByPathRowYear.resize(540, 197)
        self.label = QtGui.QLabel(SearchByPathRowYear)
        self.label.setGeometry(QtCore.QRect(40, 30, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(SearchByPathRowYear)
        self.label_2.setGeometry(QtCore.QRect(50, 80, 53, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pathLineEdit = QtGui.QLineEdit(SearchByPathRowYear)
        self.pathLineEdit.setGeometry(QtCore.QRect(110, 80, 81, 22))
        self.pathLineEdit.setObjectName(_fromUtf8("pathLineEdit"))
        self.label_3 = QtGui.QLabel(SearchByPathRowYear)
        self.label_3.setGeometry(QtCore.QRect(210, 80, 53, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.rowLineEdit = QtGui.QLineEdit(SearchByPathRowYear)
        self.rowLineEdit.setGeometry(QtCore.QRect(260, 80, 81, 22))
        self.rowLineEdit.setObjectName(_fromUtf8("rowLineEdit"))
        self.label_4 = QtGui.QLabel(SearchByPathRowYear)
        self.label_4.setGeometry(QtCore.QRect(360, 80, 41, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.yearComboBox = QtGui.QComboBox(SearchByPathRowYear)
        self.yearComboBox.setGeometry(QtCore.QRect(410, 80, 101, 22))
        self.yearComboBox.setObjectName(_fromUtf8("yearComboBox"))
        self.searchButton = QtGui.QPushButton(SearchByPathRowYear)
        self.searchButton.setGeometry(QtCore.QRect(250, 130, 93, 28))
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.cancelButton = QtGui.QPushButton(SearchByPathRowYear)
        self.cancelButton.setGeometry(QtCore.QRect(400, 130, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(SearchByPathRowYear)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SearchByPathRowYear.close)
        QtCore.QMetaObject.connectSlotsByName(SearchByPathRowYear)

    def retranslateUi(self, SearchByPathRowYear):
        SearchByPathRowYear.setWindowTitle(_translate("SearchByPathRowYear", "Search By Path/Row and Year", None))
        self.label.setText(_translate("SearchByPathRowYear", "Search by Path/Row and Year", None))
        self.label_2.setText(_translate("SearchByPathRowYear", "Path", None))
        self.label_3.setText(_translate("SearchByPathRowYear", "Row", None))
        self.label_4.setText(_translate("SearchByPathRowYear", "Year", None))
        self.searchButton.setText(_translate("SearchByPathRowYear", "Search", None))
        self.cancelButton.setText(_translate("SearchByPathRowYear", "Cancel", None))

