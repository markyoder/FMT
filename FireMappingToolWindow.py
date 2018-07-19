"""
/***************************************************************************
Name		     : FMT plugin
Description          : Fire Mapping Tool
copyright            : (C) 2016-17 by Karthik Vanumamalai, Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Aug 23, 2016
Updated              : May 10, 2017 - ESPA functionality
                       Sep 22, 2017 - Comment out HMS functionality for
                           current release.
                       Oct 5, 2017 - Adjusted scene prep to use class.
                       Oct 24, 2017 - Adjusted to use classes for other
                           external scripts.
                       Nov. 17, 2017 - Adjusted to avoid python errors when
                           a fire was not selected when needed.  Global
                           variables to class variables.
                       Dec. 14, 2017 - Add a user message when ESPA processing
                           completes
                       Jan 2, 2018 - Path Row values to 3 digits
                       Jan 17, 2018 - Corrections for L5 and L7 styles
                       Jan 25, 2018 - Removed ESPA order/download functionality
                       Feb 16, 2018 - Change EMT to FMT(Fire Mapping Tool),
                                      remove "program" choice
                       Feb 20, 1018 - Update ShapeAttributes to write to only
                                      one row

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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsMessageLog
from Ui_FireMappingTool import Ui_FireMappingTool
from Ui_AddFire import Ui_AddFire
from Ui_SearchByName import Ui_SearchByName
from Ui_SearchByDate import Ui_SearchByDate
from Ui_SearchByPathRowYear import Ui_SearchByPathRowYear
from Ui_SearchByYear import Ui_SearchByYear
from Ui_SelectInterval import Ui_SelectInterval
from Ui_CreateMapping import Ui_CreateMapping
from Ui_SetStatus import Ui_SetStatus
from FireParams import FireParams
from ScenePrep import ScenePrep
from FirePrep import FirePrep
from SubsetProcess import Subset
from RdNBR import RdNBR
from ThresholdProcess import ThresholdProcess
from GenerateMetadata import GenerateMetadata
from ProcessESPADownload import ProcessESPADownload

from qgis.core import *
from qgis.core import QgsMapLayerRegistry, QgsRasterLayer
from qgis.gui import *
from qgis.utils import iface
from osgeo import osr, ogr, gdal
from pyspatialite import dbapi2 as sqlite
# from subprocess import Popen, PIPE
import ctypes
import datetime
import os
import sys
import getpass
import glob
import ConfigParser
import webbrowser
from urlparse import urlparse, urlunparse
import urllib
from xml.etree import ElementTree

if sys.platform.startswith("win"):
    SEM_NOGPFAULTERRORBOX = 0x0002
    ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
    CREATE_NO_WINDOW = 0x08000000
    subprocess_flags = CREATE_NO_WINDOW
else:
    subprocess_flags = 0

fireLabels = (['Name', 'Mapping Status', 'Acres', 'Event Date', 'EventID',
               'P/R', 'Latitude', 'Longitude', 'Report Date', 'id'])
mapLabels = (['Id', 'Assessment Type', 'Pre-fire Scene',
              'Post-fire Scene', 'Perimeter Scene', 'Mapper', 'Date Created'])

mapTableColCt = 7

# Create the dialog for Fire Mapping Tool
class FireMappingToolWindow(QtGui.QMainWindow):
  def __init__(self):
      QtGui.QMainWindow.__init__(self)
      self.ui = Ui_FireMappingTool()
      self.ui.setupUi(self)
      ConfigDir = os.path.dirname(os.path.realpath(__file__))
      File = 'Config.ini'
      ConfigFile = os.path.join(ConfigDir, File)
      config = ConfigParser.ConfigParser()
      config.read(ConfigFile)
      self.img_src = config.get('config','img_src')
      if not self.img_src.endswith(os.sep):
          self.img_src += os.sep
      self.scene_src = config.get('config','scene_dir')
      if not self.scene_src.endswith(os.sep):
          self.scene_src += os.sep
      #
      ##yoder:
      #print('*** DEBUG: scene_src: {}'.format(self.scene_src))
      #
      self.ndvi_url = config.get('config', 'ndvi_url')
      self.ui.createMapButton.clicked.connect(self.createMapping)
      self.ui.ndviButton.clicked.connect(self.createNDVI)
      self.ui.actionAdd_Fire.triggered.connect(self.addFire)
      self.ui.actionSearch_By_Name.triggered.connect(self.searchbyName)
      self.ui.actionSearch_By_Date.triggered.connect(self.searchbyDate)
      self.ui.actionSearch_By_Path_Row_and_Year.triggered.connect(self.searchbyPathRowYear)
      self.ui.actionSearch_By_Year.triggered.connect(self.searchbyYear)
      self.ui.clearButton.clicked.connect(self.clearFire)
      self.ui.firetableWidget.itemDoubleClicked.connect(self.SelectInterval)
      self.ui.maptableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.ui.maptableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
      self.ui.maptableWidget.itemClicked.connect(self.PopulateData)
      self.ui.sceneprepButton.clicked.connect(self.RunScenePrep)
      self.ui.fireprepButton.clicked.connect(self.RunFirePrep)
      self.ui.subsetButton.clicked.connect(self.ClipSubset)
      self.ui.delineateButton.clicked.connect(self.delineate)
      self.ui.openeventButton.clicked.connect(self.openEventFolder)
      self.ui.shapeButton.clicked.connect(self.ShapeAttributes)
      self.ui.dNBRButton.clicked.connect(self.CreateRdNBR)
      self.ui.threshButton.clicked.connect(self.Threshold)
      self.ui.metaButton.clicked.connect(self.GenMetadata)
      self.ui.qacheckButton.clicked.connect(self.qaChecklist)
      self.ui.deleteButton.clicked.connect(self.deleteMapping)
      self.ui.updatemappingButton.clicked.connect(self.updateMapping)
      self.ui.generateButton.hide()
      self.ui.qacheckButton.hide()
      self.ui.getSceneListButton.clicked.connect(self.GetESPASceneList)
      self.ui.processDataButton.clicked.connect(self.ProcessESPAData)

      analys_type = ['', 'dnbr', 'dndvi', 'nbr', 'ndvi']
      for i in analys_type:
        self.ui.analysisBox.addItem(i) 
      perim_conf = ['','High', 'Low']
      for j in perim_conf:
        self.ui.perimeterBox.addItem(j)
      status = ['', 'in-progress', 'complete']
      for k in status:
        self.ui.mappingBox.addItem(k)
      self.ndvi_year = None
      self.ndvi_pathrow = None
      self.event_id = None
      self.ndvi_event_date = None

  # Creates the Pre/Post fire entries in DB depending upon assessment type.
  def createMapping(self):
        if not self.ui.firetableWidget.currentItem():
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a fire.",
                                       QtGui.QMessageBox.Ok)
            return
        createMapDlg = CreateMappingDialog()
        createMapDlg.show()
        if createMapDlg.exec_():
            dbDir = os.path.dirname(os.path.realpath(__file__))
            dbName = 'FireInfo.sqlite'
            dbFile = os.path.join(dbDir, dbName)
            dbMap = sqlite.connect(dbFile)
            cursor_map = dbMap.cursor()
            maxQ = r"""SELECT MAX(id) AS id FROM 'Mappings'"""
            maxQ = cursor_map.execute(maxQ)
            maxFetch = cursor_map.fetchone()
            if maxFetch[0] is None:
                mapId = 1
            else:
                maxValue = map(lambda x: x+1, maxFetch)
                mapId = maxValue[0]
            mapper = getpass.getuser()
            createDate = datetime.datetime.now()
            row = self.ui.firetableWidget.currentItem().row()
            colCount = self.ui.firetableWidget.columnCount()
            for i in xrange(colCount):
                colName =\
                    self.ui.firetableWidget.horizontalHeaderItem(i).text()
                if colName == 'id':
                    col = i
                    break
            fireId = str(self.ui.firetableWidget.item(row, col).text())
            currentRowCount = self.ui.maptableWidget.rowCount()
            self.ui.maptableWidget.insertRow(currentRowCount)

            self.ui.maptableWidget.setItem(
                currentRowCount, 0, QtGui.QTableWidgetItem(str(mapId)))
            self.ui.maptableWidget.setItem(
                currentRowCount, 1,
                QtGui.QTableWidgetItem(str(createMapDlg.assessStrategy)))
            if createMapDlg.presuppImage is None:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 2, QtGui.QTableWidgetItem(' '))
            else:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 2,
                  QtGui.QTableWidgetItem(str(createMapDlg.presuppImage)))
            if createMapDlg.postImage is None:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 3, QtGui.QTableWidgetItem(' '))
            else:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 3,
                  QtGui.QTableWidgetItem(str(createMapDlg.postImage)))
            if createMapDlg.periImage is None:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 4, QtGui.QTableWidgetItem(' '))
            else:
                self.ui.maptableWidget.setItem(
                  currentRowCount, 4,
                  QtGui.QTableWidgetItem(str(createMapDlg.periImage)))
            self.ui.maptableWidget.setItem(
                currentRowCount, 5, QtGui.QTableWidgetItem(str(mapper)))
            self.ui.maptableWidget.setItem(
                currentRowCount, 6, QtGui.QTableWidgetItem(str(createDate)))
            params = (mapId, fireId, createMapDlg.assessStrategy,
                      createMapDlg.presuppImage, createMapDlg.postImage,
                      createMapDlg.periImage, createMapDlg.presuppSensor,
                      createMapDlg.postSensor, createMapDlg.periSensor,
                      createMapDlg.prefireDate, createMapDlg.postfireDate,
                      createMapDlg.periDate, mapper, createDate,
                      createMapDlg.single_scene, createMapDlg.status,
                      createMapDlg.prePath, createMapDlg.preRow,
                      createMapDlg.postPath, createMapDlg.postRow,
                      createMapDlg.assessStrategy)
            if (createMapDlg.assessStrategy == 'Initial' or
                    createMapDlg.assessStrategy == 'Extended'):
                saveQ = r"""INSERT INTO 'Mappings'"""
                saveQ += """(id, fire_id, strategy, prefire_scene_id,
                             postfire_scene_id, perimeter_scene_id,
                             prefire_sensor, postfire_sensor, perimeter_sensor,
                             prefire_date, postfire_date, perimeter_date,
                             username, created_at, single_scene, status,
                             prefire_path, prefire_row, postfire_path,
                             postfire_row, predicted_strategy) VALUES(
                             ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
            else:
                saveQ = r"""INSERT INTO 'Mappings'"""
                saveQ += """(id, fire_id, strategy, supplementary_scene_id,
                             postfire_scene_id, perimeter_scene_id,
                             supplementary_sensor, postfire_sensor,
                             perimeter_sensor, supplementary_date,
                             postfire_date, perimeter_date, username,
                             created_at, single_scene, status, prefire_path,
                             prefire_row, postfire_path, postfire_row,
                             predicted_strategy) VALUES(
                             ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

            saveParam = cursor_map.execute(saveQ, params)
            dbMap.commit()
            dbMap.close()

  # #Function to add a fire entry to DB
  def addFire(self):
        addFireDlg = AddFireDialog()
        addFireDlg.show()
        addFireDlg.exec_()

  # #Function to open the url to display NDVI Graph for corresponding path/row
  def createNDVI(self):
        if self.ndvi_year is None or\
                self.ndvi_pathrow is None or self.ndvi_event_date is None:
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a fire.",
                                       QtGui.QMessageBox.Ok)
            return
        var = 1
        scheme, netloc, path, params, query, fragment = urlparse(self.ndvi_url)
        # can only have 2 digit path rows for ndvi
        tempPath = self.ndvi_pathrow[1:3] + self.ndvi_pathrow[5:7]
        join_string = ('year=' + self.ndvi_year +
                       '&pathrow=' + tempPath +
                       '&eventDate=' + self.ndvi_event_date)
        new_query = query.replace(query, join_string)
        url = urlunparse((scheme, netloc, path, params, new_query, fragment))
        webbrowser.open(url, new=var)

  def clearFire(self):
        self.ui.firetableWidget.setRowCount(0)
        self.ui.incidentCount.setText('')

  # FIXME - ALL THESE SEARCH BY FUNCTIONS ARE SIMILAR, CAN WE DO A HELPER FUNC?
  # #Function to query the DB by name and populate the firetable
  def searchbyName(self):
      nameSearchDlg = SearchByNameDialog()
      nameSearchDlg.show()
      if nameSearchDlg.exec_():
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbFire = sqlite.connect(dbFile) 
        cursor_fire = dbFire.cursor()          
        fireQ = r"""SELECT incident_name, mapping_status, area_burned, ig_date, event_id, path1, row1,
                 ig_lat, ig_long, report_date, id FROM 'Fires'"""
        fireQ += """ WHERE incident_name LIKE '%"""
        fireQ += str(nameSearchDlg.selectedName)
        fireQ += """%'"""
        fireParam = cursor_fire.execute(fireQ)
        self.ui.firetableWidget.setRowCount(0)
        self.ui.firetableWidget.setColumnCount(10)
        self.ui.firetableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.firetableWidget.setHorizontalHeaderLabels(fireLabels)
        self.ui.firetableWidget.setSortingEnabled(True)
        self.ui.firetableWidget.resizeColumnsToContents()
        self.ui.firetableWidget.resizeRowsToContents()
        self.ui.firetableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.firetableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.firetableWidget.itemClicked.connect(self.SelectMapping)
        #self.ui.firetableWidget.itemDoubleClicked.connect(self.SelectInterval)
        self.ui.maptableWidget.setColumnCount(mapTableColCt)
        self.ui.maptableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.maptableWidget.setHorizontalHeaderLabels(mapLabels)
        tempId = ''
        for i in cursor_fire:
          currentRowCount = self.ui.firetableWidget.rowCount()
          self.ui.firetableWidget.insertRow(currentRowCount)
          self.ui.firetableWidget.setItem(currentRowCount,0,QtGui.QTableWidgetItem(str(i[0])))
          self.ui.firetableWidget.setItem(currentRowCount,1,QtGui.QTableWidgetItem(str(i[1])))
          self.ui.firetableWidget.setItem(currentRowCount,2,QtGui.QTableWidgetItem(str(i[2])))
          self.ui.firetableWidget.setItem(currentRowCount,3,QtGui.QTableWidgetItem(str(i[3])))
          self.ui.firetableWidget.setItem(currentRowCount,4,QtGui.QTableWidgetItem(str(i[4])))
          self.ui.firetableWidget.setItem(currentRowCount,5,QtGui.QTableWidgetItem(str(i[5]) + '/' + str(i[6])))
          self.ui.firetableWidget.setItem(currentRowCount,6,QtGui.QTableWidgetItem(str(i[7])))
          self.ui.firetableWidget.setItem(currentRowCount,7,QtGui.QTableWidgetItem(str(i[8])))
          self.ui.firetableWidget.setItem(currentRowCount,8,QtGui.QTableWidgetItem(str(i[9])))
          self.ui.firetableWidget.setItem(currentRowCount,9,QtGui.QTableWidgetItem(str(i[10])))
          tempId = i[10]
        totalCells = self.ui.firetableWidget.rowCount()
        self.ui.incidentCount.setText(str(totalCells))
        cursor_map = dbFire.cursor()
        mapQ = r"""SELECT id, strategy, prefire_scene_id, postfire_scene_id,
                perimeter_scene_id, username, created_at FROM 'Mappings'"""
        mapQ += """ WHERE fire_id = '"""
        mapQ += str(tempId)
        mapQ += """'"""
        mapParam = cursor_map.execute(mapQ)
        self.ui.maptableWidget.setRowCount(0)
        self.ui.maptableWidget.setEditTriggers(
                QtGui.QAbstractItemView.NoEditTriggers)
        for j in cursor_map:
                currentRowCount = self.ui.maptableWidget.rowCount()
                self.ui.maptableWidget.insertRow(currentRowCount)
                for k in range(mapTableColCt):
                    self.ui.maptableWidget.setItem(
                            currentRowCount, k,
                            QtGui.QTableWidgetItem(str(j[k])))
        dbFire.close()


##Function to query the DB by date and populate the firetable

  def searchbyDate(self):
      dateSearchDlg = SearchByDateDialog()
      dateSearchDlg.show()
      if dateSearchDlg.exec_():
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbFire = sqlite.connect(dbFile) 
        cursor_fire = dbFire.cursor()        
        fire = r"""SELECT incident_name, mapping_status, area_burned, ig_date, event_id, path1, row1,
                 ig_lat, ig_long, report_date, id, expected_containment_date, actual_containment_date FROM 'Fires'"""
        fire += """ WHERE """
        fire += str(dateSearchDlg.selectedCriteria)
        fire += """ BETWEEN '"""
        fire += str(dateSearchDlg.selectedStartDate)
        fire += """' AND '"""
        fire += str(dateSearchDlg.selectedEndDate)
        fire += """'"""
        fireParam = cursor_fire.execute(fire)

        self.ui.firetableWidget.setRowCount(0)
        self.ui.firetableWidget.setColumnCount(10)
        self.ui.firetableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.firetableWidget.setHorizontalHeaderLabels(fireLabels)
        self.ui.firetableWidget.setSortingEnabled(True)
        self.ui.firetableWidget.resizeColumnsToContents()
        self.ui.firetableWidget.resizeRowsToContents()
        self.ui.firetableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.firetableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.firetableWidget.itemClicked.connect(self.SelectMapping)
        #self.ui.firetableWidget.itemDoubleClicked.connect(self.SelectInterval)
        self.ui.maptableWidget.setColumnCount(mapTableColCt)
        self.ui.maptableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.maptableWidget.setHorizontalHeaderLabels(mapLabels)      
        tempId = ''
        for i in cursor_fire:
          currentRowCount = self.ui.firetableWidget.rowCount()
          self.ui.firetableWidget.insertRow(currentRowCount)
          self.ui.firetableWidget.setItem(currentRowCount,0,QtGui.QTableWidgetItem(str(i[0])))
          self.ui.firetableWidget.setItem(currentRowCount,1,QtGui.QTableWidgetItem(str(i[1])))
          self.ui.firetableWidget.setItem(currentRowCount,2,QtGui.QTableWidgetItem(str(i[2])))
          self.ui.firetableWidget.setItem(currentRowCount,3,QtGui.QTableWidgetItem(str(i[3])))
          self.ui.firetableWidget.setItem(currentRowCount,4,QtGui.QTableWidgetItem(str(i[4])))
          self.ui.firetableWidget.setItem(currentRowCount,5,QtGui.QTableWidgetItem(str(i[5]) + '/' + str(i[6])))
          self.ui.firetableWidget.setItem(currentRowCount,6,QtGui.QTableWidgetItem(str(i[7])))
          self.ui.firetableWidget.setItem(currentRowCount,7,QtGui.QTableWidgetItem(str(i[8])))
          self.ui.firetableWidget.setItem(currentRowCount,8,QtGui.QTableWidgetItem(str(i[9])))
          self.ui.firetableWidget.setItem(currentRowCount,9,QtGui.QTableWidgetItem(str(i[10])))
          tempId = i[10]
        totalCells = self.ui.firetableWidget.rowCount()
        self.ui.incidentCount.setText(str(totalCells))
        cursor_map = dbFire.cursor()
        mapQ = r"""SELECT id, strategy, prefire_scene_id, postfire_scene_id, perimeter_scene_id,
                   username, created_at FROM 'Mappings'""" 
        mapQ += """ WHERE fire_id = '"""
        mapQ += str(tempId)
        mapQ += """'"""
        mapParam = cursor_map.execute(mapQ)
        self.ui.maptableWidget.setRowCount(0)
        self.ui.maptableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        for j in cursor_map:
                currentRowCount = self.ui.maptableWidget.rowCount()
                self.ui.maptableWidget.insertRow(currentRowCount)
                for k in range(mapTableColCt):
                    self.ui.maptableWidget.setItem(
                            currentRowCount, k,
                            QtGui.QTableWidgetItem(str(j[k])))
        dbFire.close()

  # #Function to query the DB by Path/Row and Year and populate the firetable
  def searchbyPathRowYear(self):
      prySearchDlg = SearchByPathRowYearDialog()
      prySearchDlg.show()
      if prySearchDlg.exec_():
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbFire = sqlite.connect(dbFile) 
        cursor_fire = dbFire.cursor()  
        fire = r"""SELECT incident_name, mapping_status, area_burned, ig_date, event_id, path1, row1,
                 ig_lat, ig_long, report_date, id FROM 'Fires'"""
        fire += """ WHERE strftime('%Y',ig_date) = '"""
        fire += str(prySearchDlg.selectedYear)
        fire += """' AND path1 = '"""
        fire += str(prySearchDlg.selectedPath)
        fire += """' AND row1 = '"""
        fire += str(prySearchDlg.selectedRow)
        fire += """'"""
        fireParam = cursor_fire.execute(fire)
 
        self.ui.firetableWidget.setRowCount(0)
        self.ui.firetableWidget.setColumnCount(10)
        self.ui.firetableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.firetableWidget.setHorizontalHeaderLabels(fireLabels)
        self.ui.firetableWidget.setSortingEnabled(True)
        self.ui.firetableWidget.resizeColumnsToContents()
        self.ui.firetableWidget.resizeRowsToContents()
        self.ui.firetableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.firetableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.firetableWidget.itemClicked.connect(self.SelectMapping)
        #self.ui.firetableWidget.itemDoubleClicked.connect(self.SelectInterval)
        self.ui.maptableWidget.setColumnCount(mapTableColCt)
        self.ui.maptableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.maptableWidget.setHorizontalHeaderLabels(mapLabels)
        tempId = ''
        for i in cursor_fire:
          currentRowCount = self.ui.firetableWidget.rowCount()
          self.ui.firetableWidget.insertRow(currentRowCount)
          self.ui.firetableWidget.setItem(currentRowCount,0,QtGui.QTableWidgetItem(str(i[0])))
          self.ui.firetableWidget.setItem(currentRowCount,1,QtGui.QTableWidgetItem(str(i[1])))
          self.ui.firetableWidget.setItem(currentRowCount,2,QtGui.QTableWidgetItem(str(i[2])))
          self.ui.firetableWidget.setItem(currentRowCount,3,QtGui.QTableWidgetItem(str(i[3])))
          self.ui.firetableWidget.setItem(currentRowCount,4,QtGui.QTableWidgetItem(str(i[4])))
          self.ui.firetableWidget.setItem(currentRowCount,5,QtGui.QTableWidgetItem(str(i[5]) + '/' + str(i[6])))
          self.ui.firetableWidget.setItem(currentRowCount,6,QtGui.QTableWidgetItem(str(i[7])))
          self.ui.firetableWidget.setItem(currentRowCount,7,QtGui.QTableWidgetItem(str(i[8])))
          self.ui.firetableWidget.setItem(currentRowCount,8,QtGui.QTableWidgetItem(str(i[9])))
          self.ui.firetableWidget.setItem(currentRowCount,9,QtGui.QTableWidgetItem(str(i[10])))
          tempId = i[10]
        totalCells = self.ui.firetableWidget.rowCount()
        self.ui.incidentCount.setText(str(totalCells))
        cursor_map = dbFire.cursor() 
        mapQ = r"""SELECT id, strategy, prefire_scene_id, postfire_scene_id, perimeter_scene_id,
                   username, created_at FROM 'Mappings'""" 
        mapQ += """ WHERE fire_id = '"""
        mapQ += str(tempId)
        mapQ += """'"""
        mapParam = cursor_map.execute(mapQ)
        self.ui.maptableWidget.setRowCount(0)
        self.ui.maptableWidget.setEditTriggers(
                QtGui.QAbstractItemView.NoEditTriggers)
        for j in cursor_map:
                currentRowCount = self.ui.maptableWidget.rowCount()
                self.ui.maptableWidget.insertRow(currentRowCount)
                for k in range(mapTableColCt):
                    self.ui.maptableWidget.setItem(
                            currentRowCount, k,
                            QtGui.QTableWidgetItem(str(j[k])))
        dbFire.close()

  # #Function to query the DB by Year and populate the firetable
  def searchbyYear(self):
      yearSearchDlg = SearchByYearDialog()
      yearSearchDlg.show()
      if yearSearchDlg.exec_():              
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbFire = sqlite.connect(dbFile) 
        cursor_fire = dbFire.cursor()     
        fire = r"""SELECT incident_name, mapping_status, area_burned, ig_date, event_id, path1, row1,
                 ig_lat, ig_long, report_date, id FROM 'Fires'""" 
        fire += """ WHERE strftime('%Y',ig_date) = '"""
        fire += str(yearSearchDlg.selectedYear)
        fire += """'"""
        fireParam = cursor_fire.execute(fire)

        self.ui.firetableWidget.setRowCount(0)
        self.ui.firetableWidget.setColumnCount(10)
        self.ui.firetableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ui.firetableWidget.setHorizontalHeaderLabels(fireLabels)
        self.ui.firetableWidget.setSortingEnabled(True)
        self.ui.firetableWidget.resizeColumnsToContents()
        self.ui.firetableWidget.resizeRowsToContents()
        self.ui.firetableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.firetableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ui.firetableWidget.itemClicked.connect(self.SelectMapping)
        self.ui.maptableWidget.itemClicked.connect(self.GetMapping)
        #self.ui.firetableWidget.itemDoubleClicked.connect(self.SelectInterval)
        self.ui.maptableWidget.setColumnCount(mapTableColCt)
        self.ui.maptableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.ui.maptableWidget.setHorizontalHeaderLabels(mapLabels)
        tempId = ''
        for i in cursor_fire:
          currentRowCount = self.ui.firetableWidget.rowCount()
          self.ui.firetableWidget.insertRow(currentRowCount)
          self.ui.firetableWidget.setItem(currentRowCount,0,QtGui.QTableWidgetItem(str(i[0])))
          self.ui.firetableWidget.setItem(currentRowCount,1,QtGui.QTableWidgetItem(str(i[1])))
          self.ui.firetableWidget.setItem(currentRowCount,2,QtGui.QTableWidgetItem(str(i[2])))
          self.ui.firetableWidget.setItem(currentRowCount,3,QtGui.QTableWidgetItem(str(i[3])))
          self.ui.firetableWidget.setItem(currentRowCount,4,QtGui.QTableWidgetItem(str(i[4])))
          self.ui.firetableWidget.setItem(currentRowCount,5,QtGui.QTableWidgetItem(str(i[5]) + '/' + str(i[6])))
          self.ui.firetableWidget.setItem(currentRowCount,6,QtGui.QTableWidgetItem(str(i[7])))
          self.ui.firetableWidget.setItem(currentRowCount,7,QtGui.QTableWidgetItem(str(i[8])))
          self.ui.firetableWidget.setItem(currentRowCount,8,QtGui.QTableWidgetItem(str(i[9])))
          self.ui.firetableWidget.setItem(currentRowCount,9,QtGui.QTableWidgetItem(str(i[10])))
          tempId = i[10]
        totalCells = self.ui.firetableWidget.rowCount()
        self.ui.incidentCount.setText(str(totalCells))
        cursor_map = dbFire.cursor() 
        mapQ = r"""SELECT id, strategy, prefire_scene_id, postfire_scene_id, perimeter_scene_id,
                     username, created_at FROM 'Mappings'""" 
        mapQ += """ WHERE fire_id = '"""
        mapQ += str(tempId)
        mapQ += """'"""
        mapParam = cursor_map.execute(mapQ)
        self.ui.maptableWidget.setRowCount(0)
        self.ui.maptableWidget.setEditTriggers(
                QtGui.QAbstractItemView.NoEditTriggers)
        for j in cursor_map:
                currentRowCount = self.ui.maptableWidget.rowCount()
                self.ui.maptableWidget.insertRow(currentRowCount)
                for k in range(mapTableColCt):
                    self.ui.maptableWidget.setItem(
                            currentRowCount, k,
                            QtGui.QTableWidgetItem(str(j[k])))
        dbFire.close()

  # # Function to display mapping event corresponding to the selected fire event
  def SelectMapping(self):
        if not self.ui.firetableWidget.currentItem():
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a fire.",
                                       QtGui.QMessageBox.Ok)
            return
        row = self.ui.firetableWidget.currentItem().row()
        colCount = self.ui.firetableWidget.columnCount()
        for i in xrange(colCount):
            colName = self.ui.firetableWidget.horizontalHeaderItem(i).text()
            if colName == 'id':
                col = i
            elif colName == 'Event Date':
                year = i
            elif colName == 'P/R':
                pr = i
            elif colName == 'EventID':
                e_id = i
        item = self.ui.firetableWidget.item(row, col).text()

        self.ndvi_year = self.ui.firetableWidget.item(row, year).text()[0:4]
        ndvi_pr = self.ui.firetableWidget.item(row, pr).text()

