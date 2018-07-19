"""
/***************************************************************************
Name		     : ScenePrep
Description          : Scene Prep functions for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Oct 5, 2017
Updated              : Oct 25, 2017 Comments and corrected booleans with ""
                       Oct 30 os.system to subprocess so console windows
                       don't show
                       Jan 2, 2018 - Path Row values to 3 digits
                       Jan 4, 2018 - Fix DNBRMask
                       Jan 17, 2018 - Add nodata vals to DNBR
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This code is based off of work done by:

    Kelcy Smith
    Contractor to USGS/EROS
    kelcy.smith.ctr@usgs.gov

    dNBR processing for Open Source MTBS

    Computes dNBR values (pre - post) for two given NBR rasters
    Generally only works with projected units (meters) (not really tested)

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""

import os

from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from osgeo import osr
import numpy as np

from pyspatialite import dbapi2 as sqlite
from PyQt4 import QtGui
import scipy.ndimage as nd
import subprocess


class ScenePrep():
    def __init__(self, mappingId, sceneDir, overWrite):
        self.mapId = mappingId
        self.path = sceneDir
        self.overWrite = overWrite
        self.driver = gdal.GetDriverByName("GTiff")
        self.outRows = 0
        self.outCols = 0
        self.preXOffset = 0
        self.preYOffset = 0
        self.postXOffset = 0
        self.postYOffset = 0

    '''
    Read the file information
    Args:
        fName(string) - Input image
    Returns:
        ndv(integer) - No data value
        xsize(integer) - Column count
        ysize(integer) - Row count
        gXForm(list) - GeoTransform
        proj(string) - Projection
        dataType(string) - Data type
    '''
    def GetGeoInfo(self, fName):
        srcDs = gdal.Open(fName, GA_ReadOnly)
        ndv = srcDs.GetRasterBand(1).GetNoDataValue()
        xsize = srcDs.RasterXSize
        ysize = srcDs.RasterYSize
        gXForm = srcDs.GetGeoTransform()
        proj = osr.SpatialReference()
        dataType = srcDs.GetRasterBand(1).DataType
        dataType = gdal.GetDataTypeName(dataType)
        srcDs = None
        del srcDs
        return ndv, xsize, ysize, gXForm, proj, dataType

    '''
    Read the file to an array
    Args:
        fName(string) - Input image
        dataType(string) - Data type
        cols(integer) - Column count
        rows(integer) - Row count
        colOffset(integer) - Column offset
        rowOffset(integer) - Row offset
        band(integer) - Band number
    Returns:
        dArray(array) - Data array
    '''
    def FileToArray(self, fName, dataType, cols, rows, cOffset, rOffset, band):
        srcDs = gdal.Open(fName, GA_ReadOnly)
        dArray = None
        if dataType == 'UInt16':
            inType = np.uint16
        elif dataType == 'Int16':
            inType = np.int16
        elif dataType == 'UInt8':
            inType = np.uint8
        elif dataType == 'Byte':
            inType = np.uint8
        elif dataType == 'UInt32':
            inType = np.uint32
        else:
            inType = None
        if inType:
            dArray = srcDs.GetRasterBand(band).ReadAsArray(
                cOffset, rOffset, cols, rows).astype(inType)
        srcDs = None
        del srcDs
        return dArray

    '''
    Creates 6 band TOA mask
    Args:
        reflPath(string) - Input image
        maskPath(string) - Mask image
    Returns:
        N/A
    '''
    def TOAMask(self, reflPath, maskPath):
        ds = gdal.Open(reflPath)
        rows = ds.RasterYSize
        cols = ds.RasterXSize
        geo = ds.GetGeoTransform()
        projection = ds.GetProjection()
        postGapDs = self.driver.Create(maskPath, cols, rows, 6,
                                       gdal.GDT_Byte)
        postGapDs.SetProjection(projection)
        postGapDs.SetGeoTransform(geo)
        postGapDs.SetProjection(projection)

        # Process each band, one at a time
        for num in range(6):
            num += 1

            band = ds.GetRasterBand(num)
            maskBand = postGapDs.GetRasterBand(num)

            bArr = np.array(band.ReadAsArray(0, 0, cols, rows),
                            dtype=np.float32)
            maskArr = np.zeros((rows, cols), dtype=np.bool)

            maskArr[bArr > 0] = 1

            maskBand.WriteArray(maskArr)
            del maskBand
            del maskArr
        postGapDs = None
        del postGapDs

    '''
    Buffers Toa Mask by 2 pixels
    Args:
        mkPath(string) - Mask image
    Returns:
        N/A
    '''
    def BufferMask(self, mkPath):
        mkDs = gdal.Open(mkPath, gdal.GA_Update)
        r = mkDs.RasterYSize
        c = mkDs.RasterXSize

        struct = nd.generate_binary_structure(2, 2)
        for x in range(1, mkDs.RasterCount + 1):
            band = mkDs.GetRasterBand(x)
            mArr = np.array(band.ReadAsArray(0, 0, c, r), dtype=np.int)
            buffArr = np.logical_not(
                nd.binary_dilation(np.logical_not(mArr.astype(np.bool)),
                                   structure=struct,
                                   iterations=2).astype(np.int))

            band.WriteArray(buffArr)
            band = None
            buffArr = None

        mkDs = None
        del mkDs

    '''
    Creates NBR mask from TOA bands 5 and 4 mask
    Args:
        inMask(string) - Input Mask image
        outMask(string) - Output Mask image
    Returns:
        -1 for error
         0 for success
    '''
    def NBRMask(self, inMask, outMask):
        NDV, c, r, geo, projection, DataType = self.GetGeoInfo(inMask)
        getDs = gdal.Open(inMask, gdal.GA_Update)

        projection = getDs.GetProjection()

        getDs = None
        del getDs

        b5Ar = self.FileToArray(inMask, DataType, c, r, 0, 0, 5)
        b4Ar = self.FileToArray(inMask, DataType, c, r, 0, 0, 4)
        if (b4Ar is None or b5Ar is None):
            QtGui.QMessageBox.critical(None,
                                       "Error!!",
                                       ("The mask cannot be created, "
                                        "file read failed."),
                                       QtGui.QMessageBox.Ok)
            return -1  # Error code
        outArr = b5Ar * b4Ar

        b5Ar = None
        b4Ar = None

        mkDs = self.driver.Create(outMask, c, r, 1, gdal.GDT_Byte)
        mkDs.SetGeoTransform(geo)
        mkDs.SetProjection(projection)

        mkDsBand = mkDs.GetRasterBand(1)
        mkDsBand.WriteArray(outArr)

        outArr = None
        mkDs = None
        mkDsBand = None
        return 0  # Success

    '''
    Creates dNBR mask
    Args:
        preMask(string) - Pre Mask image
        postMask(string) - Post Mask image
        cols(integer) - Column count
        rows(integer) - Row count
        geo(list) - GeoTransform
        proj(string) - Projection
    Returns:
        N/A
    '''
    def DNBRMask(self, preMask, postMask, maskOut, cols, rows, geo, proj):
        outArr = None
        preArr = None
        postArr = None

        if os.path.exists(preMask):
            preDs = gdal.Open(preMask)
            preBand = preDs.GetRasterBand(1)
            preArr = np.array(preBand.ReadAsArray(self.preXOffset,
                                                  self.preYOffset,
                                                  self.outCols,
                                                  self.outRows))
        if os.path.exists(postMask):
            postDs = gdal.Open(postMask)
            postBand = postDs.GetRasterBand(1)
            postArr = np.array(postBand.ReadAsArray(self.postXOffset,
                                                    self.postYOffset,
                                                    self.outCols,
                                                    self.outRows))
        if preArr is not None and postArr is not None:
            outArr = preArr + postArr
            outArr[(preArr > 0) | (postArr > 0)] = 1
        elif preArr is not None:
            outArr = preArr
            outArr[preArr > 0] = 1
        elif postArr is not None:
            outArr = postArr
            outArr[postArr > 0] = 1

        if outArr is not None:
            mkDs = self.driver.Create(maskOut, cols, rows, 1, gdal.GDT_Byte)
            mkDs.SetGeoTransform(geo)
            mkDs.SetProjection(proj)
            mkDsBand = mkDs.GetRasterBand(1)
            mkDsBand.WriteArray(outArr)

    '''
    Processes Scene Prep
    Args:
        N/A
    Returns:
        N/A
    '''
    def ProcessScenePrep(self):
        # TODO: The database reads/writes should be in their own class
        # TODO: There are several repeated funcitons that should be
        #       in a util class
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbMap = sqlite.connect(dbFile)

        cursor_map = dbMap.cursor()

        sql = ("SELECT * FROM 'Mappings' WHERE id = " + self.mapId)

        query = cursor_map.execute(sql)
        fetch = cursor_map.fetchone()
        prefireId = str(fetch[6])
        postfireId = str(fetch[10])
        if not prefireId == 'None':
            preYear = prefireId[7:11]
            preMonth = prefireId[11:13]
            preDay = prefireId[13:15]
        else:
            pass

        if not postfireId == 'None':
            postYear = postfireId[7:11]
            postMonth = postfireId[11:13]
            postDay = postfireId[13:15]
        else:
            pass

        prePathRow = prefireId[1:4] + prefireId[4:7]
        postPathRow = postfireId[1:4] + postfireId[4:7]

        outputPath = self.path.replace("img_src", "img_proc")
        preNBR = prefireId + '_NBR.TIF'
        postNBR = postfireId + '_NBR.TIF'

        prePath = os.path.join(self.path, prePathRow, prefireId, preNBR)
        postPath = os.path.join(self.path, postPathRow, postfireId, postNBR)
        if not os.path.exists(prePath):
            QtGui.QMessageBox.critical(None,
                                       "Error!!",
                                       ("Prefire  scene does not exist.\n"
                                        "Exiting..."),
                                       QtGui.QMessageBox.Ok)
            return
        if not os.path.exists(postPath):
            QtGui.QMessageBox.critical(None,
                                       "Error!!",
                                       ("Postfire  scene does not exist.\n"
                                        "Exiting..."),
                                       QtGui.QMessageBox.Ok)
            return

        preReflPath = prePath.replace('_NBR.TIF', '_REFL.TIF')
        postReflPath = postPath.replace('_NBR.TIF', '_REFL.TIF')

        # Gap mask if Landsat 7
        preGapMaskPath = prePath.replace('_NBR.TIF', '_GM.tif')
        preGapMaskPathTemp =\
            preGapMaskPath.replace('_GM.tif', '_gapmask.tif')
        postGapMaskPath = postPath.replace('_NBR.TIF', '_GM.tif')
        postGapMaskPathTemp =\
            postGapMaskPath.replace('_GM.tif', '_gapmask.tif')

        tempString =\
            (prePathRow + '_' + preYear + preMonth + preDay +
             '_' + postPathRow + '_' + postYear + postMonth + postDay)

        dNBROutDir = os.path.join(outputPath, tempString)
        if not os.path.exists(dNBROutDir):
            os.makedirs(dNBROutDir)

        dNBROutPath = os.path.join(dNBROutDir, ('d' + tempString + '.tif'))
        dNBRMaskPath = os.path.join(dNBROutDir, ('m' + tempString + '.tif'))
        maskTemp = dNBRMaskPath.replace('.tif', '_temp.tif')

        if os.path.exists(dNBRMaskPath) and self.overWrite is True:
            os.remove(dNBRMaskPath)

        if os.path.exists(dNBROutPath) and self.overWrite is False:
            QtGui.QMessageBox.warning(None,
                                      "Warning!",
                                      ("DNBR image already exists.\n"
                                       "'Run Scene Prep' exiting."),
                                      QtGui.QMessageBox.Ok)
            return

        overlap = False

        # Get the bounding box coordinates for the two NBR's
        preCoords = []
        preDs = gdal.Open(prePath)
        preBand = preDs.GetRasterBand(1)
        preRows = preBand.YSize
        preCols = preBand.XSize
        preGeo = preDs.GetGeoTransform()
        preProj = preDs.GetProjection()

        preCoords.append(preGeo[0])
        preCoords.append(preGeo[3] + preGeo[5] * preRows)
        preCoords.append(preGeo[0] + preGeo[1] * preCols)
        preCoords.append(preGeo[3])

        postCoords = []
        postDs = gdal.Open(postPath)
        postBand = postDs.GetRasterBand(1)
        postRows = postBand.YSize
        postCols = postBand.XSize
        postGeo = postDs.GetGeoTransform()
        postProj = postDs.GetProjection()

        postCoords.append(postGeo[0])
        postCoords.append(postGeo[3] + postGeo[5] * postRows)
        postCoords.append(postGeo[0] + postGeo[1] * postCols)
        postCoords.append(postGeo[3])

        # Verify same projection
        if preProj != postProj:
            QtGui.QMessageBox.critical(None,
                                       "Error!",
                                       ("Files are not in the same "
                                        "projection.\n"
                                        "Scene Prep exiting."),
                                       QtGui.QMessageBox.Ok)
            return
        # Determine the total extent of where they overlap
        if postCoords[0] <= preCoords[0] <= postCoords[2]:
            xMin = preCoords[0]
            if postCoords[0] <= preCoords[2] <= postCoords[2]:
                xMax = preCoords[2]
            else:
                xMax = postCoords[2]

            if postCoords[1] <= preCoords[1] <= postCoords[3]:
                yMin = preCoords[1]
                if postCoords[1] <= preCoords[3] <= postCoords[3]:
                    yMax = preCoords[3]
                else:
                    yMax = postCoords[3]
                overlap = True

            elif preCoords[1] <= postCoords[1] <= preCoords[3]:
                yMin = postCoords[1]
                if preCoords[1] <= postCoords[3] <= preCoords[3]:
                    yMax = postCoords[3]
                else:
                    yMax = preCoords[3]
                overlap = True

        elif preCoords[0] <= postCoords[0] <= preCoords[2]:
            xMin = postCoords[0]
            if preCoords[0] <= postCoords[2] <= preCoords[2]:
                xMax = postCoords[2]
            else:
                xMax = preCoords[2]

            if postCoords[1] <= preCoords[1] <= postCoords[3]:
                yMin = preCoords[1]
                if postCoords[1] <= preCoords[3] <= postCoords[3]:
                    yMax = preCoords[3]
                else:
                    yMax = postCoords[3]
                overlap = True

            elif preCoords[1] <= postCoords[1] <= preCoords[3]:
                yMin = postCoords[1]
                if preCoords[1] <= postCoords[3] <= preCoords[3]:
                    yMax = postCoords[3]
                else:
                    yMax = preCoords[3]
                overlap = True
        if not overlap:
            QtGui.QMessageBox.critical(None,
                                       "Error!",
                                       ("Scenes do not intersect.\n"
                                        "Scene Prep exiting."),
                                       QtGui.QMessageBox.Ok)
            return

        # Calculate output rows and columns
        self.outRows = int(abs(yMax - yMin) / 30)
        self.outCols = int(abs(xMax - xMin) / 30)

        # Calculate offset values needed for pre and post raster
        self.preXOffset = int(abs((preCoords[0] - xMin) / 30))
        self.preYOffset = int(abs((preCoords[3] - yMax) / 30))
        self.postXOffset = int(abs((postCoords[0] - xMin) / 30))
        self.postYOffset = int(abs((postCoords[3] - yMax) / 30))

        # Get new geo and proj
        dNBRGeo = (xMin, 30, 0, yMax, 0, -30)
        dNBRProj = preProj

        #  Create Gap Mask
        if os.path.exists(preReflPath):
            if preNBR.startswith('7'):
                if os.path.exists(preGapMaskPath):
                    os.remove(preGapMaskPath)
                    self.TOAMask(preReflPath, preGapMaskPath)
                    self.BufferMask(preGapMaskPath)
                    rv = self.NBRMask(preGapMaskPath,
                                      preGapMaskPathTemp)
                else:
                    self.TOAMask(preReflPath, preGapMaskPath)
                    self.BufferMask(preGapMaskPath)
                    rv = self.NBRMask(preGapMaskPath,
                                      preGapMaskPathTemp)
                if rv != 0:
                    return
        if os.path.exists(postReflPath):
            if postNBR.startswith('7'):
                if os.path.exists(postGapMaskPath):
                    os.remove(postGapMaskPath)
                    self.TOAMask(postReflPath, postGapMaskPath)
                    self.BufferMask(postGapMaskPath)
                    rv = self.NBRMask(postGapMaskPath,
                                      postGapMaskPathTemp)
                else:
                    self.TOAMask(postReflPath, postGapMaskPath)
                    self.BufferMask(postGapMaskPath)
                    rv = self.NBRMask(postGapMaskPath,
                                      postGapMaskPathTemp)
                if rv != 0:
                    return
        # Open pre and post arrays
        preArr = np.array(preBand.ReadAsArray(self.preXOffset,
                                              self.preYOffset,
                                              self.outCols,
                                              self.outRows))
        postArr = np.array(postBand.ReadAsArray(self.postXOffset,
                                                self.postYOffset,
                                                self.outCols,
                                                self.outRows))
        # Create dNBR mask
        if not os.path.exists(maskTemp):
            self.DNBRMask(preGapMaskPathTemp, postGapMaskPathTemp,
                          maskTemp, self.outCols, self.outRows,
                          dNBRGeo, dNBRProj)
        elif os.path.exists(maskTemp) and self.overWrite is True:
            self.DNBRMask(preGapMaskPathTemp, postGapMaskPathTemp,
                          maskTemp, self.outCols, self.outRows,
                          dNBRGeo, dNBRProj)

        # Convert masks to 1 bit images
        if os.path.exists(maskTemp):
            command = ("gdal_translate -co NBITS=1 " +
                       maskTemp + ' ' + dNBRMaskPath)

            # TODO - at time of release both os.system and subprocess.call
            # for gdal_translate cause a crash dump message when QGIS closes.
            # Leave as subprocess.call until QGIS bug is resolved. 
            subprocess.call(command, shell=True)
            os.remove(maskTemp)
        if os.path.exists(preGapMaskPath):
            os.remove(preGapMaskPath)
            if os.path.exists(preGapMaskPathTemp):
                command = ("gdal_translate -co NBITS=1 " +
                           preGapMaskPathTemp + ' ' +
                           preGapMaskPath)
                # os.system(command)
                subprocess.call(command, shell=True)
                os.remove(preGapMaskPathTemp)
        if os.path.exists(postGapMaskPath):
            os.remove(postGapMaskPath)
            if os.path.exists(postGapMaskPathTemp):
                command = ("gdal_translate -co NBITS=1 " +
                           postGapMaskPathTemp + ' ' +
                           postGapMaskPath)
                # os.system(command)
                subprocess.call(command, shell=True)
                os.remove(postGapMaskPathTemp)
        # Open the dNBR mask
        if os.path.exists(dNBRMaskPath):
            dNBRMaskDs = gdal.Open(dNBRMaskPath)
            dNBRMaskBand = dNBRMaskDs.GetRasterBand(1)
            dNBRMaskArr =\
                np.array(dNBRMaskBand.ReadAsArray(), dtype=np.byte)
            dNBRMaskDs = None
            dNBRMaskBand = None

        # Compute the dNBR and output the finished product
        dNBRArr = preArr - postArr
        if os.path.exists(dNBRMaskPath):
            dNBRArr[dNBRMaskArr == 0] = -32768
            dNBRArr[dNBRArr >= 20000] = -32768
            dNBRArr[(preArr == -32768) | (postArr == -32768)] = -32768
            dNBRMaskArr = None
        else:
            dNBRArr[(preArr == -32768) | (postArr == -32768)] = -32768

        dNBRDs = self.driver.Create(dNBROutPath, self.outCols,
                                    self.outRows, 1, gdal.GDT_Int16)
        dNBRDs.SetGeoTransform(dNBRGeo)
        dNBRDs.SetProjection(dNBRProj)
        dNBRBand = dNBRDs.GetRasterBand(1)
        dNBRBand.WriteArray(dNBRArr)
        dNBRBand.FlushCache()
        dNBRDs = None
