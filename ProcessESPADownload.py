'''
/***************************************************************************
Name		     : FMT plugin
Description          : Process ESPA Downloads
                     : Based on MTBS Glovis processing by Kelcy Smith
                     : Computes TOA and NBR rasters for use in the FMT mapping.
copyright            : (C) 2016-17 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Dec 09, 2016
Revised              : Apr 27, 2017
                       Oct 30, 2017 - Add checks for path row lengths, used
                       subprocess to circumvent problem with processing module
                       Nov 08, 2017 - Revert Oct 30 changes
                       Dec 14, 2017 - Fix L7 gap values fix
                       Jan 2, 2017 - Path Row values to 3 digits
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''
import gc
import glob
import math
import numpy as np
import os
from osgeo import gdal
from osgeo import osr
import processing
import shutil
import subprocess
import tarfile

from qgis.utils import iface
from qgis.core import QgsMessageLog, QgsRasterLayer, QgsMapLayerRegistry
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from PyQt4.QtCore import QFileInfo
from PyQt4 import QtGui


class ProcessESPADownload(object):

    def __init__(self, workspace, reprojectFlag):
        self.workspace = workspace
        self.copyPath = os.path.join(self.workspace, "img_src", "landsat")
        self.driver = gdal.GetDriverByName("GTiff")
        self.sceneID = ""
        self.sensor = ""
        self.minShort = -32768
        self.reprojectFlag = reprojectFlag
        self.bandName = ""
        self.workPath = ""
        self.path = ""
        self.row = ""
        self.bandA = ""
        self.bandB = ""
        self.sceneIDPath = ""
        self.outFileUTM = ""
        self.outFileREFL = ""
        self.outFileNBR = ""
        self.toaFileList = []
        self.albersFlag = False

    '''
    Process the file to create utm, refl and nbr outputs.
    Args:
        N/A
    Returns:
        N/A
    '''
    def ProcessFile(self, inputFile):
        self.workPath = os.path.join(self.workspace, "working")
        if os.path.exists(self.workPath):
            shutil.rmtree(self.workPath)
        os.makedirs(self.workPath)
        gzName = os.path.basename(inputFile)
        self.sceneID = gzName[:-24]
        QgsMessageLog.logMessage("Begin processing for : " + self.sceneID,
                                 level=QgsMessageLog.INFO)
        self.sensor = self.sceneID[3]
        self.path = int(self.sceneID[4:7])
        self.row = int(self.sceneID[7:10])

        if self.sensor == "8":
            self.bandA = "5"
            self.bandB = "7"
        else:
            self.bandA = "4"
            self.bandB = "7"

        tempPath = str(self.path).zfill(3)
        tempRow = str(self.row).zfill(3)
        # create output location if needed
        prPath =\
            os.path.join(self.copyPath,
                         tempPath + tempRow)
        self.sceneIDPath =\
            os.path.join(prPath, self.sceneID[3:])
        if not os.path.exists(self.sceneIDPath):
            os.makedirs(self.sceneIDPath)
        else:
            reply = QtGui.QMessageBox.question(None, u"Overwrite?",
                                               (self.sceneID[3:] +
                                                " output folder already "
                                                "exists."
                                                "\nOverwrite?"),
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
            else:
                shutil.rmtree(self.sceneIDPath)
                os.mkdir(self.sceneIDPath)
        self.outFileUTM = os.path.join(self.sceneIDPath,
                                       self.sceneID[3:] + "_UTM.TIF")
        self.outFileREFL = os.path.join(self.sceneIDPath,
                                        self.sceneID[3:] + "_REFL.TIF")
        self.outFileNBR = os.path.join(self.sceneIDPath,
                                       self.sceneID[3:] + "_NBR.TIF")

        # unzip and gather info from new files
        self.UnzipFile(inputFile)
        self.toaFileList = glob.glob(self.workPath + os.sep +
                                     "*_toa_band*.tif")
        if not self.toaFileList:
            QgsMessageLog.logMessage("Error:  No toa files unzipped",
                                     level=QgsMessageLog.CRITICAL)
            return

        # determine if the inputs are already in Albers
        ds = gdal.Open(self.toaFileList[0])
        projection = ds.GetProjection()
        reprojectedFilesList = []
        # if inputs are Albers, reproject back to Albers, fixes "unnamed" name
        if "Albers" in str(projection):
            self.albersFlag = True
            self.reprojectFlag = True
        if self.reprojectFlag:
            self.ReprojectInputs()
            for entry in self.toaFileList:
                reprName = entry.replace(".tif", "repr.tif")
                reprojectedFilesList.append(reprName)
        self.bandName = os.path.basename(self.toaFileList[0])[:49]

        # calculate NBR from 16 bit images (either UTM or Conus)
        if self.reprojectFlag:
            inFileA = os.path.join(self.workPath,
                                   (self.bandName + self.bandA + "repr.tif"))
            inFileB = os.path.join(self.workPath,
                                   (self.bandName + self.bandB + "repr.tif"))
        else:
            inFileA = os.path.join(self.workPath,
                                   (self.bandName + self.bandA + ".tif"))
            inFileB = os.path.join(self.workPath,
                                   (self.bandName + self.bandB + ".tif"))

        calcResult = self.ProcessNBR(inFileA, inFileB)
        if calcResult == 0:
            QgsMessageLog.logMessage(
                "Info: NBR calculation succeeded:  " + str(calcResult),
                level=QgsMessageLog.INFO)
        else:
            QgsMessageLog.logMessage(
                "Error: NBR calculation failed:  " + str(calcResult),
                level=QgsMessageLog.CRITICAL)

        # stack byte files and write to REFL and UTM files
        if self.albersFlag:
            self.WriteMultiBandFiles(reprojectedFilesList, self.outFileREFL)
        elif self.reprojectFlag:
            self.WriteMultiBandFiles(self.toaFileList, self.outFileUTM)
            self.WriteMultiBandFiles(reprojectedFilesList, self.outFileREFL)
        else:
            self.WriteMultiBandFiles(self.toaFileList, self.outFileUTM)
            shutil.copy(self.outFileUTM, self.outFileREFL)

        # cleanup
        reprojectedFilesList = None
        self.toaFileList = None
        del reprojectedFilesList
        gc.collect()

        # remove temp NBR file
        fileList = glob.glob(self.sceneIDPath + os.sep + "*temp*")
        os.remove(fileList[0])
        QgsMessageLog.logMessage("Processing for : " + self.sceneID +
                                 " completed.",
                                 level=QgsMessageLog.INFO)

    '''
    Unzip the downloaded files, place extracted file in working directory.
    The scene ID and sensor are assigned here.
    Args:
        N/A
    Returns:
        N/A
    '''
    def UnzipFile(self, tgzFile):
        msg = u"Extracting " + tgzFile + "..."
        iface.mainWindow().statusBar().showMessage(msg)

        # Extract tarball into the working directory
        tar = tarfile.open(tgzFile)
        tar.extractall(self.workPath)
        tar.close()
        QgsMessageLog.logMessage("File extraction completed for: " + tgzFile,
                                 level=QgsMessageLog.INFO)
        return

    '''
    Stack a set of files and write to a Byte output
    Args:
        N/A
    Returns:
        N/A
    '''
    def WriteMultiBandFiles(self, fileList, outFile):
        msg = u"WriteMultiBandFiles for " + self.sceneID + "..."
        iface.mainWindow().statusBar().showMessage(msg)
        # give ownership of layers to map registry so unlock happens
        for entry in fileList:
            fileInfo1 = QFileInfo(entry)
            baseName1 = fileInfo1.baseName()
            layer1 = QgsRasterLayer(entry, baseName1)
            QgsMapLayerRegistry.instance().addMapLayer(layer1)

        # Build VRT for TOA processing
        vrtPath = os.path.join(self.workPath, self.sceneID + ".vrt")
        processing.runalg("gdalogr:buildvirtualraster",
                          {"INPUT": fileList,
                           "RESOLUTION": 0,
                           "SEPARATE": True,
                           "OUTPUT": vrtPath})

        # write out virtual raster
        ds = gdal.Open(vrtPath)
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        geo = ds.GetGeoTransform()
        projection = ds.GetProjection()

        if self.sensor == "8":
            toa_ds =\
                self.driver.Create(outFile,
                                   cols, rows, 8, gdal.GDT_Byte,
                                   ["TILED=YES",
                                    "BLOCKXSIZE=64",
                                    "BLOCKYSIZE=64"])
        else:
            toa_ds =\
                self.driver.Create(outFile,
                                   cols, rows, 6, gdal.GDT_Byte,
                                   ["TILED=YES",
                                    "BLOCKXSIZE=64",
                                    "BLOCKYSIZE=64"])

        toa_ds.SetGeoTransform(geo)
        toa_ds.SetProjection(projection)
        # Process each band, one at a time
        for num in range(8):
            num += 1

            if self.sensor != "8" and num > 6:
                continue

            band = ds.GetRasterBand(num)
            toa_band = toa_ds.GetRasterBand(num)

            b_arr = np.array(band.ReadAsArray(0, 0, cols, rows),
                             dtype=np.int16)
            b_arr[b_arr < 0] = 0
            b_arr = b_arr / 25
            toa_band.WriteArray(b_arr.astype(np.uint8))
            del toa_band

        del b_arr
        ds = None
        toa_ds = None
        vrtPath = None
        del ds
        del toa_ds
        del vrtPath
        QgsMapLayerRegistry.instance().removeAllMapLayers()

        msg = u"WriteMultiBandFiles for " + self.sceneID + " Completed"
        iface.mainWindow().statusBar().showMessage(msg)
        return

    '''
    Reproject the .tif files in the working directory to Albers.
    Args:
        N/A
    Returns:
        N/A
    '''
    def ReprojectInputs(self):
        proj4_str = ""
        QgsMessageLog.logMessage("Reprojecting input files",
                                 level=QgsMessageLog.INFO)
        if (self.path > 9 and self.path < 49 and
                self.row > 24 and self.row < 44):  # CONUS
            proj4_str =\
                ("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 "
                 "+lon_0=-96 +datum=NAD83 +units=m +no_defs")
        elif (self.path > 49 and self.path < 85 and
                self.row > 7 and self.row < 23):  # Alaska
            proj4_str = ("+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 "
                         "+lon_0=-154 +x_0=0 +y_0=0 +ellps=GRS80 "
                         "+datum=NAD83 +units=m +no_defs")
        elif (self.path > 61 and self.path < 67 and
              self.row > 43 and self.row < 48):  # Hawaii
            proj4_str = ("+proj=aea +lat_1=8 +lat_2=18 +lat_0=3 "
                         "+lon_0=-157 "
                         "+x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 "
                         "+units=m +no_defs")
        elif ((self.path == 4 or self.path == 5) and
                (self.row == 47 or self.row == 48)):  # Puerto Rico
            proj4_str = ("+proj=aea +lat_1=8 +lat_2=18 +lat_0=3 "
                         "+lon_0=-66 "
                         "+x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 "
                         "+units=m +no_defs")
        else:
            QtGui.QMessageBox.information(
                None,
                u"Albers reprojection not valid!",
                (u"The scene cannot be reprojected to an an Albers projection,"
                 " it is outside the path/row of CONUS, Alaska, Hawaii or "
                 "Puerto Rico. Projection will remain as UTM.  "
                 "Scene path/row:  " + str(self.path).zfill(3) + " / " +
                 str(self.row).zfill(3)),
                QtGui.QMessageBox.Ok)
        if proj4_str:
            gdal_str = "-t_srs \"%s\"" % proj4_str
            box_ls = self.GetCoords(self.toaFileList[0], proj4_str)

        for entry in self.toaFileList:
            outFile = entry.replace(".tif", "repr.tif")
            if proj4_str:
                subprocess.call(
                    'gdalwarp -r cubic -tr 30 30 -te %s %s %s %s %s %s %s' % (
                        box_ls[0], box_ls[1], box_ls[2],
                        box_ls[3], gdal_str, entry, outFile),
                    shell=True)
            else:
                shutil.copy(entry, outFile)

    '''
    Process the NBR band files
    Args:
        N/A
    Returns:
        N/A
    '''
    def ProcessNBR(self, inFileA, inFileB):
        msg = u"NBR Processing for " + self.sceneID + "..."
        iface.mainWindow().statusBar().showMessage(msg)
        QgsMessageLog.logMessage(msg, level=QgsMessageLog.INFO)
        try:
            calculatorEntryList = []
            tempOutFile = self.outFileNBR.replace("NBR", "NBR_temp")

            fileInfo1 = QFileInfo(inFileA)
            baseName1 = fileInfo1.baseName()
            newLayer1 = QgsRasterLayer(inFileA, baseName1)
            boh1 = QgsRasterCalculatorEntry()
            boh1.ref = "boh@1"
            boh1.bandNumber = 1
            calculatorEntryList.append(boh1)
            boh1.raster = newLayer1

            if newLayer1.isValid():
                extents = newLayer1.extent()
                colCt = newLayer1.width()
                rowCt = newLayer1.height()
            else:
                raise IOError(u"Error, Invalid layer read!")

            fileInfo2 = QFileInfo(inFileB)
            baseName2 = fileInfo2.baseName()
            newLayer2 = QgsRasterLayer(inFileB, baseName2)
            boh2 = QgsRasterCalculatorEntry()
            boh2.ref = "boh@2"
            boh2.bandNumber = 1
            calculatorEntryList.append(boh2)
            boh2.raster = newLayer2
            if not newLayer2.isValid():
                raise IOError(u"Error, Invalid layer read!")

            formula = ("(((boh@1 != 0 AND boh@2 != 0) * "
                       "(boh@1 - boh@2) / (boh@1 + boh@2) * 1000) + "
                       "((boh@1 = 0 OR boh@2 = 0) * " +
                       str(self.minShort) + "))")

            # Process calculation with input extent and resolution
            calc = QgsRasterCalculator(formula,
                                       tempOutFile,
                                       'GTiff',
                                       extents,
                                       colCt,
                                       rowCt,
                                       calculatorEntryList)

            result = calc.processCalculation()

            if result != 0:
                raise RuntimeError(u"Raster calculator failed.")

            # convert Raster Calculator result to int 16
            self.Float2IntTif(tempOutFile, self.outFileNBR)
        except:
            raise RuntimeError(u"Unspecified error when calculating NBR")
        finally:
            # cleanup
            calculatorEntryList = None
            fileInfo1 = None
            baseName1 = None
            fileInfo2 = None
            baseName2 = None
            formula = None
            boh1 = None
            boh2 = None
            calc = None
            newLayer1 = None
            newLayer2 = None

            del calculatorEntryList
            del fileInfo1
            del baseName1
            del fileInfo2
            del baseName2
            del formula
            del boh1
            del boh2
            del calc
            del newLayer1
            del newLayer2
        gc.collect()

        msg = u"NBR Processing for " + self.sceneID + " Completed"
        iface.mainWindow().statusBar().showMessage(msg)
        QgsMessageLog.logMessage(msg, level=QgsMessageLog.INFO)
        iface.mainWindow().statusBar().showMessage("")
        return result

    '''
     Get offset of fifteen.  Used to align coordinates to a specific grid
     Args:
         coord(float) - Input value.
     Returns:
         val(float) - Output value.
    '''
    # Used to align coordinates to a specific grid
    def FifteenOffset(self, coord):
        return math.floor(coord / 30.0) * 30.0 + 15

    '''
     Get coordinates. This will transform, and determine the
     coordinates to snap the raster to.
     Args:
         tifFile(string) - Tif filename.
         proj(string) - Projection.
     Returns:
         coordLs(list) - [xMin, yMin, xMax, yMax]
    '''
    def GetCoords(self, tifFile, proj):
        coordLs = []

        tDs = gdal.Open(tifFile)
        tBand = tDs.GetRasterBand(1)
        tRows = tBand.YSize
        tCols = tBand.XSize
        tProj = tDs.GetProjectionRef()
        tGeoXform = tDs.GetGeoTransform()

        albersProj = osr.SpatialReference()
        albersProj.ImportFromProj4(proj)

        fromProj = osr.SpatialReference()
        fromProj.ImportFromWkt(tProj)

        coordTrans = osr.CoordinateTransformation(fromProj, albersProj)

        ll = coordTrans.TransformPoint(tGeoXform[0],
                                       (tGeoXform[3] + tGeoXform[5] * tRows))
        ul = coordTrans.TransformPoint(tGeoXform[0], tGeoXform[3])
        ur = coordTrans.TransformPoint((tGeoXform[0] + tGeoXform[1] * tCols),
                                       tGeoXform[3])
        lr = coordTrans.TransformPoint((tGeoXform[0] + tGeoXform[1] * tCols),
                                       (tGeoXform[3] + tGeoXform[5] * tRows))

        xMin = min(ll[0], ul[0])
        yMin = min(ll[1], lr[1])
        xMax = max(lr[0], ur[0])
        yMax = max(ul[1], ur[1])

        # Determine the extents to keep consistent (xmin ymin xmax ymax)
        coordLs.append(str(self.FifteenOffset(xMin)))
        coordLs.append(str(self.FifteenOffset(yMin)))
        coordLs.append(str(self.FifteenOffset(xMax)))
        coordLs.append(str(self.FifteenOffset(yMax)))

        tBand = None
        tDs = None
        return coordLs

    '''
    Change tif to int16 format.
    Args:
        inFile(string) - Input file name.
        outFile(string) - Output file name.
    Returns:
        N/A.
    '''
    def Float2IntTif(self, inFile, outFile):
        cmd = ("gdal_translate " +
               inFile + " " +
               outFile + " -ot Int16 -of GTiff -a_nodata none")
        subprocess.call(cmd, shell=True)
        return