#        self.ndvi_pathrow = ndvi_pr.replace('/', '')
        tempList = ndvi_pr.split('/')
        self.ndvi_pathrow = tempList[0].zfill(3) + "_" + tempList[1].zfill(3)

        self.ndvi_event_date = self.ui.firetableWidget.item(row, year).text()
        self.event_id = self.ui.firetableWidget.item(row, e_id).text()
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbMap = sqlite.connect(dbFile)
        cursor_map = dbMap.cursor()
        mapQ = r"""SELECT id, strategy, prefire_scene_id, postfire_scene_id,
                   perimeter_scene_id, username, created_at FROM 'Mappings'"""
        mapQ += """ WHERE fire_id = '"""
        mapQ += str(item)
        mapQ += """'"""
        mapParam = cursor_map.execute(mapQ)
        self.ui.maptableWidget.setRowCount(0)
        for j in cursor_map:
                currentRowCount = self.ui.maptableWidget.rowCount()
                self.ui.maptableWidget.insertRow(currentRowCount)
                for k in range(mapTableColCt):
                    self.ui.maptableWidget.setItem(
                            currentRowCount, k,
                            QtGui.QTableWidgetItem(str(j[k])))
        dbMap.close()

  # Get the mapping id from selected mapping
  def GetMapping(self):
        mapping_id = None
        if self.ui.maptableWidget.currentItem() is None:
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a mapping.",
                                       QtGui.QMessageBox.Ok)
        else:
            row = self.ui.maptableWidget.currentItem().row()
            colCount = self.ui.maptableWidget.columnCount()
            for i in xrange(colCount):
                colName = self.ui.maptableWidget.horizontalHeaderItem(i).text()
                if colName == 'Id':
                    col = i
            mapping_id = self.ui.maptableWidget.item(row, col).text()
        return mapping_id

  # #Function to select the ESPA/Full Scenes between years
  def SelectInterval(self):
        row = self.ui.firetableWidget.currentItem().row()
        colCount = self.ui.firetableWidget.columnCount()
        for i in xrange(colCount):
            colName =\
                self.ui.firetableWidget.horizontalHeaderItem(i).text()
            if colName == 'P/R':
                col = i
                break
        pathRow = str(self.ui.firetableWidget.item(row, col).text()).split('/')
        path = pathRow[0].zfill(3)
        row = pathRow[1].zfill(3)
        self.ndvi_pathrow = path + row
        dirList = glob.glob(os.path.join(self.img_src, self.ndvi_pathrow, "*"))
        yrList = []
        for entry in dirList:
            yr = entry[-12:-8]
            if yr not in yrList:
                yrList.append(yr)

        yrList.sort()

        intervalDlg = SelectIntervalDialog(self.img_src, self.ndvi_pathrow)
        if intervalDlg is None:
            intervalDlg.show()
        if intervalDlg.exec_():
            preYear = int(intervalDlg.preYear)
            postYear = int(intervalDlg.postYear)
            imageList = []
            for year in range(preYear, postYear+1, 1):
                folder = '*' + str(year) + '*'
                for image in glob.glob(os.path.join(self.img_src,
                                                    self.ndvi_pathrow,
                                                    folder,
                                                    '*_REFL.TIF')):
                    imageList.append(image)

            if not imageList:
                QtGui.QMessageBox.information(self,
                                              "Information",
                                              "No Images to load ({} :: {})".format(self.img_src, self.ndvi_pathrow),
                                              QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(
                    self,
                    "Information",
                    "Number of Images loading: %s" % len(imageList),
                    QtGui.QMessageBox.Ok)
                currentLayers = QgsMapLayerRegistry.instance().mapLayers()
                for name, layer in currentLayers.iteritems():
                    QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

            for srcimage in imageList:
                rasterLyr =\
                    QgsRasterLayer(srcimage, os.path.basename(srcimage))
                clrDir = os.path.dirname(os.path.realpath(__file__))
                if os.path.basename(srcimage).startswith('5'):
                    stylePath = 'Style/L5Style.qml'
                elif os.path.basename(srcimage).startswith('7'):
                    stylePath = 'Style/L7Style.qml'
                elif os.path.basename(srcimage).startswith('8'):
                    stylePath = 'Style/L8Style.qml'
                else:
                    stylePath = ''
                styleFile = os.path.join(clrDir, stylePath)
                rasterLyr.loadNamedStyle(styleFile)
                QgsMapLayerRegistry.instance().addMapLayer(rasterLyr)
        intervalDlg.close()

  def PopulateData(self):
      mapping_id = self.GetMapping()
      if mapping_id is None:
          return
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbMap = sqlite.connect(dbFile)

      dbCursor = dbMap.cursor()
      dataCols = "SELECT analysis,dnbr_offset,perimeter_confidence,threshold1,threshold2,threshold3,no_data_thresh,"\
                 "greenness_thresh,status,single_scene,standard_deviation,perimeter_comments,mapping_comments FROM 'Mappings'" +\
                 'WHERE id = ' +\
                  mapping_id
      dataColsExec = dbCursor.execute(dataCols)

      for i in dataColsExec:
         if i[0] == 'dnbr':
             self.ui.analysisBox.setCurrentIndex(1)
         elif i[0] == 'dndvi':
             self.ui.analysisBox.setCurrentIndex(2)
         elif i[0] == 'nbr':
             self.ui.analysisBox.setCurrentIndex(3)
         elif i[0] == 'ndvi':
             self.ui.analysisBox.setCurrentIndex(4)
             
         self.ui.offsetLineEdit.setText(i[1])
       
         if i[2] == 'High':
             self.ui.perimeterBox.setCurrentIndex(1)
         elif i[2] == 'Low':
             self.ui.perimeterBox.setCurrentIndex(2)

         self.ui.thresh1LineEdit.setText(str(i[3]))
         self.ui.thresh2LineEdit.setText(str(i[4]))
         self.ui.thresh3LineEdit.setText(str(i[5]))
         self.ui.nothreshLineEdit.setText(str(i[6]))
         self.ui.greenthreshLineEdit.setText(str(i[7]))
         self.ui.sdLineEdit.setText(str(i[10]))

         if i[8] == 'in-progress':
             self.ui.mappingBox.setCurrentIndex(1)
         elif i[8] == 'complete':
             self.ui.mappingBox.setCurrentIndex(2)

         if i[9] == '1':
             self.ui.sceneprepButton.setEnabled(False)
             self.ui.groupBox_3.setEnabled(False)
         else:
             self.ui.sceneprepButton.setEnabled(True)
             self.ui.groupBox_3.setEnabled(True)

         self.ui.perimeterTextEdit.setPlainText(str(i[11]))
         self.ui.mappingTextEdit.setPlainText(str(i[12]))
         
      dataColsExec.close()
      dbMap.close()
      QgsMapLayerRegistry.instance().removeAllMapLayers()
      QgsMessageLog.logMessage(r'Mapping selection change - clear map panel',
                               level=QgsMessageLog.CRITICAL)

  # Creates mask/dNBR image
  def RunScenePrep(self):
        mapping_id = self.GetMapping()
        if not mapping_id:
            return
        single_scene = self.SingleScene(mapping_id)
        if single_scene == 1:  # True
            QtGui.QMessageBox.critical(None,
                                       "Error!",
                                       ("Mapping is single scene.\n"
                                        "Exiting scene prep."),
                                       QtGui.QMessageBox.Ok)
            return
        if self.ui.checkBox.isChecked():
            resp = QtGui.QMessageBox.warning(None,
                                             "Warning",
                                             ("This process will overwrite "
                                              "the files.\n"
                                              "Do you want to proceed?\n"
                                              "Press OK to continue or "
                                              "Cancel to exit."),
                                             QtGui.QMessageBox.Ok,
                                             QtGui.QMessageBox.Cancel)
            if resp == QtGui.QMessageBox.Ok:
                overwrite = True
            else:
                iface.mainWindow().statusBar().showMessage(
                    "Scene Prep Cancelled")
                return
        else:
            overwrite = False
        self.DisableContols()
        iface.mainWindow().statusBar().showMessage("Running Scene Prep...")
        scenePrep = ScenePrep(mapping_id, self.img_src, overwrite)
        scenePrep.ProcessScenePrep()
        self.EnableContols()
        iface.mainWindow().statusBar().showMessage("Completed Scene Prep")

  # Creates the Qgis project files corresponding to the mapping id
  def RunFirePrep(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        iface.mainWindow().statusBar().showMessage("Running Fire Prep")
        self.DisableContols()
        fPrep = FirePrep(mapping_id, self.scene_src)
        fPrep.ProcessFirePrep()
        self.EnableContols()
        iface.mainWindow().statusBar().showMessage("Completed Fire Prep")

  # Delineate loads the project files so that a perimeter may be drawn
  # if necessary
  def delineate(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return

        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbMap = sqlite.connect(dbFile)
        cursor_map = dbMap.cursor()
        sql = "SELECT * FROM 'Mappings' WHERE id = " + mapping_id
        query = cursor_map.execute(sql)
        fetch = cursor_map.fetchone()
        fire_id = str(fetch[1])
        sql = "SELECT * FROM 'Fires' WHERE id = " + fire_id
        query = cursor_map.execute(sql)
        fetch = cursor_map.fetchone()
        mtbs_id = fetch[1]
        fire_date = fetch[4]
        StrFireDate = str(fire_date).split('-')
        FireYear = StrFireDate[0]

        # Make Fire Folder
        mapping_folder = os.path.join(self.scene_src,
                                      'event_prods',
                                      'fire',
                                      FireYear,
                                      mtbs_id.lower(),
                                      ('mtbs_' + mapping_id))
        for infile in glob.glob(os.path.join(mapping_folder, '*.qgs')):
            QgisProj = infile
        if QgisProj:
            QgsProject.instance().read(QFileInfo(QgisProj))
        else:
            QtGui.QMessageBox.warning(None,
                                      'No project file found',
                                      'Run "Fire Prep"',
                                      QtGui.QMessageBox.Ok)
            return
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layers.iteritems():
            clrDir = os.path.dirname(os.path.realpath(__file__))
            if layer.name().startswith('Post_Scene_Refl (5') or\
                    layer.name().startswith('Pre_Scene_Refl (5') or\
                    layer.name().startswith('Perim_Scene_Refl (5'):
                stylePath = 'Style/L5Style.qml'
                styleFile = os.path.join(clrDir, stylePath)
                layer.loadNamedStyle(styleFile)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
            elif layer.name().startswith('Post_Scene_Refl (7') or\
                    layer.name().startswith('Pre_Scene_Refl (7') or\
                    layer.name().startswith('Perim_Scene_Refl (7'):
                stylePath = 'Style/L7Style.qml'
                styleFile = os.path.join(clrDir, stylePath)
                layer.loadNamedStyle(styleFile)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
            elif layer.name().startswith('Post_Scene_Refl (8') or\
                    layer.name().startswith('Pre_Scene_Refl (8') or\
                    layer.name().startswith('Perim_Scene_Refl (8'):
                stylePath = 'Style/L8Style.qml'
                styleFile = os.path.join(clrDir, stylePath)
                layer.loadNamedStyle(styleFile)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
        QtGui.QMessageBox.information(None,
                                      'Status',
                                      'Qgis Project files are loaded',
                                      QtGui.QMessageBox.Ok)

##Function to open the Fire folder

  def openEventFolder(self):
      # TODO: looks like this (and maybe some other) scripts are hard-coded with "\" (in the form of "\\"), "back-slash" delimiters.
      # ... so this totally breaks under Linux, (and Mac?)
      mapping_id = self.GetMapping()
      if mapping_id is None:
            return
      #
      # yoder:
      event_prods_path = os.path.join(self.scene_src, 'event_prods', 'fire')
      #event_prods_path = os.path.join(self.scene_src, 'event_prods\\fire\\')
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbMap = sqlite.connect(dbFile) 
      cursor_map = dbMap.cursor()
      sql = "SELECT * FROM 'Mappings'" +\
            'WHERE id = ' +\
             mapping_id
      query = cursor_map.execute(sql)
      fetch = cursor_map.fetchone()
      fire_id = str(fetch[1])
      sql = "SELECT * FROM 'Fires'" +\
            'WHERE id = ' +\
            str(fire_id)
      query = cursor_map.execute(sql)
      fetch = cursor_map.fetchone()
      mtbs_id = fetch[1]
      fire_date = fetch[4]
      StrFireDate = str(fire_date).split('-')
      FireYear = StrFireDate[0]

      # Make Fire Folder
      # yoder:
      fire_year_folder = os.path.join(event_prods_path, FireYear)
      #fire_year_folder = event_prods_path +\
      #                 FireYear +\
      #                 '\\'
      fire_folder = os.path.join(fire_year_folder, mtbs_id.lower())
      #fire_folder = fire_year_folder +\
      #            mtbs_id.lower() +\
      #            '\\'
      mapping_folder = os.path.join(fire_folder, 'mtbs_'.format(mapping_id))
      #mapping_folder = fire_folder +\
      #               'mtbs_' +\
      #               mapping_id +\
      #               '\\'
      os.startfile(mapping_folder)


  # Function to calculate dNBR offset and threshold values
  def ClipSubset(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        iface.mainWindow().statusBar().showMessage("Running Subset")
        self.DisableContols()
        single_scene = self.SingleScene(mapping_id)
        sbst = Subset(mapping_id, self.scene_src, single_scene)
        var1, var2, var3, var4, var5, var6, var7, var8 = sbst.ProcessSubset()

        self.ui.offsetLineEdit.setText(var1)
        self.ui.thresh1LineEdit.setText(var2)
        self.ui.thresh2LineEdit.setText(var3)
        self.ui.thresh3LineEdit.setText(var4)
        self.ui.nothreshLineEdit.setText('-970')
        self.ui.greenthreshLineEdit.setText(var5)
        self.ui.sdLineEdit.setText(var6)

        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbUpdate = sqlite.connect(dbFile)
        dbCursor = dbUpdate.cursor()

        updCols = r"""UPDATE 'Mappings' SET burn_bndy_alb_x = '"""
        updCols += var7
        updCols += """',burn_bndy_alb_y = '"""
        updCols += var8
        updCols += """' WHERE id = '"""
        updCols += str(mapping_id)
        updCols += """'"""

        dataupdColsExec = dbCursor.execute(updCols)
        dbUpdate.commit()
        dataupdColsExec.close()
        dbUpdate.close()

        self.EnableContols()
        iface.mainWindow().statusBar().showMessage("Completed Subset")

  def ShapeAttributes(self):
        # this sets the perimeter confidence columns
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbUpdate = sqlite.connect(dbFile)
        dbCursor = dbUpdate.cursor()

        updCols = r"""UPDATE 'Mappings' SET perimeter_confidence = '"""
        updCols += str(self.ui.perimeterBox.currentText())
        updCols += """',perimeter_comments = '"""
        updCols += str(self.ui.perimeterTextEdit.toPlainText())
        updCols += """' WHERE id = '"""
        updCols += str(mapping_id)
        updCols += """'"""

        dataupdColsExec = dbCursor.execute(updCols)
        dbUpdate.commit()
        dataupdColsExec.close()
        dbUpdate.close()

        QtGui.QMessageBox.information(None,
                                      'Status',
                                      'Shape attributes are populated',
                                      QtGui.QMessageBox.Ok)

  # Function to create RdNBR image
  def CreateRdNBR(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        iface.mainWindow().statusBar().showMessage("Creating RnDBR")
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbUpdate = sqlite.connect(dbFile)
        dbCursor = dbUpdate.cursor()

        updCols = r"""UPDATE 'Mappings' SET analysis = '"""
        updCols += str(self.ui.analysisBox.currentText())
        updCols += """',dnbr_offset = '"""
        updCols += str(self.ui.offsetLineEdit.text())
        updCols += """',standard_deviation = '"""
        updCols += str(self.ui.sdLineEdit.text())
        updCols += """' WHERE id = '"""
        updCols += str(mapping_id)
        updCols += """'"""

        dataupdColsExec = dbCursor.execute(updCols)
        dbUpdate.commit()
        dataupdColsExec.close()
        dbUpdate.close()
        rdnbr = RdNBR(mapping_id,
                      self.scene_src,
                      str(self.ui.offsetLineEdit.text()))
        rdnbr.RdNBRProcess()
        iface.mainWindow().statusBar().showMessage("RnDBR Completed")

  def generateMedian(self):
        QtGui.QMessageBox.information(
            None,
            'Information',
            'Funtionality for generating moderate threshold '
            'has not been implemented yet.',
            QtGui.QMessageBox.Ok)

  # Function to create final image after applying threshold values
  def Threshold(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        low = str(self.ui.thresh1LineEdit.text())
        mod = str(self.ui.thresh2LineEdit.text())
        high = str(self.ui.thresh3LineEdit.text())
        regrowth = str(self.ui.greenthreshLineEdit.text())
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbUpdate = sqlite.connect(dbFile)
        dbCursor = dbUpdate.cursor()

        updCols = r"""UPDATE 'Mappings' SET threshold1 = '"""
        updCols += low
        updCols += """',threshold2 = '"""
        updCols += mod
        updCols += """',threshold3 = '"""
        updCols += high
        updCols += """',no_data_thresh = '"""
        updCols += str(self.ui.nothreshLineEdit.text())
        updCols += """',greenness_thresh = '"""
        updCols += regrowth
        updCols += """',mapping_comments = '"""
        updCols += str(self.ui.mappingTextEdit.toPlainText())
        updCols += """' WHERE id = '"""
        updCols += str(mapping_id)
        updCols += """'"""

        dataupdColsExec = dbCursor.execute(updCols)
        dbUpdate.commit()
        dataupdColsExec.close()
        dbUpdate.close()
        iface.mainWindow().statusBar().showMessage("Threshold Calculating")
        thresh = ThresholdProcess(mapping_id,
                                  self.scene_src,
                                  low,
                                  mod,
                                  high,
                                  regrowth)
        thresh.CalcThresholds()
        iface.mainWindow().statusBar().showMessage("Threshold Completed")

  # Function to generate Metadata
  def GenMetadata(self):
        mapping_id = self.GetMapping()
        if mapping_id is None:
            return
        iface.mainWindow().statusBar().showMessage("Generating Metadata")
        md = GenerateMetadata(mapping_id, self.scene_src)
        md.GenerateMetadataProcess()
        iface.mainWindow().statusBar().showMessage("Metadata Completed")

  def qaChecklist(self):
      QtGui.QMessageBox.information(None, 'Information',\
                                           'Funtionality for QA has not been implemented yet.',\
                                           QtGui.QMessageBox.Ok)
          
##Returns if the assessment type is single scene or not

  def SingleScene(self,mappingId):
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbMap = sqlite.connect(dbFile) 
      cursor_map = dbMap.cursor()

      sql = "SELECT single_scene FROM 'Mappings'" +\
            'WHERE id = ' +\
             mappingId

      query = cursor_map.execute(sql)
      for i in query:
          single_scene = str(i[0])
      return single_scene
      dbMap.close()

##Function to delete the mapping entry from DB

  def deleteMapping(self):
      mapping_id = self.GetMapping()
      if mapping_id is None:
            return
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbUpdate = sqlite.connect(dbFile)     
      dbCursor = dbUpdate.cursor()

      updCols = r"""DELETE FROM 'Mappings' WHERE id = '"""
      updCols += str(mapping_id)
      updCols += """'"""

      dataupdColsExec = dbCursor.execute(updCols)
      dbUpdate.commit()
      dataupdColsExec.close()
      dbUpdate.close()

      row = self.ui.maptableWidget.currentItem().row()
      self.ui.maptableWidget.removeRow(row)


##Function to update the mapping status

  def updateMapping(self):
      mapping_id = self.GetMapping()
      if mapping_id is None:
            return
      if not self.ui.firetableWidget.currentItem():
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a fire.",
                                       QtGui.QMessageBox.Ok)
            return
      row = self.ui.firetableWidget.currentItem().row()
      colCount = self.ui.firetableWidget.columnCount()
      for i in xrange(colCount):
          colName = self.ui.firetableWidget.horizontalHeaderItem(i).text()
          if colName == 'id':
             col = i
      fire_id = self.ui.firetableWidget.item(row,col).text()
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbUpdate = sqlite.connect(dbFile)     
      dbCursor = dbUpdate.cursor()

      updCols = r"""UPDATE 'Fires' SET mapping_status = '"""
      updCols += str(self.ui.mappingBox.currentText())
      updCols += """' WHERE id = '"""
      updCols += str(fire_id)
      updCols += """'"""

      updMap = r"""UPDATE 'Mappings' SET status = '"""
      updMap += str(self.ui.mappingBox.currentText())
      updMap += """' WHERE id = '"""
      updMap += str(mapping_id)
      updMap += """'"""

      dataupdColsExec = dbCursor.execute(updCols)
      dataupdMapExec = dbCursor.execute(updMap)
      dbUpdate.commit()
      dataupdColsExec.close()
      dataupdMapExec.close()
      dbUpdate.close()

      self.dynamicUpdate()

  def dynamicUpdate(self):
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbFire = sqlite.connect(dbFile)     
      cursor_fire = dbFire.cursor()
      
      fire = r"""SELECT mapping_status FROM 'Fires'""" 
      fireParam = cursor_fire.execute(fire)
      if not self.ui.firetableWidget.currentItem():
            QtGui.QMessageBox.critical(self,
                                       "Error!",
                                       "You must select a fire.",
                                       QtGui.QMessageBox.Ok)
            return
      row = self.ui.firetableWidget.currentItem().row()

      for i in cursor_fire:
          #currentRowCount = self.ui.firetableWidget.rowCount()
          self.ui.firetableWidget.setItem(row,1,QtGui.QTableWidgetItem(str(i[0])))
      dbFire.close()

  '''
    Get a scene list to order files from ESPA(ESPA order must be done from
    the ESPA web interface)
    Args:
        N/A.
    Returns:
        N/A
  '''
  def GetESPASceneList(self):
        workspace = os.path.dirname(self.scene_src)
        sceneIDList = None
        params = FireParams(self.scene_src)
        params.exec_()
        if params.begDate != "" and params.endDate != "":
            sceneIDList =\
                self.GetSceneList(workspace,
                                  params.latitude,
                                  params.latitude,
                                  params.longitude,
                                  params.longitude,
                                  params.begDate,
                                  params.endDate)

        if sceneIDList is None:
            QtGui.QMessageBox.critical(None,
                                       u"Error",
                                       u"Bad scene list file",
                                       QtGui.QMessageBox.Ok)
            return
        return

  '''
     Produce a scene list.
     Args:
         minLat(float) - Minimum latitude.
         maxLat(float) - Maximum latitude.
         minLong(float) - Minimum longitude.
         maxLong(float) - Maximum longitude.
         begDate(string) - Begin date.(YYYY-MM-DD)
         endDate(string) - End date.(YYYY-MM-DD)
     Returns:
         sceneList(list) - Scene list.
  '''
  def GetSceneList(self, workspace, minLat, maxLat,
                   minLong, maxLong, begDate, endDate):
        iface.mainWindow().statusBar().showMessage("Getting scene list")
        sceneList = []
        url = ("http://earthexplorer.usgs.gov/EE/InventoryStream/"
               "latlong?sensor=LANDSAT_COMBINED_C1"
               "&north=" + str(maxLat) +
               "&south=" + str(minLat) +
               "&east=" + str(maxLong) +
               "&west=" + str(minLong) +
               "&start_date=" + begDate +
               "&end_date=" + endDate + "&cc=2")
        tempFile = urllib.urlretrieve(url)
        base = ("metadata" + begDate.replace("-", "") +
                "_" + endDate.replace("-", "") +
                ".xml")
        newMetaDataXML = os.path.join(workspace, base)
        if os.path.exists(newMetaDataXML):
            os.remove(newMetaDataXML)
        os.rename(list(tempFile)[0], newMetaDataXML)
        # parse the XML file (newMetaDataXML)
        tree = ElementTree.parse(newMetaDataXML)
        root = tree.getroot()
        ns = {"src": "http://upe.ldcm.usgs.gov/schema/metadata"}
        for child in root.findall("src:metaData", ns):
            for child2 in child:
                if "LANDSAT_PRODUCT_ID" in child2.tag:
                    sceneList.append(child2.text)
        # write sceneList out to a file
        self.WriteSceneList(sceneList, workspace)
        return sceneList

  '''
    Function to save the scene list to text file.
    Args:
        N/A
    Returns:
        N/A
  '''
  def WriteSceneList(self, sceneList, workspace):
        try:
            fname =\
                QtGui.QFileDialog.getSaveFileName(None,
                                                  u"Select path and name for "
                                                  "the saved scene list file",
                                                  workspace,
                                                  "*.txt")
            if fname:
                with open(fname, "wb") as outFile:
                    for entry in sceneList:
                        outFile.write(entry + "\r\n")
            iface.mainWindow().statusBar().showMessage("Scene List complete")
        except:
            raise(IOError, "Scene List file write failed.")

  '''
    Process ESPA Downloads to NBR, REFL and UTM
    Args:
        N/A.
    Returns:
        N/A
  '''
  def ProcessESPAData(self):
        self.DisableContols()
        reprojectFlag = False
        msg = u"Do you want the output files in Albers projection?"
        reply = QtGui.QMessageBox.question(self, u"Albers projection?",
                                           msg,
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            reprojectFlag = True

        workspace = os.path.dirname(self.scene_src)
        prc = ProcessESPADownload(workspace, reprojectFlag)

        targzPath = os.path.join(workspace, "targz")
        fileList = glob.glob(targzPath + os.sep + "*.tar.gz")

        if fileList:
            for entry in fileList:
                prc.ProcessFile(entry)
        else:
            QtGui.QMessageBox.information(None,
                                          u"No files found to process {}".format(self.scene_src),
                                          u"No files found to process {}".format(self.scene_src),
                                          QtGui.QMessageBox.Ok)
        for gz_file in fileList:
            try:
                os.remove(gz_file)
            except:
                pass
        self.EnableContols()
        QtGui.QMessageBox.information(None,
                                      u"Process ESPA files complete",
                                      u"Processing ESPA files completed",
                                      QtGui.QMessageBox.Ok)
        iface.mainWindow().statusBar().showMessage(
            u"Processing ESPA files completed")
        return

  # To re-enable controls after a process is complete
  def EnableContols(self):
        self.ui.createMapButton.setEnabled(True)
        self.ui.sceneprepButton.setEnabled(True)
        self.ui.fireprepButton.setEnabled(True)
        self.ui.delineateButton.setEnabled(True)
        self.ui.subsetButton.setEnabled(True)
        self.ui.openeventButton.setEnabled(True)
        self.ui.checkBox.setEnabled(True)
        self.ui.deleteButton.setEnabled(True)
        self.ui.updatemappingButton.setEnabled(True)
        self.ui.qacheckButton.setEnabled(True)
        self.ui.clearButton.setEnabled(True)
        self.ui.ndviButton.setEnabled(True)
        self.ui.metaButton.setEnabled(True)
        self.ui.getSceneListButton.setEnabled(True)
        self.ui.processDataButton.setEnabled(True)
        self.ui.groupBox.setEnabled(True)
        self.ui.groupBox_3.setEnabled(True)
        self.ui.groupBox_4.setEnabled(True)
        self.ui.groupBox_5.setEnabled(True)
        self.ui.analysisBox.setEnabled(True)
        self.ui.perimeterBox.setEnabled(True)

  # To disable controls while processing
  def DisableContols(self):
        self.ui.createMapButton.setEnabled(False)
        self.ui.sceneprepButton.setEnabled(False)
        self.ui.fireprepButton.setEnabled(False)
        self.ui.delineateButton.setEnabled(False)
        self.ui.subsetButton.setEnabled(False)
        self.ui.openeventButton.setEnabled(False)
        self.ui.checkBox.setEnabled(False)
        self.ui.deleteButton.setEnabled(False)
        self.ui.updatemappingButton.setEnabled(False)
        self.ui.qacheckButton.setEnabled(False)
        self.ui.clearButton.setEnabled(False)
        self.ui.ndviButton.setEnabled(False)
        self.ui.metaButton.setEnabled(False)
        self.ui.getSceneListButton.setEnabled(False)
        self.ui.processDataButton.setEnabled(False)
        self.ui.groupBox.setEnabled(False)
        self.ui.groupBox_3.setEnabled(False)
        self.ui.groupBox_4.setEnabled(False)
        self.ui.groupBox_5.setEnabled(False)
        self.ui.analysisBox.setEnabled(False)
        self.ui.perimeterBox.setEnabled(False)


class AddFireDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_AddFire()
        self.ui.setupUi(self)
        self.ui.igDateEdit.setCalendarPopup(True)

        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
                  'Colorado', 'Connecticut', 'Delaware',
                  'District of Columbia', 'Florida',
                  'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
                  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
                  'Massachussets', 'Michigan', 'Minnesota', 'Mississippi',
                  'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
                  'New Jersey', 'New Mexico', 'North Carolina', 'North Dakota',
                  'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico',
                  'Rhode Island', 'South Carolina', 'South Dakota',
                  'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
                  'Washington', 'West Virginia', 'Wisconsin', 'Wyoming',
                  'International']
        for i in states:
            self.ui.stateBox.addItem(i)

        self.ui.acreSpinBox.setValue(999999)

        eventType = ['WF', 'RX', 'WFU', 'UNK', 'Other']
        for j in eventType:
            self.ui.eventBox.addItem(j)

        self.ui.eventIDButton.clicked.connect(self.LoadFireInfo)

    def LoadFireInfo(self):
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbInsert = sqlite.connect(dbFile)
        dbCursor = dbInsert.cursor()

        maxQ = r"""SELECT MAX(id) AS id FROM 'Fires'"""
        maxQ = dbCursor.execute(maxQ)
        maxFetch = dbCursor.fetchone()
        if maxFetch[0] is None:
            fireId = 1
        else:
            maxValue = map(lambda x: x+1, maxFetch)
            fireId = maxValue[0]

        states = {
            'Alabama': 'AL',
            'Alaska': 'AK',
            'Arizona': 'AZ',
            'Arkansas': 'AR',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'Delaware': 'DE',
            'District Of Columbia': 'DC',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Hawaii': 'HI',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Iowa': 'IA',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Maine': 'ME',
            'Maryland': 'MD',
            'Massachusetts': 'MA',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Mississippi': 'MS',
            'Missouri': 'MO',
            'Montana': 'MT',
            'Nebraska': 'NE',
            'Nevada': 'NV',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'New York': 'NY',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Vermont': 'VT',
            'Virginia': 'VA',
            'Washington': 'WA',
            'West Virginia': 'WV',
            'Wisconsin': 'WI',
            'Wyoming': 'WY',
            'International': "IT"}
        boxValue = self.ui.stateBox.currentText()
        state = states.get(boxValue)
        latdecimal = self.ui.latSpinBox.value()
        longdecimal = self.ui.longSpinBox.value()

        dateformat =\
            datetime.datetime.strptime(str(self.ui.igDateEdit.text()),
                                       '%m/%d/%Y').strftime('%Y-%m-%d')
        sDate = dateformat.replace("-", "")
        # it is possible that we have both positive and negative lat annd long
        # but assume a single user will not have both, so we remove any "-"
        # for the event id
        sLat = format(latdecimal, '.3f')
        sLong = format(longdecimal, '.3f')

        eventID = (state +
                   sLat.replace('.', '').replace('-', '').zfill(5) +
                   sLong.replace('.', '').replace('-', '').zfill(6) +
                   sDate)

        params = (str(fireId),
                  eventID,
                  self.ui.nameEdit.text(),
                  self.ui.eventBox.currentText(),
                  dateformat,
                  sLat,
                  sLong,
                  str(self.ui.acreSpinBox.value()),
                  self.ui.expectedDateEdit.text(),
                  self.ui.actualDateEdit.text(),
                  self.ui.stateBox.currentText(),
                  self.ui.adminEdit.text(),
                  self.ui.agencyEdit.text(),
                  self.ui.reportDateEdit.text(),
                  self.ui.commentEdit.text(),
                  self.ui.fuelsEdit.text(),
                  str(self.ui.pathSpinBox.value()),
                  str(self.ui.rowSpinBox.value()), 'in-progress', 'NULL',)

        updCols = (r"""INSERT INTO 'Fires' (id,event_id,incident_name,""" +
                   """incident_type,ig_date,ig_lat,ig_long,area_burned,""" +
                   """expected_containment_date,actual_containment_date,""" +
                   """ig_state,ig_admin,ig_agency,report_date,comment,""" +
                   """fuels,path1,row1,mapping_status,mapping_in_progress)""" +
                   """VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""")

        dbCursor.execute(updCols, params)
        dbInsert.commit()
        dbCursor.close()
        dbInsert.close()


class SearchByNameDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_SearchByName()
        self.ui.setupUi(self)
        self.ui.searchButton.clicked.connect(self.searchbyEventName)

    def searchbyEventName(self):
        self.selectedName = self.ui.incidentLineEdit.text()
        QtGui.QDialog.accept(self)

class SearchByDateDialog(QtGui.QDialog):
  def __init__(self): 
      QtGui.QDialog.__init__(self)   
      self.ui = Ui_SearchByDate()
      self.ui.setupUi(self)
      self.ui.startdateEdit.setCalendarPopup(True)
      self.ui.startdateEdit.setDate(QtCore.QDate.currentDate())
      self.ui.enddateEdit.setCalendarPopup(True)
      self.ui.enddateEdit.setDate(QtCore.QDate.currentDate())
      dateLabels = ['ig_date','report_date','expected_containment_date','actual_containment_date']
      for param in dateLabels:
        self.ui.dateFieldComboBox.addItem(param)
      self.ui.searchButton.clicked.connect(self.searchbyEventDate)      

  def searchbyEventDate(self):
      if self.ui.dateFieldComboBox.currentText() == 'ig_date':
        self.selectedCriteria = 'ig_date'
      elif self.ui.dateFieldComboBox.currentText() == 'report_date':
        self.selectedCriteria = 'report_date'
      elif self.ui.dateFieldComboBox.currentText() == 'expected_containment_date':
        self.selectedCriteria = 'expected_containment_date'
      elif self.ui.dateFieldComboBox.currentText() == 'actual_containment_date':
        self.selectedCriteria = 'actual_containment_date'      
      self.selectedStartDate = self.ui.startdateEdit.date().toPyDate()
      self.selectedEndDate = self.ui.enddateEdit.date().toPyDate()
      QDialog.accept(self)
       
class SearchByPathRowYearDialog(QtGui.QDialog):
  def __init__(self): 
      QtGui.QDialog.__init__(self)     
      self.ui = Ui_SearchByPathRowYear()
      self.ui.setupUi(self)
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbYear = sqlite.connect(dbFile) 
      cursor_year = dbYear.cursor()
      year = r"""SELECT DISTINCT strftime('%Y',ig_date) FROM 'Fires'"""
      yearQ = cursor_year.execute(year)
      yearFetch = cursor_year.fetchall()
      yearList = []
      for years in yearFetch:
          yearList.append(years[0])
      yearList = sorted(set(yearList), key = None, reverse = True)
      for entries in yearList:
        self.ui.yearComboBox.addItem(str(entries))
      self.ui.searchButton.clicked.connect(self.searchbyEventPathRowYear)

  def searchbyEventPathRowYear(self):
      self.selectedYear = self.ui.yearComboBox.currentText()
      self.selectedPath = self.ui.pathLineEdit.text()
      self.selectedRow = self.ui.rowLineEdit.text() 
      QDialog.accept(self)
 
class SearchByYearDialog(QtGui.QDialog):
  def __init__(self): 
      QtGui.QDialog.__init__(self)     
      self.ui = Ui_SearchByYear()
      self.ui.setupUi(self)
      dbDir = os.path.dirname(os.path.realpath(__file__))
      dbName = 'FireInfo.sqlite'
      dbFile = os.path.join(dbDir, dbName)
      dbYear = sqlite.connect(dbFile) 
      cursor_year = dbYear.cursor()
      year = r"""SELECT DISTINCT strftime('%Y',ig_date) AS ig_date FROM 'Fires'"""
      yearQ = cursor_year.execute(year)
      yearFetch = cursor_year.fetchall()
      yearList = []     
      for years in yearFetch:
          yearList.append(years[0])
      yearList = sorted(set(yearList), key = None, reverse = True)
      for entries in yearList:
        self.ui.yearComboBox.addItem(str(entries))
      self.ui.searchButton.clicked.connect(self.searchbyEventYear)

  def searchbyEventYear(self):
      self.selectedYear = self.ui.yearComboBox.currentText()      
      QDialog.accept(self)

class SelectIntervalDialog(QtGui.QDialog):
  def __init__(self, img_src, ndvi_pr):
      QtGui.QDialog.__init__(self)
      self.ui = Ui_SelectInterval()
      self.ui.setupUi(self)
      ImageType = [' ', 'Collections Data']
      for image in ImageType:
          self.ui.imageBox.addItem(image)
      self.ui.imageBox.activated.connect(self.SelectImages)
      self.img_src = img_src
      self.ndvi_pathrow = ndvi_pr

  def SelectImages(self):      
      if self.ui.imageBox.currentText() == 'Collections Data':
        thedir = os.path.join(self.img_src, self.ndvi_pathrow)
        listDir = [i for i in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, i))]
        yearList = []
        for folders in listDir:
            yearList.append(str(folders)[7:11])

        yearList = list(sorted(set(yearList)))    
        for years in yearList:
            self.ui.preFireBox.addItem(str(years))
            self.ui.postFireBox.addItem(str(years))

      elif self.ui.imageBox.currentText() == 'Add ESPA Images':
        self.ui.preFireBox.clear()
        self.ui.postFireBox.clear()
      self.ui.okButton.clicked.connect(self.LoadImages)
      
  def LoadImages(self):
      self.imageType = self.ui.imageBox.currentText()
      self.preYear = self.ui.preFireBox.currentText()
      self.postYear = self.ui.postFireBox.currentText()
      QDialog.accept(self)
      
class CreateMappingDialog(QtGui.QDialog):
  def __init__(self): 
        QtGui.QDialog.__init__(self)     
        self.ui = Ui_CreateMapping()
        self.ui.setupUi(self)

        self.ui.assessmentComboBox.activated.connect(self.assessmentSelect)
        self.populatePrefireData()
        self.populatePostfireData()
        self.populatePerifireData()
        self.ui.saveButton.clicked.connect(self.saveMapping)
        assessment = [' ', 'Initial', 'Initial (SS)',
                      'Extended', 'Extended (SS)']
        for j in assessment:
            self.ui.assessmentComboBox.addItem(j)

  def assessmentSelect(self):   
      if str(self.ui.assessmentComboBox.currentText()) == 'Initial' or \
         str(self.ui.assessmentComboBox.currentText()) == 'Extended':
         self.ui.labelImage.setText('Pre Image')
         self.ui.labelSensor.setText('Pre Sensor Used')
         self.ui.labelDate.setText('Prefire Date')
         self.single_scene = 0
      elif str(self.ui.assessmentComboBox.currentText()) == 'Initial (SS)' or \
           str(self.ui.assessmentComboBox.currentText()) == 'Extended (SS)':
         self.ui.labelImage.setText('Supplementary Image')
         self.ui.labelSensor.setText('Supplementary Sensor Used')
         self.ui.labelDate.setText('Supplementary Date')
         self.single_scene = 1

  def populatePrefireData(self):
      layers = QgsMapLayerRegistry.instance().mapLayers()
      self.ui.preImageComboBox.addItem(' ')
      prefireList = []
      for name, layer in layers.iteritems():
        if layer.name().startswith('LC'):
          prefireList.append(layer.name()[2:21])
        else:
          prefireList.append(layer.name()[0:19])
      #prefireList.sort(cmp=lambda i,j:cmp(int(i[7:]), int(j[7:])))
      for x in prefireList:
        self.ui.preImageComboBox.addItem(x)
      self.ui.preImageComboBox.activated.connect(self.prefire)

  def prefire(self):      
      fileName = self.ui.preImageComboBox.currentText()
      year = int(os.path.basename(fileName)[7:11])
      month = int(os.path.basename(fileName)[11:13])
      day = int(os.path.basename(fileName)[13:15])
      date = datetime.datetime(year, month, day)
##      jd   = int(os.path.basename(fileName)[-3:]) - 1
##      date = datetime.datetime(year,1,1) + datetime.timedelta(jd)
      self.ui.preDatelineEdit.setText(date.strftime('%Y-%m-%d'))     
      if fileName.startswith('5'):
        self.ui.preSensorlineEdit.setText('l5')
      elif fileName.startswith('7'):
        self.ui.preSensorlineEdit.setText('l7')
      elif fileName.startswith('8'):
        self.ui.preSensorlineEdit.setText('l8')
              
  def populatePostfireData(self):
      layers = QgsMapLayerRegistry.instance().mapLayers()
      self.ui.postImageComboBox.addItem(' ')
      postfireList = []
      for name, layer in layers.iteritems():
        if layer.name().startswith('LC'):
          postfireList.append(layer.name()[2:21])
        else:
          postfireList.append(layer.name()[0:19])
      #postfireList.sort(cmp=lambda i,j:cmp(int(i[7:]), int(j[7:])))
      for x in postfireList:
        self.ui.postImageComboBox.addItem(x)
      self.ui.postImageComboBox.activated.connect(self.postfire)

  def postfire(self):
      fileName = self.ui.postImageComboBox.currentText()
      year = int(os.path.basename(fileName)[7:11])
      month = int(os.path.basename(fileName)[11:13])
      day = int(os.path.basename(fileName)[13:15])
      date = datetime.datetime(year, month, day)
      self.ui.postDatelineEdit.setText(date.strftime('%Y-%m-%d'))
      if fileName.startswith('5'):
        self.ui.postSensorlineEdit.setText('l5')
      elif fileName.startswith('7'):
        self.ui.postSensorlineEdit.setText('l7')
      elif fileName.startswith('8'):
        self.ui.postSensorlineEdit.setText('l8')
                
  def populatePerifireData(self):
      layers = QgsMapLayerRegistry.instance().mapLayers()
      self.ui.periImageComboBox.addItem(' ')
      perifireList = []
      for name, layer in layers.iteritems():
        if layer.name().startswith('LC'):
          perifireList.append(layer.name()[2:21])
        else:
          perifireList.append(layer.name()[0:19])
      #perifireList.sort(cmp=lambda i,j:cmp(int(i[7:]), int(j[7:])))
      for x in perifireList:
        self.ui.periImageComboBox.addItem(x)
      self.ui.periImageComboBox.activated.connect(self.perifire)

  def perifire(self):
      fileName = self.ui.periImageComboBox.currentText()
      year = int(os.path.basename(fileName)[7:11])
      month = int(os.path.basename(fileName)[11:13])
      day = int(os.path.basename(fileName)[13:15])
      date = datetime.datetime(year, month, day)
      self.ui.periDatelineEdit.setText(date.strftime('%Y-%m-%d'))
      if fileName.startswith('5'):
        self.ui.periSensorlineEdit.setText('l5')
      elif fileName.startswith('7'):
        self.ui.periSensorlineEdit.setText('l7')
      elif fileName.startswith('8'):
        self.ui.periSensorlineEdit.setText('l8')
               
  def saveMapping(self):
      self.assessStrategy = self.ui.assessmentComboBox.currentText()
      if not self.ui.preImageComboBox.currentText() == ' ':
        self.presuppImage = self.ui.preImageComboBox.currentText()
      else:
        self.presuppImage = None
      if self.presuppImage:
          self.prePath = self.presuppImage[2:4]
          self.preRow = self.presuppImage[5:7]
      else:
          self.prePath = None
          self.preRow = None
      if not self.ui.postImageComboBox.currentText() == ' ':
        self.postImage = self.ui.postImageComboBox.currentText()
      else:
        self.postImage = None
      if self.postImage:
          self.postPath = self.postImage[2:4]
          self.postRow = self.postImage[5:7]
      else:
          self.postPath = None
          self.postRow = None
      if not self.ui.periImageComboBox.currentText() == ' ':
        self.periImage = self.ui.periImageComboBox.currentText()
      else:
        self.periImage = None
      if self.periImage:
          self.periPath = self.periImage[2:4]
          self.periRow = self.periImage[5:7]
##      else:
##          self.periPath = None
##          self.periRow = None
      self.presuppSensor = self.ui.preSensorlineEdit.text()
      self.postSensor = self.ui.postSensorlineEdit.text()
      self.periSensor = self.ui.periSensorlineEdit.text()
      if self.ui.preDatelineEdit.text():
        self.prefireDate = self.ui.preDatelineEdit.text()        
      else:
        self.prefireDate = None
      if self.ui.postDatelineEdit.text():
        self.postfireDate = self.ui.postDatelineEdit.text()
      else:
        self.postfireDate = None
      if self.ui.periDatelineEdit.text():
        self.periDate = self.ui.periDatelineEdit.text()
      else:
        self.periDate = None
      self.status = 'in-progress'
      QDialog.accept(self)
