"""
/***************************************************************************
Name		     : Threshold
Description          : Threshold functions for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Oct 19, 2017
Updated              : Nov 08, 2017 - Typecast incoming thresholds, os.system
                           to subprocess to avoid popup consoles
                       Jan 2, 2018 - Path Row values to 3 digits
                       Jan 4, 2018 - Recode values for -9999 to 6
                       Jan 17, 2018 - Corrected population of shapefiles
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

    Threshold for Open Source MTBS

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""

import os
from osgeo import gdal
from osgeo import ogr
from osgeo.gdalconst import GA_ReadOnly
import numpy as np
from pyspatialite import dbapi2 as sqlite
from PyQt4 import QtGui
import subprocess


class ThresholdProcess():
    def __init__(self, mappingId, parentPath, low, mod, high, regrowth):
        self.mappingId = mappingId
        self.low = int(low)
        self.mod = int(mod)
        self.high = int(high)
        self.regrowth = regrowth  # this remains a string until recode

        self.imgSrcPath = os.path.join(parentPath, 'img_src', 'landsat')
        self.evtProdsPath = os.path.join(parentPath, 'event_prods', 'fire')

    '''
    Run a sql query
    Args:
        sql(string) - Input query
    Returns:
        fetch(list) - Query result
    '''
    def RunQuery(self, sql):
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbMap = sqlite.connect(dbFile)
        cursor_map = dbMap.cursor()
        query = cursor_map.execute(sql)
        fetch = cursor_map.fetchone()
        return fetch

    '''
    Get params from image id
    Args:
        img(string) - Input image
    Returns:
        imageYear(integer) - Image year
        imageMonth(integer) - Image month
        imageDay(integer) - Image day
        imagePr(integer) - Image path row
    '''
    def ExtractImageParams(self, imgId):
        imageYear = None
        imageMonth = None
        imageDay = None
        imagePr = None
        if imgId:
            imageYear = imgId[7:11]
            imageMonth = imgId[11:13]
            imageDay = imgId[13:15]
            imagePr = imgId[2:4] + imgId[5:7]
        return imageYear, imageMonth, imageDay, imagePr

    # Return Array
    def FileToArray(self, fName):
        fileArr = None
        srcDs = gdal.Open(fName, GA_ReadOnly)

        dataType = srcDs.GetRasterBand(1).DataType
        dataType = gdal.GetDataTypeName(dataType)

        if dataType == 'UInt16':
            InType = np.uint16
        elif dataType == 'Int16':
            InType = np.int16
        elif dataType == 'UInt8':
            InType = np.uint8
        elif dataType == 'Byte':
            InType = np.uint8
        elif dataType == 'UInt32':
            InType = np.uint32
        else:
            QtGui.QMessageBox.critical(None,
                                       "Incorrect data type",
                                       "Incorrect data type",
                                       QtGui.QMessageBox.Ok)
            return

        fileArr = srcDs.GetRasterBand(1).ReadAsArray().astype(InType)
        srcDs = None
        del srcDs

        return fileArr

    # Recoding schema for dNBR
    def RecodeDNBR(self, val):
        # No data recode
        if val <= -9999:
            retVal = 6
        # Veg Regrowth Recode
        elif val > -9999 and val <= int(self.regrowth):
            retVal = 5
        # Unburned recode
        elif val > int(self.regrowth) and val < self.low:
            retVal = 1
        # Low recode
        elif val >= self.low and val < self.mod:
            retVal = 2
        # Mod recode
        elif val >= self.mod and val < self.high:
            retVal = 3
        elif val >= self.high and val < 9999:
            retVal = 4
        else:
            retVal = 0

        return retVal

    # Recoding schema for NBR
    def RecodeNBR(self, val):
        # No data recode
        if val <= -9999:
            retVal = 6
        # Unburned recode
        elif val > self.low:
            retVal = 1
        # Low recode
        elif val <= self.low and val > self.mod:
            retVal = 2
        # Mod recode
        elif val <= self.mod and val > self.high:
            retVal = 3
        elif val <= self.high and val > -9999:
            retVal = 4
        else:
            retVal = 0

        return retVal

    def CalcThresholds(self):
        table1 = 'Fires'
        table2 = 'Mappings'

        sql = "SELECT * FROM " + table2 + ' WHERE Id = ' + self.mappingId
        fetch = self.RunQuery(sql)

        fireId = str(fetch[1])
        preFireId = str(fetch[6])
        postFireId = str(fetch[10])
        fireComment = str(fetch[14])
        confidence = str(fetch[24])

        sql = "SELECT * FROM " + table1 + ' WHERE Id = ' + str(fireId)
        fetch = self.RunQuery(sql)

        mtbsId = str(fetch[1])
        mtbsIdLower = mtbsId.lower()

        if fireComment == '':
            fireComment = 'None'

        fireDate = fetch[4]
        strFireDate = str(fireDate).split('-')
        fireYear = strFireDate[0]

        # Make Folder
        mappingDir = os.path.join(self.evtProdsPath,
                                  fireYear,
                                  mtbsIdLower,
                                  'mtbs_' + self.mappingId)

        if not os.path.exists(mappingDir):
            os.makedirs(mappingDir)

        preYear, preMonth, preDay, prePr = self.ExtractImageParams(preFireId)
        postYear, postMonth, postDay, postPr =\
            self.ExtractImageParams(postFireId)
        preDate = preYear + preMonth + preDay
        postDate = postYear + postMonth + postDay

        # Clip Post Nbr
        postNbrClip = os.path.join(mappingDir,
                                   (mtbsIdLower + '_' + postDate + '_nbr.tif'))

        # Clip dNBR location
        dNbrClip = os.path.join(mappingDir,
                                (mtbsIdLower + '_' + preDate + '_' +
                                 postDate + '_dnbr.tif'))

        # Mask Clip Locations
        dnbrMaskClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' + preDate + '_' +
                                     postDate + '_gapmask.tif'))

        postMaskClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' +
                                     postDate + '_gapmask.tif'))

        # Create Fire Shapefile
        if os.path.exists(dNbrClip):
            burnShp = (mtbsIdLower + '_' + preDate + '_' +
                       postDate + '_burn_bndy.shp')
        else:
            burnShp = (mtbsIdLower + '_' + postDate + '_burn_bndy.shp')

        burnBndy = os.path.join(mappingDir, burnShp)

        # Add data to Shapefile
        # Open Burn Bndy using OGR
        driver = ogr.GetDriverByName("ESRI Shapefile")
        srcDs = driver.Open(burnBndy, 1)
        lyr = srcDs.GetLayer()

        count = -1
        for feature in lyr:
            count = count + 1
            feature.SetField('Confidence', confidence)
            feature.SetField('Comment', fireComment)
            lyr.SetFeature(feature)

            feature = None
            del feature

        srcDs.Destroy()

        lyr = None
        del lyr

        # Mask Shapefile
        mask_shp = burnShp.replace('_burn_bndy.shp', '_mask.shp')
        maskBndy = os.path.join(mappingDir, mask_shp)

        maskTif = maskBndy.replace('.shp', '.tif')
        inputImage = None
        # Start Main Process
        if os.path.exists(dNbrClip):
            inputImage = dNbrClip
            outputImage = inputImage.replace('_dnbr.tif', '_dnbr6.tif')
            outputTemp = outputImage.replace('.tif', '_temp.tif')
        else:
            if os.path.exists(postNbrClip):
                inputImage = postNbrClip
                outputImage = inputImage.replace('_nbr.tif', '_nbr6.tif')
                outputTemp = outputImage.replace('.tif', '_temp.tif')

        if not inputImage:
            QtGui.QMessageBox.critical(None,
                                       "Missing file",
                                       "Input image is missing",
                                       QtGui.QMessageBox.Ok)
            return
        # Open file
        Thresh = gdal.Open(inputImage)
        threshBand = Thresh.GetRasterBand(1)
        threshGXfrm = Thresh.GetGeoTransform()
        threshCols = threshBand.XSize
        threshRows = threshBand.YSize
        # Determine whether 8 or 16 bit data
        threshBitType = gdal.GetDataTypeName(threshBand.DataType)
        threshProj = Thresh.GetProjection()

        # Check the input image bit type
        if threshBitType == 'Int8':
            bitType = np.int8
        elif threshBitType == 'Int16':
            bitType = np.int16
        elif threshBitType == 'Int32':
            bitType = np.int32
        else:
            QtGui.QMessageBox.critical(None,
                                       "Incorrect data type",
                                       "Incorrect data type" + threshBitType,
                                       QtGui.QMessageBox.Ok)
            return

        # Bring in data as an array
        threshArr = np.array(threshBand.ReadAsArray(0, 0,
                                                    threshCols,
                                                    threshRows), dtype=bitType)
        #  (rows, cols) = threshArr.shape
        # Flatten array and change to list
        threshArrFlat = threshArr.flatten()
        threshArrList = threshArrFlat.tolist()
        # Recode the list
        if inputImage.endswith('_dnbr.tif'):
            recodeThreshList = map(self.RecodeDNBR, threshArrList)
        else:
            recodeThreshList = map(self.RecodeNBR, threshArrList)
        # Array to list specifying the bit type (e.g. 16 bits).
        recodeThreshArr = np.array(recodeThreshList,
                                   dtype=bitType).reshape(threshRows,
                                                          threshCols)

        # Open Mask as array
        maskArr = self.FileToArray(maskTif)

        # Open Gap Mask
        if os.path.exists(dnbrMaskClip):
            gapArr = self.FileToArray(dnbrMaskClip)
            recodeThreshArr[(maskArr == 1) | (gapArr == 0)] = 6
        else:
            if os.path.exists(postMaskClip):
                gapArr = self.FileToArray(postMaskClip)
                recodeThreshArr[(maskArr == 1) | (gapArr == 0)] = 6
            else:
                # Convert Masked values equal to 1 to 6 (mask MTBS value)
                recodeThreshArr[maskArr == 1] = 6
        maskArr = None
        gapArr = None

        # Setup the recode
        # Delete image if it already exists
        if os.path.exists(outputTemp):
            os.remove(outputTemp)

        # Create output image and write data
        driver = gdal.GetDriverByName("GTiff")
        outDs = driver.Create(outputTemp,
                              threshCols,
                              threshRows,
                              1, gdal.GDT_Byte)
        outDs.SetGeoTransform(threshGXfrm)
        outDs.SetProjection(threshProj)
        outBand = outDs.GetRasterBand(1)
        outBand.WriteArray(recodeThreshArr)

        del outBand
        del recodeThreshArr
        del Thresh
        del threshBand
        del outDs

        # Create temp vrt
        outVrt = outputTemp.replace('.tif', '.vrt')
        # Delete image if it already exists
        if os.path.exists(outVrt):
            os.remove(outVrt)
        command1 = ("gdal_translate -q -of VRT " + outputTemp + " " + outVrt)
        subprocess.call(command1, shell=True)

        # Add Color Table
        outputVrt2 = outVrt.replace('.vrt', '2.vrt')
        # Delete image if it already exists
        if os.path.exists(outputVrt2):
            os.remove(outputVrt2)

        oVrt = open(outVrt, 'r')
        rVrt = oVrt.readlines()
        oVrt.close()

        oVrt2 = open(outputVrt2, 'w')

        rText = ('<ColorInterp>Palette</ColorInterp>\n' +
                 '       <ColorTable>\n' +
                 '           <Entry c1="0" c2="0" c3="0" c4="255"/>\n' +
                 '           <Entry c1="0" c2="100" c3="0" c4="255"/>\n' +
                 '           <Entry c1="127" c2="255" c3="212" c4="255"/>\n' +
                 '           <Entry c1="255" c2="255" c3="0" c4="255"/>\n' +
                 '           <Entry c1="255" c2="0" c3="0" c4="255"/>\n' +
                 '           <Entry c1="127" c2="255" c3="0" c4="255"/>\n' +
                 '           <Entry c1="255" c2="255" c3="255" c4="255"/>\n' +
                 '       </ColorTable>')

        for line in rVrt:
            if "<ColorInterp>Gray</ColorInterp>" not in line:
                oVrt2.write(line)
            else:
                oVrt2.write(line.replace('<ColorInterp>Gray</ColorInterp>',
                                         rText))

        oVrt2.close()

        # run gdal_translate to create new image with color map
        if os.path.exists(outVrt):
            os.remove(outVrt)

        if os.path.exists(outputImage):
            os.remove(outputImage)

        command2 = ("gdal_translate -q -ot Byte " + outputVrt2 + " " +
                    outputImage)
        subprocess.call(command2, shell=True)

        # Delete Vrt Files
        if os.path.exists(outputVrt2):
            os.remove(outputVrt2)

        if os.path.exists(outputTemp):
            os.remove(outputTemp)

        # Clip Image to Shapefile
        command3 = ('gdalwarp -q -cutline ' + burnBndy + " " + outputImage +
                    " " + outputTemp)
        subprocess.call(command3, shell=True)

        if os.path.exists(outputTemp):
            if os.path.exists(outputImage):
                os.remove(outputImage)
            os.rename(outputTemp, outputImage)
