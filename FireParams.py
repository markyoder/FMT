"""
/***************************************************************************
Name		     : FMT plugin
Description          : Fire parameters
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Jan 05, 2017
Revised              : Jan 26, 2017
                       Jan 25, 2018 - Removed select scene list
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from Ui_FireParams import Ui_FireParams

from PyQt4 import QtGui


class FireParams(QtGui.QDialog):
    def __init__(self, sceneDir):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_FireParams()
        self.ui.setupUi(self)

        self.latitude = 0.0
        self.longitude = 0.0
        self.begDate = ""
        self.endDate = ""
        self.sceneListFile = ""
        self.sceneDir = sceneDir

        self.ui.beginCalendarWidget.clicked.connect(self.GetDates)
        self.ui.endCalendarWidget.clicked.connect(self.GetDates)
        self.ui.okButton.clicked.connect(self.SetupFireDataSearch)
        self.ui.groupBox.setEnabled(True)

    '''
    Get start date parmeters.
    Args:
        N/A.
    Returns:
        N/A
    '''
    def GetDates(self):
        startDateTemp = self.ui.beginCalendarWidget.selectedDate()
        endDateTemp = self.ui.endCalendarWidget.selectedDate()
        startYear = startDateTemp.year()
        startMonth = startDateTemp.month()
        startDay = startDateTemp.day()
        endYear = endDateTemp.year()
        endMonth = endDateTemp.month()
        endDay = endDateTemp.day()
        self.begDate = (str(startYear) + "-" +
                        str(startMonth).zfill(2) + "-" +
                        str(startDay).zfill(2))
        self.endDate = (str(endYear) + "-" +
                        str(endMonth).zfill(2) + "-" +
                        str(endDay).zfill(2))

        return

    '''
    Get fire data parameters.
    Args:
        N/A.
    Returns:
        N/A
    '''
    def SetupFireDataSearch(self):
        if self.begDate < self.endDate:
            self.latitude = self.ui.latSpinBox.value()
            self.longitude = self.ui.longSpinBox.value()
            self.close()
        else:
            QtGui.QMessageBox.information(None,
                                          u"Error - Date mismatch",
                                          (u"The begin date must be "
                                           "earlier than the end date"),
                                          QtGui.QMessageBox.Ok)
