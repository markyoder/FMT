# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_FireParams.ui'
#
# Created: Thu Jan 25 08:28:47 2018
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

class Ui_FireParams(object):
    def setupUi(self, FireParams):
        FireParams.setObjectName(_fromUtf8("FireParams"))
        FireParams.resize(680, 374)
        self.groupBox = QtGui.QGroupBox(FireParams)
        self.groupBox.setGeometry(QtCore.QRect(30, 10, 611, 281))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.lblLat = QtGui.QLabel(self.groupBox)
        self.lblLat.setGeometry(QtCore.QRect(20, 20, 51, 16))
        self.lblLat.setObjectName(_fromUtf8("lblLat"))
        self.lblLong = QtGui.QLabel(self.groupBox)
        self.lblLong.setGeometry(QtCore.QRect(370, 20, 51, 16))
        self.lblLong.setObjectName(_fromUtf8("lblLong"))
        self.latSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.latSpinBox.setGeometry(QtCore.QRect(80, 20, 111, 22))
        self.latSpinBox.setDecimals(3)
        self.latSpinBox.setMinimum(-180.0)
        self.latSpinBox.setMaximum(180.0)
        self.latSpinBox.setObjectName(_fromUtf8("latSpinBox"))
        self.longSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.longSpinBox.setGeometry(QtCore.QRect(430, 20, 111, 22))
        self.longSpinBox.setDecimals(3)
        self.longSpinBox.setMinimum(-180.0)
        self.longSpinBox.setMaximum(180.0)
        self.longSpinBox.setObjectName(_fromUtf8("longSpinBox"))
        self.beginCalendarWidget = QtGui.QCalendarWidget(self.groupBox)
        self.beginCalendarWidget.setGeometry(QtCore.QRect(40, 90, 251, 171))
        self.beginCalendarWidget.setMinimumDate(QtCore.QDate(1984, 1, 1))
        self.beginCalendarWidget.setMaximumDate(QtCore.QDate(2035, 12, 31))
        self.beginCalendarWidget.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.beginCalendarWidget.setObjectName(_fromUtf8("beginCalendarWidget"))
        self.lblBeginDate = QtGui.QLabel(self.groupBox)
        self.lblBeginDate.setGeometry(QtCore.QRect(40, 60, 81, 16))
        self.lblBeginDate.setObjectName(_fromUtf8("lblBeginDate"))
        self.endCalendarWidget = QtGui.QCalendarWidget(self.groupBox)
        self.endCalendarWidget.setGeometry(QtCore.QRect(310, 90, 251, 171))
        self.endCalendarWidget.setMinimumDate(QtCore.QDate(1984, 1, 1))
        self.endCalendarWidget.setMaximumDate(QtCore.QDate(2035, 12, 31))
        self.endCalendarWidget.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        self.endCalendarWidget.setObjectName(_fromUtf8("endCalendarWidget"))
        self.lblEndDate = QtGui.QLabel(self.groupBox)
        self.lblEndDate.setGeometry(QtCore.QRect(320, 60, 81, 16))
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.okButton = QtGui.QPushButton(FireParams)
        self.okButton.setGeometry(QtCore.QRect(110, 310, 93, 28))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.cancelButton = QtGui.QPushButton(FireParams)
        self.cancelButton.setGeometry(QtCore.QRect(360, 310, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(FireParams)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), FireParams.close)
        QtCore.QMetaObject.connectSlotsByName(FireParams)

    def retranslateUi(self, FireParams):
        FireParams.setWindowTitle(_translate("FireParams", "Define Fire Parameters", None))
        self.lblLat.setText(_translate("FireParams", "Latitude:", None))
        self.lblLong.setText(_translate("FireParams", "Longitude:", None))
        self.lblBeginDate.setText(_translate("FireParams", "Start Date:", None))
        self.lblEndDate.setText(_translate("FireParams", "End Date:", None))
        self.okButton.setText(_translate("FireParams", "OK", None))
        self.cancelButton.setText(_translate("FireParams", "Cancel", None))

