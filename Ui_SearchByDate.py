# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_SearchByDate.ui'
#
# Created: Mon Oct 26 16:42:00 2015
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

class Ui_SearchByDate(object):
    def setupUi(self, SearchByDate):
        SearchByDate.setObjectName(_fromUtf8("SearchByDate"))
        SearchByDate.resize(703, 252)
        self.label = QtGui.QLabel(SearchByDate)
        self.label.setGeometry(QtCore.QRect(40, 25, 191, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(SearchByDate)
        self.label_2.setGeometry(QtCore.QRect(40, 80, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(8)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.dateFieldComboBox = QtGui.QComboBox(SearchByDate)
        self.dateFieldComboBox.setGeometry(QtCore.QRect(170, 80, 211, 22))
        self.dateFieldComboBox.setObjectName(_fromUtf8("dateFieldComboBox"))
        self.label_3 = QtGui.QLabel(SearchByDate)
        self.label_3.setGeometry(QtCore.QRect(40, 130, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(SearchByDate)
        self.label_4.setGeometry(QtCore.QRect(380, 130, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.searchButton = QtGui.QPushButton(SearchByDate)
        self.searchButton.setGeometry(QtCore.QRect(390, 210, 93, 28))
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.cancelButton = QtGui.QPushButton(SearchByDate)
        self.cancelButton.setGeometry(QtCore.QRect(540, 210, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.startdateEdit = QtGui.QDateEdit(SearchByDate)
        self.startdateEdit.setGeometry(QtCore.QRect(40, 160, 241, 22))
        self.startdateEdit.setObjectName(_fromUtf8("startdateEdit"))
        self.enddateEdit = QtGui.QDateEdit(SearchByDate)
        self.enddateEdit.setGeometry(QtCore.QRect(380, 160, 241, 22))
        self.enddateEdit.setObjectName(_fromUtf8("enddateEdit"))

        self.retranslateUi(SearchByDate)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), SearchByDate.close)
        QtCore.QMetaObject.connectSlotsByName(SearchByDate)

    def retranslateUi(self, SearchByDate):
        SearchByDate.setWindowTitle(_translate("SearchByDate", "Search By Date", None))
        self.label.setText(_translate("SearchByDate", "Search By Date", None))
        self.label_2.setText(_translate("SearchByDate", "Date Field", None))
        self.label_3.setText(_translate("SearchByDate", "Starting Date", None))
        self.label_4.setText(_translate("SearchByDate", "Ending Date", None))
        self.searchButton.setText(_translate("SearchByDate", "Search", None))
        self.cancelButton.setText(_translate("SearchByDate", "Cancel", None))

