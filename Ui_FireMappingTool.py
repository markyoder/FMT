# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_FireMappingTool.ui'
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

class Ui_FireMappingTool(object):
    def setupUi(self, FireMappingTool):
        FireMappingTool.setObjectName(_fromUtf8("FireMappingTool"))
        FireMappingTool.resize(1181, 923)
        FireMappingTool.setMaximumSize(QtCore.QSize(1181, 953))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Icons/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("Icons/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        FireMappingTool.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(FireMappingTool)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1161, 862))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.fireprepButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.fireprepButton.setFont(font)
        self.fireprepButton.setObjectName(_fromUtf8("fireprepButton"))
        self.gridLayout_2.addWidget(self.fireprepButton, 11, 0, 1, 1)
        self.maptableWidget = QtGui.QTableWidget(self.scrollAreaWidgetContents)
        self.maptableWidget.setObjectName(_fromUtf8("maptableWidget"))
        self.maptableWidget.setColumnCount(0)
        self.maptableWidget.setRowCount(0)
        self.gridLayout_2.addWidget(self.maptableWidget, 3, 0, 1, 11)
        self.sceneprepButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.sceneprepButton.setFont(font)
        self.sceneprepButton.setObjectName(_fromUtf8("sceneprepButton"))
        self.gridLayout_2.addWidget(self.sceneprepButton, 10, 0, 1, 1)
        self.delineateButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.delineateButton.setFont(font)
        self.delineateButton.setObjectName(_fromUtf8("delineateButton"))
        self.gridLayout_2.addWidget(self.delineateButton, 12, 0, 1, 1)
        self.subsetButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.subsetButton.setFont(font)
        self.subsetButton.setObjectName(_fromUtf8("subsetButton"))
        self.gridLayout_2.addWidget(self.subsetButton, 13, 0, 1, 1)
        self.openeventButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.openeventButton.setFont(font)
        self.openeventButton.setObjectName(_fromUtf8("openeventButton"))
        self.gridLayout_2.addWidget(self.openeventButton, 14, 0, 1, 1)
        self.metaButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.metaButton.setFont(font)
        self.metaButton.setObjectName(_fromUtf8("metaButton"))
        self.gridLayout_2.addWidget(self.metaButton, 12, 8, 1, 1)
        self.qacheckButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.qacheckButton.setFont(font)
        self.qacheckButton.setObjectName(_fromUtf8("qacheckButton"))
        self.gridLayout_2.addWidget(self.qacheckButton, 13, 8, 1, 1)
        self.updatemappingButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.updatemappingButton.setFont(font)
        self.updatemappingButton.setObjectName(_fromUtf8("updatemappingButton"))
        self.gridLayout_2.addWidget(self.updatemappingButton, 17, 8, 1, 1)
        self.checkBox = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout_2.addWidget(self.checkBox, 9, 0, 1, 1)
        self.createMapButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.createMapButton.setObjectName(_fromUtf8("createMapButton"))
        self.gridLayout_2.addWidget(self.createMapButton, 2, 0, 1, 2)
        self.processDataButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.processDataButton.setObjectName(_fromUtf8("processDataButton"))
        self.gridLayout_2.addWidget(self.processDataButton, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 2, 8, 1, 1)
        self.incidentCount = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.incidentCount.setText(_fromUtf8(""))
        self.incidentCount.setObjectName(_fromUtf8("incidentCount"))
        self.gridLayout_2.addWidget(self.incidentCount, 2, 9, 1, 1)
        self.firetableWidget = QtGui.QTableWidget(self.scrollAreaWidgetContents)
        self.firetableWidget.setObjectName(_fromUtf8("firetableWidget"))
        self.firetableWidget.setColumnCount(0)
        self.firetableWidget.setRowCount(0)
        self.gridLayout_2.addWidget(self.firetableWidget, 1, 0, 1, 11)
        self.clearButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.clearButton.setIconSize(QtCore.QSize(20, 20))
        self.clearButton.setCheckable(False)
        self.clearButton.setObjectName(_fromUtf8("clearButton"))
        self.gridLayout_2.addWidget(self.clearButton, 2, 10, 1, 1)
        self.getSceneListButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.getSceneListButton.setObjectName(_fromUtf8("getSceneListButton"))
        self.gridLayout_2.addWidget(self.getSceneListButton, 0, 0, 1, 2)
        self.ndviButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.ndviButton.setObjectName(_fromUtf8("ndviButton"))
        self.gridLayout_2.addWidget(self.ndviButton, 2, 7, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_4.setAutoFillBackground(False)
        self.groupBox_4.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 127);"))
        self.groupBox_4.setTitle(_fromUtf8(""))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.generateButton = QtGui.QPushButton(self.groupBox_4)
        self.generateButton.setAutoFillBackground(False)
        self.generateButton.setStyleSheet(_fromUtf8("background-color: rgb(188, 188, 188);"))
        self.generateButton.setObjectName(_fromUtf8("generateButton"))
        self.gridLayout_3.addWidget(self.generateButton, 1, 0, 1, 4)
        self.thresh2LineEdit = QtGui.QLineEdit(self.groupBox_4)
        self.thresh2LineEdit.setAutoFillBackground(False)
        self.thresh2LineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.thresh2LineEdit.setObjectName(_fromUtf8("thresh2LineEdit"))
        self.gridLayout_3.addWidget(self.thresh2LineEdit, 0, 2, 1, 1)
        self.thresh3LineEdit = QtGui.QLineEdit(self.groupBox_4)
        self.thresh3LineEdit.setAutoFillBackground(False)
        self.thresh3LineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.thresh3LineEdit.setObjectName(_fromUtf8("thresh3LineEdit"))
        self.gridLayout_3.addWidget(self.thresh3LineEdit, 0, 3, 1, 1)
        self.thresh1LineEdit = QtGui.QLineEdit(self.groupBox_4)
        self.thresh1LineEdit.setAutoFillBackground(False)
        self.thresh1LineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.thresh1LineEdit.setObjectName(_fromUtf8("thresh1LineEdit"))
        self.gridLayout_3.addWidget(self.thresh1LineEdit, 0, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self.groupBox_4)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setStyleSheet(_fromUtf8("background-color: rgb(188, 188, 188);"))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayout = QtGui.QFormLayout(self.tab)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_7 = QtGui.QLabel(self.tab)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self.nothreshLineEdit = QtGui.QLineEdit(self.tab)
        self.nothreshLineEdit.setAutoFillBackground(False)
        self.nothreshLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.nothreshLineEdit.setObjectName(_fromUtf8("nothreshLineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.nothreshLineEdit)
        self.label_8 = QtGui.QLabel(self.tab)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_8)
        self.greenthreshLineEdit = QtGui.QLineEdit(self.tab)
        self.greenthreshLineEdit.setAutoFillBackground(False)
        self.greenthreshLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.greenthreshLineEdit.setObjectName(_fromUtf8("greenthreshLineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.greenthreshLineEdit)
        self.label_9 = QtGui.QLabel(self.tab)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_9)
        self.mappingTextEdit = QtGui.QTextEdit(self.tab)
        self.mappingTextEdit.setAutoFillBackground(True)
        self.mappingTextEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.mappingTextEdit.setObjectName(_fromUtf8("mappingTextEdit"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.mappingTextEdit)
        self.threshButton = QtGui.QPushButton(self.tab)
        self.threshButton.setObjectName(_fromUtf8("threshButton"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.threshButton)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 2, 0, 1, 4)
        self.label_6 = QtGui.QLabel(self.groupBox_4)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_4, 9, 6, 11, 1)
        self.groupBox_5 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_5.setAutoFillBackground(False)
        self.groupBox_5.setStyleSheet(_fromUtf8("background-color: rgb(155, 255, 179);"))
        self.groupBox_5.setTitle(_fromUtf8(""))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_5)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_10 = QtGui.QLabel(self.groupBox_5)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_6.addWidget(self.label_10, 0, 1, 1, 1)
        self.label_11 = QtGui.QLabel(self.groupBox_5)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_6.addWidget(self.label_11, 1, 0, 1, 1)
        self.mappingBox = QtGui.QComboBox(self.groupBox_5)
        self.mappingBox.setAutoFillBackground(False)
        self.mappingBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.mappingBox.setObjectName(_fromUtf8("mappingBox"))
        self.gridLayout_6.addWidget(self.mappingBox, 1, 1, 1, 2)
        self.revisedCheckBox = QtGui.QCheckBox(self.groupBox_5)
        self.revisedCheckBox.setAutoFillBackground(False)
        self.revisedCheckBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.revisedCheckBox.setText(_fromUtf8(""))
        self.revisedCheckBox.setObjectName(_fromUtf8("revisedCheckBox"))
        self.gridLayout_6.addWidget(self.revisedCheckBox, 0, 2, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_5, 16, 8, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 230, 227))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 173, 163))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 78, 66))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 186, 177))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 230, 227))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 173, 163))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 78, 66))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 186, 177))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 230, 227))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 173, 163))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 78, 66))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(127, 58, 49))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 171, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 117, 99))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.groupBox_3.setPalette(palette)
        self.groupBox_3.setAutoFillBackground(False)
        self.groupBox_3.setStyleSheet(_fromUtf8("background-color: rgb(255, 171, 171);"))
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.analysisBox = QtGui.QComboBox(self.groupBox_3)
        self.analysisBox.setAutoFillBackground(False)
        self.analysisBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.analysisBox.setObjectName(_fromUtf8("analysisBox"))
        self.gridLayout_5.addWidget(self.analysisBox, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_5.addWidget(self.label_4, 1, 0, 1, 1)
        self.offsetLineEdit = QtGui.QLineEdit(self.groupBox_3)
        self.offsetLineEdit.setAutoFillBackground(False)
        self.offsetLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.offsetLineEdit.setObjectName(_fromUtf8("offsetLineEdit"))
        self.gridLayout_5.addWidget(self.offsetLineEdit, 1, 1, 1, 1)
        self.label_12 = QtGui.QLabel(self.groupBox_3)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_5.addWidget(self.label_12, 2, 0, 1, 1)
        self.sdLineEdit = QtGui.QLineEdit(self.groupBox_3)
        self.sdLineEdit.setAutoFillBackground(False)
        self.sdLineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.sdLineEdit.setObjectName(_fromUtf8("sdLineEdit"))
        self.gridLayout_5.addWidget(self.sdLineEdit, 2, 1, 1, 1)
        self.dNBRButton = QtGui.QPushButton(self.groupBox_3)
        self.dNBRButton.setAutoFillBackground(False)
        self.dNBRButton.setStyleSheet(_fromUtf8("background-color: rgb(179, 179, 179);"))
        self.dNBRButton.setObjectName(_fromUtf8("dNBRButton"))
        self.gridLayout_5.addWidget(self.dNBRButton, 3, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_5.addWidget(self.label_3, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_3, 16, 2, 3, 1)
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setStyleSheet(_fromUtf8("background-color: rgb(135, 206, 250)"))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)
        self.perimeterBox = QtGui.QComboBox(self.groupBox)
        self.perimeterBox.setAutoFillBackground(False)
        self.perimeterBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.perimeterBox.setObjectName(_fromUtf8("perimeterBox"))
        self.gridLayout_4.addWidget(self.perimeterBox, 0, 1, 1, 1)
        self.shapeButton = QtGui.QPushButton(self.groupBox)
        self.shapeButton.setStyleSheet(_fromUtf8("background-color: rgb(179, 179, 179);"))
        self.shapeButton.setObjectName(_fromUtf8("shapeButton"))
        self.gridLayout_4.addWidget(self.shapeButton, 3, 0, 1, 2)
        self.perimeterTextEdit = QtGui.QTextEdit(self.groupBox)
        self.perimeterTextEdit.setAutoFillBackground(True)
        self.perimeterTextEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.perimeterTextEdit.setObjectName(_fromUtf8("perimeterTextEdit"))
        self.gridLayout_4.addWidget(self.perimeterTextEdit, 2, 0, 1, 2)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 9, 2, 6, 1)
        self.deleteButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.gridLayout_2.addWidget(self.deleteButton, 2, 2, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        FireMappingTool.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(FireMappingTool)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1181, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSearch = QtGui.QMenu(self.menubar)
        self.menuSearch.setObjectName(_fromUtf8("menuSearch"))
        self.menuPreferences = QtGui.QMenu(self.menubar)
        self.menuPreferences.setObjectName(_fromUtf8("menuPreferences"))
        FireMappingTool.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(FireMappingTool)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        FireMappingTool.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(FireMappingTool)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionSearch_By_Name = QtGui.QAction(FireMappingTool)
        self.actionSearch_By_Name.setObjectName(_fromUtf8("actionSearch_By_Name"))
        self.actionSearch_By_Date = QtGui.QAction(FireMappingTool)
        self.actionSearch_By_Date.setObjectName(_fromUtf8("actionSearch_By_Date"))
        self.actionSearch_By_Path_Row_and_Year = QtGui.QAction(FireMappingTool)
        self.actionSearch_By_Path_Row_and_Year.setObjectName(_fromUtf8("actionSearch_By_Path_Row_and_Year"))
        self.actionSearch_By_Year = QtGui.QAction(FireMappingTool)
        self.actionSearch_By_Year.setObjectName(_fromUtf8("actionSearch_By_Year"))
        self.actionScript_Locations = QtGui.QAction(FireMappingTool)
        self.actionScript_Locations.setObjectName(_fromUtf8("actionScript_Locations"))
        self.actionGeneral_Settings = QtGui.QAction(FireMappingTool)
        self.actionGeneral_Settings.setObjectName(_fromUtf8("actionGeneral_Settings"))
        self.actionAdd_Fire = QtGui.QAction(FireMappingTool)
        self.actionAdd_Fire.setObjectName(_fromUtf8("actionAdd_Fire"))
        self.menuFile.addAction(self.actionAdd_Fire)
        self.menuFile.addAction(self.actionExit)
        self.menuSearch.addAction(self.actionSearch_By_Name)
        self.menuSearch.addAction(self.actionSearch_By_Date)
        self.menuSearch.addAction(self.actionSearch_By_Path_Row_and_Year)
        self.menuSearch.addAction(self.actionSearch_By_Year)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSearch.menuAction())
        self.menubar.addAction(self.menuPreferences.menuAction())

        self.retranslateUi(FireMappingTool)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("activated()")), FireMappingTool.close)
        QtCore.QMetaObject.connectSlotsByName(FireMappingTool)

    def retranslateUi(self, FireMappingTool):
        FireMappingTool.setWindowTitle(_translate("FireMappingTool", "Fire Mapping Tool", None))
        self.fireprepButton.setText(_translate("FireMappingTool", "Run Fire Prep", None))
        self.sceneprepButton.setText(_translate("FireMappingTool", "Run Scene Prep", None))
        self.delineateButton.setText(_translate("FireMappingTool", "Delineate Perimeter", None))
        self.subsetButton.setText(_translate("FireMappingTool", "Subset", None))
        self.openeventButton.setText(_translate("FireMappingTool", "Open Event Folder", None))
        self.metaButton.setText(_translate("FireMappingTool", "Generate Metadata", None))
        self.qacheckButton.setText(_translate("FireMappingTool", "QA Checklist", None))
        self.updatemappingButton.setText(_translate("FireMappingTool", "Update Mapping", None))
        self.checkBox.setText(_translate("FireMappingTool", "Overwrite", None))
        self.createMapButton.setText(_translate("FireMappingTool", "Create New Mapping", None))
        self.processDataButton.setText(_translate("FireMappingTool", "Process ESPA Data", None))
        self.label.setText(_translate("FireMappingTool", "                                Incidents", None))
        self.clearButton.setText(_translate("FireMappingTool", "Clear", None))
        self.getSceneListButton.setText(_translate("FireMappingTool", "Get Scene List", None))
        self.ndviButton.setText(_translate("FireMappingTool", "NDVI Curves", None))
        self.generateButton.setText(_translate("FireMappingTool", "Generate Moderate", None))
        self.label_7.setText(_translate("FireMappingTool", "No Data Threshold", None))
        self.label_8.setText(_translate("FireMappingTool", "Increased Greenness Threshold", None))
        self.label_9.setText(_translate("FireMappingTool", "Mapping Comments", None))
        self.threshButton.setText(_translate("FireMappingTool", "Threshold", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("FireMappingTool", "MTBS", None))
        self.label_6.setText(_translate("FireMappingTool", "Thresholds", None))
        self.label_10.setText(_translate("FireMappingTool", "Revised", None))
        self.label_11.setText(_translate("FireMappingTool", "Mapping Status", None))
        self.label_4.setText(_translate("FireMappingTool", "dNBR Offset", None))
        self.label_12.setText(_translate("FireMappingTool", "SD Offset", None))
        self.dNBRButton.setText(_translate("FireMappingTool", "RdNBR", None))
        self.label_3.setText(_translate("FireMappingTool", "Analysis Type", None))
        self.label_5.setText(_translate("FireMappingTool", "Perimeter Confidence", None))
        self.shapeButton.setText(_translate("FireMappingTool", "OK", None))
        self.label_2.setText(_translate("FireMappingTool", "Perimeter Comments", None))
        self.deleteButton.setText(_translate("FireMappingTool", "Delete Mapping", None))
        self.menuFile.setTitle(_translate("FireMappingTool", "File", None))
        self.menuSearch.setTitle(_translate("FireMappingTool", "Search", None))
        self.menuPreferences.setTitle(_translate("FireMappingTool", "Preferences", None))
        self.actionExit.setText(_translate("FireMappingTool", "Exit", None))
        self.actionSearch_By_Name.setText(_translate("FireMappingTool", "Search By Name", None))
        self.actionSearch_By_Date.setText(_translate("FireMappingTool", "Search By Date", None))
        self.actionSearch_By_Path_Row_and_Year.setText(_translate("FireMappingTool", "Search By Path/Row and Year", None))
        self.actionSearch_By_Year.setText(_translate("FireMappingTool", "Search By Year", None))
        self.actionScript_Locations.setText(_translate("FireMappingTool", "Script Locations", None))
        self.actionGeneral_Settings.setText(_translate("FireMappingTool", "General Settings", None))
        self.actionAdd_Fire.setText(_translate("FireMappingTool", "Add Fire", None))

