"""
/***************************************************************************
Name		     : FMT plugin
Description          : Fire Mapping Tool 
copyright            : (C) 2015-2018 by Karthik Vanumamalai, Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 Modified: Feb 14, 2018: Changed event mapping tool to fire mapping tool
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtSql import *
from qgis.utils import *

# Import the code for the dialog
from FireMappingToolWindow import FireMappingToolWindow
import os.path


class FMT:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(
            ":/plugins/.qgis2/FMT/FMT.png"), u"FMT", self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("activated()"), self.eventtool)

        self.actionMain = QAction(u"Fire Mapping Tool", self.iface.mainWindow())
        QObject.connect(self.actionMain, SIGNAL("activated()"), self.eventtool)

        self.menu = QMenu("FMT")
        self.menu.addAction(self.actionMain)
        self.iface.mainWindow().menuBar().insertMenu(
                self.iface.firstRightStandardMenu().menuAction(), self.menu)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removeToolBarIcon(self.action)
        self.menu.deleteLater()

    # run method that performs all the real work
    def eventtool(self):
        self.mainWindow = FireMappingToolWindow()
        self.mainWindow.show()
