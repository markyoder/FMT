"""
/***************************************************************************
Name		     : Subset
Description          : Clip and subset functions for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Oct 17, 2017
Updated              : Oct 23, 2017 - Added check for successful clip, changed
                           clip output to Int16, dNbrImage check to dNbrOutPath
                    Oct 30, 2017 os.system to subprocess.call
                    Jan 2, 2018 - Path Row values to 3 digits
                    Jan 17, 2018 - Corrected population of shapefiles
                    Mar 8, 2018 - JPicotte tweaked threshold process

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

    Clip and subset for Open Source MTBS

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""
import math
import numpy as np
import os
from osgeo import ogr
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from PyQt4 import QtGui
from pyspatialite import dbapi2 as sqlite
from qgis.core import QgsRasterLayer
import subprocess


class Subset():
    def __init__(self, mappingId, parentPath, singleScene):
        self.parentPath = parentPath
        self.mappingId = mappingId
        self.singleScene = singleScene
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.imgSrcPath =\
            os.path.join(self.parentPath, 'img_src', 'landsat')
        self.imgProcPath =\
            os.path.join(self.parentPath, 'img_proc', 'landsat')
        self.evtProdsPath =\
            os.path.join(self.parentPath, 'event_prods', 'fire')
        self.shpXmin = 0.0
        self.shpYmin = 0.0
        self.shpXmax = 0.0
        self.shpYmax = 0.0

    '''
    Get the sensor type from image name
    Args:
        imgName(string) - Image name
    Returns:
        sensor(string) - Sensor
    '''
    def GetSensor(self, imgName):
        if imgName.startswith('7'):
            sensor = 'l7'
        elif imgName.startswith('5'):
            sensor = 'l5'
        elif imgName.startswith('8'):
            sensor = 'l8'
        else:
            sensor = 'None'
        return sensor

    '''
    Calculate the correct corners for gdal
    Args:
        oord(integer) - Input val
    Returns:
        newVal(integer) - Output val
    '''
    def OddEven(self, oord):
        num15s = oord // 15
        dec, intpart15 = math.modf(num15s)

        if (oord > 0 and intpart15 % 2 == 0):
            newVal = 15 * (num15s + 1)
        elif (oord < 0 and intpart15 % 2 == 0):
            newVal = 15 * (num15s + 1)
        else:
            newVal = 15 * num15s
        return newVal

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
    Extract info from image id
    Args:
        img(string) - Input image
    Returns:
        imageYear(string) - Image year
        imageMonth(string) - Image month
        imageDay(string) - Image day
        imagePr(string) - Image path row
    '''
    def LoadImage(self, imgId):
        imageYear = None
        imageMonth = None
        imageDay = None
        imagePr = None
        if imgId:
            imageYear = imgId[7:11]
            imageMonth = imgId[11:13]
            imageDay = imgId[13:15]
            imagePr = imgId[1:4] + imgId[4:7]
        return imageYear, imageMonth, imageDay, imagePr

    '''
    Calculate rDNBR offset
    Args:
        img(string) - Input image
        perimImage(string) - Perimeter input image
        maskImage(string) - Mask Input image
        dLow(integer) - Low value break
        dHigh(integer) - High value break
    Returns:
        offDnbr(integer) - rDnbr offset
        offStd(integer) - Std dev of rDnbr offset
    '''
    def RnbrOff(self, img, perimImage, maskImage, dLow, dHigh):

        readIn = gdal.Open(img, GA_ReadOnly)
        bandIn = readIn.GetRasterBand(1)

        perimIn = gdal.Open(perimImage, GA_ReadOnly)
        pBand = perimIn.GetRasterBand(1)

        maskIn = gdal.Open(maskImage, GA_ReadOnly)
        mBand = maskIn.GetRasterBand(1)

        dataInArr = np.array(bandIn.ReadAsArray(), dtype=np.float64)
        perimArr = np.array(pBand.ReadAsArray(), dtype=np.byte)
        maskArr = np.array(mBand.ReadAsArray(), dtype=np.byte)

        dataInArr[(dataInArr <= dLow) |
                  (dataInArr >= dHigh) |
                  (perimArr == 1) |
                  (maskArr == 1)] = np.nan

        offDnbr = int(round(np.nanmedian(dataInArr)))
        offStd = int(round(np.nanstd(dataInArr)))
        maskArr = None
        del maskArr
        maskIn = None
        del maskIn
        mBand = None
        del mBand
        perimArr = None
        perimIn = None
        pBand = None
        del perimArr
        del perimIn
        del pBand
        dataInArr = None
        del dataInArr
        readIn = None
        del readIn
        bandIn = None
        del bandIn

        return offDnbr, offStd

    '''
    Histogram using Otsu Threshold method
    Args:
        image(string) - Input image
        nbins(integer) - Bin count
    Returns:
        hist(array) - Histogram
        binCenters(array) - Bin centers
    '''
    def Histogram(self, image, nbins=256):
        # For integer types, histogramming with bincount is more efficient.
        if np.issubdtype(image.dtype, np.integer):
            offset = 0
            imgMin = np.min(image)
            if imgMin < 0:
                offset = imgMin
                imgRange = np.max(image).astype(np.int64) - imgMin
                # get smallest dtype that can hold both min and offset max
                offsetDType = np.promote_types(np.min_scalar_type(imgRange),
                                               np.min_scalar_type(imgMin))
                if image.dtype != offsetDType:
                    # prevent overflow errors when offsetting
                    image = image.astype(offsetDType)
                image = image - offset
            hist = np.bincount(image.ravel())
            binCenters = np.arange(len(hist)) + offset

            # clip histogram to start with a non-zero bin
            if not len(hist):
                return hist, binCenters
            idx = np.nonzero(hist)[0][0]
            return hist[idx:], binCenters[idx:]
        else:
            hist, binEdges = np.histogram(image.flat, nbins)
            binCenters = (binEdges[:-1] + binEdges[1:]) / 2.
            return hist, binCenters

    '''
    Threshold using Otsu method
    Args:
        image(string) - Input image
        nbins(integer) - Bin count
    Returns:
        threshold(integer) - Threshold value

    ##########################################################################
    # Utilize the Otsu method for determining a threshold to use with a raster
    # the modified histogram function boosts the output
    # http://en.wikipedia.org/wiki/Otsu%27s_method
    ##########################################################################
    '''
    def ThresholdOtsu(self, image, nbins=256):
        hist, binCenters = self.Histogram(image, nbins)
        hist = hist.astype(float)

        # class probabilities for all possible thresholds
        weight1 = np.cumsum(hist)
        weight2 = np.cumsum(hist[::-1])[::-1]
        if not np.all(weight1):
            return 0
        # class means for all possible thresholds
        mean1 = np.cumsum(hist * binCenters) / weight1
        mean2 = (np.cumsum((hist * binCenters)[::-1]) / weight2[::-1])[::-1]

        # Clip ends to align class 1 and class 2 variables:
        # The last value of `weight1`/`mean1` should pair with zero values in
        # `weight2`/`mean2`, which do not exist.
        variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
        if not len(variance12):
            return 0

        idx = np.argmax(variance12)
        threshold = binCenters[:-1][idx]
        return threshold

    '''
    Get approximate breakpoints for image
    Args:
        inputImg(string) - Input image
    Returns:
        low(integer) - Low threshold value
        mod(integer) - Moderate threshold value
        high(integer) - High threshold value
        regrowth(integer) - Regrowth value
        std(integer) - Standard deviation value
    '''
    # Approximate Potential MTBS breakpoints
    def ApproxBreaks(self, inputImg):
        readG = gdal.Open(inputImg, GA_ReadOnly)
        bandG = readG.GetRasterBand(1)
        dataGArr = bandG.ReadAsArray()
        if inputImg.endswith('_nbr.tif'):
            # Set NBR bounds (-1000 >= NBR <= 1000)
            maskArr = dataGArr[(dataGArr >= -1000) & (dataGArr <= 1000)]

            # Set values <= x to x
            # This weights the distribution of image values
            # to the left- or right-hand data distribution
            maskArrLow = np.where(maskArr <= 400, 400, maskArr)
            maskArrMod = np.where(maskArr >= 300, 300, maskArr)
            maskArrHigh = np.where(maskArr >= 100, 100, maskArr)
            regrowth = None

        # Examine dNBR imagery
        elif inputImg.endswith('_dnbr.tif'):
            # Set dNBR bounds (-2000 >= dNBR <= 2000)
            maskArr = dataGArr[(dataGArr > -2000) & (dataGArr < 2000)]

            # Set values <= x to x
            # This weights the distribution of image values
            # to the left- or right-hand data distribution
            maskArrLow = maskArr[(maskArr > -200) & (maskArr <= 200)]
            maskArrMod = maskArr[(maskArr > 200) & (maskArr <= 500)]
            maskArrHigh = maskArr[(maskArr >= 400)]
            regrowth = -150

        # Standard Deviation of masked image
        std = np.std(maskArr)

        # Determine Threshold using Otsu
        threshLow = self.ThresholdOtsu(maskArrLow)
        threshMod = self.ThresholdOtsu(maskArrMod)
        threshHigh = self.ThresholdOtsu(maskArrHigh)

        # Use Standard Deviation to tailor the breaks
        if inputImg.endswith('_nbr.tif'):
            low = int(round(threshLow) - 110.0)
            mod = int(round(threshMod) - 154.0)
            high = int(round(threshHigh) - 95.0)
        elif inputImg.endswith('_dnbr.tif'):
            low = int(round(threshLow) + 59.0)
            mod = int(round(threshMod) - 22.0)
            high = int(round(threshHigh) - 58.0)

        # Clear out in memory arrays
        readG = None
        dataGArr = None
        maskArr = None
        maskArrLow = None
        maskArrMod = None
        maskArrHigh = None
        del readG
        del dataGArr
        del maskArr
        del maskArrLow
        del maskArrMod
        del maskArrHigh

        return low, mod, high, regrowth, std

    '''
    Run the subset process
    Args:
        N/A
    Returns:
        N/A
    '''
    def ProcessSubset(self):
        offCalc = None
        offStd = None
        low = None
        mod = None
        high = None
        regrowth = None
        bbAlbX = None
        bbAlbY = None

        table1 = 'Fires'
        table2 = 'Mappings'

        sql = "SELECT * FROM " + table2 + ' WHERE Id = ' + self.mappingId
        fetch = self.RunQuery(sql)

        fireId = str(fetch[1])

        prefireId = str(fetch[6])
        postfireId = str(fetch[10])
        perimId = str(fetch[12])
        confidence = str(fetch[24])

        sql = "SELECT * FROM " + table1 + ' WHERE Id = ' + str(fireId)
        fetch = self.RunQuery(sql)

        mtbsId = str(fetch[1])
        mtbsIdLower = mtbsId.lower()
        fireName = str(fetch[2])
        fireComment = str(fetch[14])

        if fireComment == '':
            fireComment = 'None'

        fireDate = fetch[4]
        strFireDate = str(fireDate).split('-')
        fireYear = strFireDate[0]
        fireMonth = strFireDate[1]
        fireDay = strFireDate[2]
        # Make Folder
        mappingDir = os.path.join(self.evtProdsPath,
                                  fireYear,
                                  mtbsIdLower,
                                  'mtbs_' + self.mappingId)

        if not os.path.exists(mappingDir):
            os.makedirs(mappingDir)

        # REFL Images
        preYear, preMonth, preDay, prePathRow = self.LoadImage(prefireId)
        perimYear, perimMonth, perimDay, perimPathRow = self.LoadImage(perimId)
        postYear, postMonth, postDay, postPathRow = self.LoadImage(postfireId)
        preDate = preYear + preMonth + preDay
        postDate = postYear + postMonth + postDay
        perimDate = perimYear + perimMonth + perimDay

        postRefl = os.path.join(self.imgSrcPath,
                                postPathRow,
                                postfireId,
                                postfireId + '_REFL.TIF')

        preRefl = os.path.join(self.imgSrcPath,
                               prePathRow,
                               prefireId,
                               prefireId + '_REFL.TIF')

        perimRefl = os.path.join(self.imgSrcPath,
                                 perimPathRow,
                                 perimId,
                                 perimId + '_REFL.TIF')

        # Get Image clip output names
        preReflClip = os.path.join(mappingDir,
                                   (mtbsIdLower + '_' + preDate + '_' +
                                    self.GetSensor(prefireId) + '_refl.tif'))

        postReflClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' + postDate + '_' +
                                     self.GetSensor(postfireId) + '_refl.tif'))

        perimReflClip = os.path.join(mappingDir,
                                     (mtbsIdLower + '_' + perimDate + '_' +
                                      self.GetSensor(perimId) + '_refl.tif'))

        postNbr = os.path.join(self.imgSrcPath,
                               postPathRow,
                               postfireId,
                               postfireId + '_NBR.TIF')

        preNbr = os.path.join(self.imgSrcPath,
                              prePathRow,
                              prefireId,
                              prefireId + '_NBR.TIF')

        perimNbr = os.path.join(self.imgSrcPath,
                                perimPathRow,
                                perimId,
                                perimId + '_nbr.TIF')

        postNbrMask = postNbr.replace('_NBR.TIF', '_GM.tif')

        # Clip Post Nbr
        postNbrClip = os.path.join(mappingDir,
                                   (mtbsIdLower + '_' +
                                    postDate + '_nbr.tif'))

        preNbrClip = os.path.join(mappingDir,
                                  (mtbsIdLower + '_' +
                                   preDate + '_nbr.tif'))

        perimNbrClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' +
                                     perimDate + '_nbr.tif'))

        postMaskClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' +
                                     postDate + '_gapmask.tif'))

        # dNBR Images
        dNbrOutDir = os.path.join(self.imgProcPath,
                                  (prePathRow + '_' + preDate + '_' +
                                   postPathRow + '_' + postDate))
        dNbrImage = ('d' + prePathRow + '_' + preDate + '_' +
                     postPathRow + '_' + postDate + '.tif')

        dNbrMaskImage = ('m' + prePathRow + '_' + preDate + '_' +
                         postPathRow + '_' + postDate + '.tif')

        dNbrOutPath = os.path.join(dNbrOutDir, dNbrImage)
        dNbrMaskPath = os.path.join(dNbrOutDir, dNbrMaskImage)

        # Clip dNBR location
        dNbrClip = os.path.join(mappingDir,
                                (mtbsIdLower + '_' +
                                 preDate + '_' + postDate + '_dnbr.tif'))

        dNbrMaskClip =\
            os.path.join(mappingDir,
                         (mtbsIdLower + '_' +
                          preDate + '_' + postDate + '_gapmask.tif'))

        # Create Fire Shapefile
        if os.path.exists(dNbrOutPath):
            burnShp = (mtbsIdLower + '_' + preDate + '_' +
                       postDate + '_burn_bndy.shp')
        else:
            burnShp = (mtbsIdLower + '_' + postDate + '_burn_bndy.shp')
        burnBndy = os.path.join(mappingDir, burnShp)

        burnTif = burnBndy.replace('.shp', '.tif')

        # Mask Shapefile
        maskShp = burnShp.replace('_burn_bndy.shp', '_mask.shp')
        maskBndy = os.path.join(mappingDir, maskShp)

        maskTif = maskBndy.replace('.shp', '.tif')

        # Add data to Shapefile
        dataSource = self.driver.Open(burnBndy, 1)
        lyr = dataSource.GetLayer()

        count = -1
        for feature in lyr:
            count = count + 1
            geom = feature.GetGeometryRef()
            area = round(float(geom.GetArea()), 5)
            perimeter = geom.Boundary().Length()
            acres = round(float(area * 0.000247105), 5)

            feature.SetField('Id', count)
            feature.SetField('Area', area)
            feature.SetField('Perimeter', perimeter)
            feature.SetField('Acres', acres)
            feature.SetField('Fire_Id', mtbsId)
            feature.SetField('Fire_Name', fireName)
            feature.SetField('Year', fireYear)
            feature.SetField('StartMonth', fireMonth)
            feature.SetField('StartDay', fireDay)
            feature.SetField('Confidence', confidence)
            feature.SetField('Comment', fireComment)
            lyr.SetFeature(feature)

            feature = None
            del feature

        dataSource.Destroy()

        lyr = None
        del lyr

        # Open Mask Bndy using OGR
        dataSource = self.driver.Open(maskBndy, 1)
        lyr = dataSource.GetLayer()

        count = -1
        for feature in lyr:
            count = count + 1
            geom = feature.GetGeometryRef()
            Area = round(float(geom.GetArea()), 5)
            Perimeter = geom.Boundary().Length()

            feature.SetField('Id', count)
            feature.SetField('Area', Area)
            feature.SetField('Perimeter', Perimeter)
            lyr.SetFeature(feature)

            feature = None
            del feature

        dataSource.Destroy()

        lyr = None
        del lyr

        # Open Shapefile using OGR
        dataSource = self.driver.Open(burnBndy, 0)
        lyr = dataSource.GetLayer()

        # Clip images
        orgExtentDict = {}
        for feature in lyr:
            # Get the Value for ORGCODE
            Id = feature.GetField('Fire_Id')
            # Get the envelope geometry
            try:
                geom = feature.GetGeometryRef().GetEnvelope()
                # Set up Dictionary to identify envelopes associated
                #   with each Id
                key = Id

                if key not in orgExtentDict:
                    orgExtentDict[key] = (geom,)
                else:
                    value_list = list(orgExtentDict[key])
                    value_list.append(geom,)
                    value_tuple = tuple(value_list)
                    orgExtentDict[key] = value_tuple
            except Exception:
                pass

        # Need to state if looping through multiple shapes
        lyr.ResetReading()

        dataSource = None
        del dataSource
        lyr = None
        del lyr

        # Loop through each Id in the dictionary to determine
        #   min and max x and y envelope coordinates
        for i in orgExtentDict.items():
            xMin = min(tuple(x[0] for x in i[1]))
            yMin = min(tuple(y[2] for y in i[1]))
            xMax = max(tuple(x[1] for x in i[1]))
            yMax = max(tuple(y[3] for y in i[1]))

            # Calculate the new envelope for the each individual output raster
            self.shpXmin = self.OddEven(float(xMin) - 5000.0)
            self.shpYmin = self.OddEven(float(yMin) - 5000.0)
            self.shpXmax = self.OddEven(float(xMax) + 5000.0)
            self.shpYmax = self.OddEven(float(yMax) + 5000.0)

            # Get Centroid of shape(s)
            bbAlbX = (self.shpXmin + self.shpXmax) / 2
            bbAlbY = (self.shpYmin + self.shpYmax) / 2

            # Clip images
            self.ClipRaster(postRefl, postReflClip)
            self.ClipRaster(preRefl, preReflClip)
            self.ClipRaster(perimRefl, perimReflClip)
            self.ClipRaster(dNbrOutPath, dNbrClip)
            self.ClipRaster(postNbr, postNbrClip)
            self.ClipRaster(preNbr, preNbrClip)
            self.ClipRaster(perimNbr, perimNbrClip)
            self.ClipRaster(dNbrMaskPath, dNbrMaskClip)
            self.ClipRaster(postNbrMask, postMaskClip)

            # Create Binary Mask from Burn Boundary Shapefile
            if os.path.exists(burnBndy):
                cmd = ('gdal_rasterize -burn 1 ' + '-te ' +
                       str(self.shpXmin) + ' ' + str(self.shpYmin) + ' ' +
                       str(self.shpXmax) + ' ' + str(self.shpYmax) + ' ' +
                       '-ot Byte -co NBITS=1 -tr 30 30 -q ' +
                       burnBndy + ' ' + burnTif)
                subprocess.call(cmd, shell=True)
                # os.system(cmd)

            # Create Binary Mask from Mask Shapefile
            if os.path.exists(maskBndy):
                cmd = ('gdal_rasterize -burn 1 ' + '-te ' +
                       str(self.shpXmin) + ' ' + str(self.shpYmin) + ' ' +
                       str(self.shpXmax) + ' ' + str(self.shpYmax) + ' ' +
                       '-ot Byte -co NBITS=1 -tr 30 30 -q ' +
                       maskBndy + ' ' + maskTif)
                # os.system(cmd)
                subprocess.call(cmd, shell=True)

        # Check to see if dnbr or nbr imagery used...
        if os.path.exists(dNbrClip):
            if not os.path.exists(dNbrMaskClip):
                self.ClipRaster(preNbr, preNbrClip)
            # Get dnbr offset value
            offCalc, offStd =\
                self.RnbrOff(dNbrClip, burnTif, maskTif, -100, 100)

        # Start Main Process
        if os.path.exists(dNbrClip):
            imgIn = dNbrClip
        else:
            if os.path.exists(postNbr):
                imgIn = postNbrClip

        # Approximate Breakpoints
        low, mod, high, regrowth, std = self.ApproxBreaks(imgIn)
        # typecast to strings for return
        if offCalc:
            offCalc = str(offCalc)
        low = str(low)
        mod = str(mod)
        high = str(high)
        regrowth = str(regrowth)
        if offStd:
            offStd = str(offStd)
        bbAlbX = str(bbAlbX)
        bbAlbY = str(bbAlbY)

        QtGui.QMessageBox.information(None,
                                      "Subset Complete",
                                      'Subset step is Complete',
                                      QtGui.QMessageBox.Ok)

        return offCalc, low, mod, high, regrowth, offStd, bbAlbX, bbAlbY

    '''
    Clip an input raster to specified extents.
    Args:
        inFile(string) - Input filename.
        outFile(string) - Output filename.
    Returns:
        N/A
    '''
    def ClipRaster(self, inFile, outFile):
        # TODO - at time of release both os.system and subprocess.call
        # for gdal_translate cause a crash dump message when QGIS closes.
        # Leave as subprocess until QGIS bug is resolved. There is a
        # processing module within QGIS that is supposed to handle such
        # things but is also too glitchy to trust at this point.
        if os.path.exists(inFile) and not os.path.exists(outFile):
            gRasterLayer = QgsRasterLayer(inFile, os.path.basename(inFile))
            if not gRasterLayer.isValid():
                QtGui.QMessageBox.warning(None,
                                          "Raster layer problem",
                                          inFile + " is invalid!",
                                          QtGui.QMessageBox.Ok)
                raise IOError(inFile + " is invalid!")
#            projwinString = (str(self.shpXmin) + ", " +
#                             str(self.shpXmax) + ", " +
#                             str(self.shpYmin) + ", " +
#                             str(self.shpYmax))

            cmd = ('gdalwarp -q -te ' + str(self.shpXmin) + ' ' +
                   str(self.shpYmin) + ' ' + str(self.shpXmax) + ' ' +
                   str(self.shpYmax) + ' ' + inFile + ' ' + outFile)
            # os.system(cmd)
            subprocess.call(cmd, shell=True)

#            processing.runalg("gdalogr:cliprasterbyextent",
#                              {"INPUT": gRasterLayer,
#                               "PROJWIN": projwinString,
#                               "RTYPE": 1,
#                               "OUTPUT": outFile})
            outLayer = QgsRasterLayer(outFile, os.path.basename(outFile))
            if not outLayer.isValid():
                QtGui.QMessageBox.warning(None,
                                          "Clip - subset error",
                                          outFile + " is invalid!",
                                          QtGui.QMessageBox.Ok)

            gRasterLayer = None
            outLayer = None
            del gRasterLayer
            del outLayer
