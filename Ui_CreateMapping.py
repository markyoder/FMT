# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_CreateMapping.ui'
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

class Ui_CreateMapping(object):
    def setupUi(self, CreateMapping):
        CreateMapping.setObjectName(_fromUtf8("CreateMapping"))
        CreateMapping.resize(649, 368)
        self.assessmentComboBox = QtGui.QComboBox(CreateMapping)
        self.assessmentComboBox.setGeometry(QtCore.QRect(30, 50, 151, 22))
        self.assessmentComboBox.setObjectName(_fromUtf8("assessmentComboBox"))
        self.label_2 = QtGui.QLabel(CreateMapping)
        self.label_2.setGeometry(QtCore.QRect(30, 20, 131, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.labelImage = QtGui.QLabel(CreateMapping)
        self.labelImage.setGeometry(QtCore.QRect(30, 90, 141, 16))
        self.labelImage.setObjectName(_fromUtf8("labelImage"))
        self.label_4 = QtGui.QLabel(CreateMapping)
        self.label_4.setGeometry(QtCore.QRect(240, 90, 101, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(CreateMapping)
        self.label_5.setGeometry(QtCore.QRect(450, 90, 111, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.preSensorlineEdit = QtGui.QLineEdit(CreateMapping)
        self.preSensorlineEdit.setGeometry(QtCore.QRect(30, 190, 151, 22))
        self.preSensorlineEdit.setObjectName(_fromUtf8("preSensorlineEdit"))
        self.labelSensor = QtGui.QLabel(CreateMapping)
        self.labelSensor.setGeometry(QtCore.QRect(30, 160, 171, 16))
        self.labelSensor.setObjectName(_fromUtf8("labelSensor"))
        self.postSensorlineEdit = QtGui.QLineEdit(CreateMapping)
        self.postSensorlineEdit.setGeometry(QtCore.QRect(240, 190, 151, 22))
        self.postSensorlineEdit.setObjectName(_fromUtf8("postSensorlineEdit"))
        self.label_7 = QtGui.QLabel(CreateMapping)
        self.label_7.setGeometry(QtCore.QRect(240, 160, 121, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.periSensorlineEdit = QtGui.QLineEdit(CreateMapping)
        self.periSensorlineEdit.setGeometry(QtCore.QRect(450, 190, 141, 22))
        self.periSensorlineEdit.setObjectName(_fromUtf8("periSensorlineEdit"))
        self.label_8 = QtGui.QLabel(CreateMapping)
        self.label_8.setGeometry(QtCore.QRect(450, 160, 141, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.preDatelineEdit = QtGui.QLineEdit(CreateMapping)
        self.preDatelineEdit.setGeometry(QtCore.QRect(30, 260, 151, 22))
        self.preDatelineEdit.setObjectName(_fromUtf8("preDatelineEdit"))
        self.labelDate = QtGui.QLabel(CreateMapping)
        self.labelDate.setGeometry(QtCore.QRect(30, 230, 151, 16))
        self.labelDate.setObjectName(_fromUtf8("labelDate"))
        self.postDatelineEdit = QtGui.QLineEdit(CreateMapping)
        self.postDatelineEdit.setGeometry(QtCore.QRect(240, 260, 151, 22))
        self.postDatelineEdit.setObjectName(_fromUtf8("postDatelineEdit"))
        self.label_10 = QtGui.QLabel(CreateMapping)
        self.label_10.setGeometry(QtCore.QRect(240, 230, 101, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.periDatelineEdit = QtGui.QLineEdit(CreateMapping)
        self.periDatelineEdit.setGeometry(QtCore.QRect(450, 260, 141, 22))
        self.periDatelineEdit.setObjectName(_fromUtf8("periDatelineEdit"))
        self.label_11 = QtGui.QLabel(CreateMapping)
        self.label_11.setGeometry(QtCore.QRect(450, 230, 101, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.saveButton = QtGui.QPushButton(CreateMapping)
        self.saveButton.setGeometry(QtCore.QRect(120, 310, 101, 28))
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.cancelButton = QtGui.QPushButton(CreateMapping)
        self.cancelButton.setGeometry(QtCore.QRect(360, 310, 93, 28))
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.preImageComboBox = QtGui.QComboBox(CreateMapping)
        self.preImageComboBox.setGeometry(QtCore.QRect(30, 120, 151, 22))
        self.preImageComboBox.setObjectName(_fromUtf8("preImageComboBox"))
        self.postImageComboBox = QtGui.QComboBox(CreateMapping)
        self.postImageComboBox.setGeometry(QtCore.QRect(240, 120, 151, 22))
        self.postImageComboBox.setObjectName(_fromUtf8("postImageComboBox"))
        self.periImageComboBox = QtGui.QComboBox(CreateMapping)
        self.periImageComboBox.setGeometry(QtCore.QRect(450, 120, 141, 22))
        self.periImageComboBox.setObjectName(_fromUtf8("periImageComboBox"))

        self.retranslateUi(CreateMapping)
        QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL(_fromUtf8("clicked()")), CreateMapping.close)
        QtCore.QMetaObject.connectSlotsByName(CreateMapping)

    def retranslateUi(self, CreateMapping):
        CreateMapping.setWindowTitle(_translate("CreateMapping", "Create Scene Pair", None))
        self.label_2.setText(_translate("CreateMapping", "Assessment Strategy", None))
        self.labelImage.setText(_translate("CreateMapping", "Pre Image", None))
        self.label_4.setText(_translate("CreateMapping", "Post Image", None))
        self.label_5.setText(_translate("CreateMapping", "Perimeter Image", None))
        self.labelSensor.setText(_translate("CreateMapping", "Pre Sensor Used", None))
        self.label_7.setText(_translate("CreateMapping", "Post Sensor Used", None))
        self.label_8.setText(_translate("CreateMapping", "Perimeter Sensor Used", None))
        self.labelDate.setText(_translate("CreateMapping", "Prefire Date", None))
        self.label_10.setText(_translate("CreateMapping", "Postfire Date", None))
        self.label_11.setText(_translate("CreateMapping", "Perimeter Date", None))
        self.saveButton.setText(_translate("CreateMapping", "Save Mapping", None))
        self.cancelButton.setText(_translate("CreateMapping", "Cancel", None))

