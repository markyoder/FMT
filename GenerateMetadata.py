"""
/***************************************************************************
Name		     : GenerateMetadata
Description          : Generate metadata function for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Nov 06, 2017
Updated              : Jan 2, 2017 - Path Row values to 3 digits

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

    Generate metadata for Open Source MTBS

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""
import calendar
import math
import os
from osgeo import ogr
from osgeo import osr
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
from PyQt4 import QtGui
from pyspatialite import dbapi2 as sqlite

MINPERDEG = 60.0
SECPERDEG = 3600.0
HALFCELL = 15.0


class GenerateMetadata():
    def __init__(self, mappingId, parentPath):
        self.parentPath = parentPath
        self.mappingId = mappingId
        self.driver = ogr.GetDriverByName("ESRI Shapefile")
        self.imgSrcPath =\
            os.path.join(self.parentPath, 'img_src', 'landsat')
        self.imgProcPath =\
            os.path.join(self.parentPath, 'img_proc', 'landsat')
        self.evtProdsPath =\
            os.path.join(self.parentPath, 'event_prods', 'fire')

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
        num15s = oord // HALFCELL
        dec, intpart15 = math.modf(num15s)

        if (oord > 0 and intpart15 % 2 == 0):
            newVal = HALFCELL * (num15s + 1)
        elif (oord < 0 and intpart15 % 2 == 0):
            newVal = HALFCELL * (num15s + 1)
        else:
            newVal = HALFCELL * num15s
        return int(newVal)

    '''
    Get Bounding Box Coords
    Args:
        xAlb(integer) - X Albers Value
        yAlb(integer) - Y Albers Value
        bDist(integer) - Buffer distance
    Returns:
        xmin(integer) - Min X value
        ymin(integer) - Min y value
        xmax(integer) - Max X value
        ymax(integer) - Max y value
    '''
    def GetBb(self, xAlb, yAlb, bDist):
        xmin = str(self.OddEven(xAlb) - bDist)
        ymin = str(self.OddEven(yAlb) - bDist)
        xmax = str(self.OddEven(xAlb) + bDist)
        ymax = str(self.OddEven(yAlb) + bDist)

        return xmin, ymin, xmax, ymax

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
    Extract info from image
    Args:
        fileName(string) - Input image filename
    Returns:
        NDV(integer) - No data value
        xsize(integer) - Column count
        ysize(integer) - Row count
        gXFrm(object) - GeoTransform
        proj(string) - Projection
        dType(integer) - Data type
    '''
    def GetGeoInfo(self, fileName):
        srcDs = gdal.Open(fileName, GA_ReadOnly)
        NDV = srcDs.GetRasterBand(1).GetNoDataValue()
        xsize = srcDs.RasterXSize
        ysize = srcDs.RasterYSize
        gXFrm = srcDs.GetGeoTransform()
        proj = osr.SpatialReference()
        proj.ImportFromWkt(srcDs.GetProjectionRef())
        dType = srcDs.GetRasterBand(1).DataType
        dType = gdal.GetDataTypeName(dType)
        return NDV, xsize, ysize, gXFrm, proj, dType

    '''
    Spatial Coordinate Transformation
    Args:
        epsgCode(string) - Input EPSG code
    Returns:
        spRef(integer) - Spatial reference
    '''
    def GetSpatialRef(self, epsgCode):
        spRef = osr.SpatialReference()
        spRef.ImportFromEPSG(epsgCode)
        return spRef

    '''
    Generate the metadata
    Args:
        N/A
    Returns:
        N/A
    '''
    def GenerateMetadataProcess(self):
        finalPub = '99990101'
        # EPSG code for USGS Albers CONUS
        conusSpRef = self.GetSpatialRef(5070)
        # EPSG code for WGS84
        wgs84SpRef = self.GetSpatialRef(4326)

        WGSCoordXfrm = osr.CoordinateTransformation(conusSpRef, wgs84SpRef)

        table1 = 'Fires'
        table2 = 'Mappings'
        # get mapping info
        sql = "SELECT * FROM " + table2 + ' WHERE Id = ' + self.mappingId
        fetch = self.RunQuery(sql)

        fireId = str(fetch[1])
        prefireId = str(fetch[6])
        postfireId = str(fetch[10])
        perimId = str(fetch[12])
        dNbrOffset = fetch[16]
        if not dNbrOffset:
            dNbrOffset = 'No RdNBR produced; Single scene assessment'
        lowThresh = fetch[17]
        if not lowThresh:
            lowThresh = 'None'
        modThresh = fetch[18]
        if not modThresh:
            modThresh = 'None'
        highThresh = fetch[19]
        if not highThresh:
            highThresh = 'None'
        perimComment = fetch[25]
        if not perimComment:
            perimComment = 'None'
        noThresh = fetch[35]
        if not noThresh:
            noThresh = 'None'
        incThresh = fetch[36]
        if not incThresh:
            incThresh = 'None'
        comments = fetch[37]
        if not comments:
            comments = 'None'
        fireX = float(fetch[42])
        fireY = float(fetch[43])
        predStrat = str(fetch[44])
        sdOffset = fetch[45]

        # get fire info
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
        fireAcres = float(fetch[7])
        firePath = fetch[16]
        fireRow = fetch[17]

        # Get Potential Fire Area
        buffDist =\
            round(math.sqrt(float(fireAcres) * 0.404686 * 10000), 0) + 5000
        # Get bounding Box coordinates
        xmin, ymin, xmax, ymax = self.GetBb(fireX, fireY, buffDist)

        # Make Folder
        mappingDir = os.path.join(self.evtProdsPath,
                                  fireYear,
                                  mtbsIdLower,
                                  'mtbs_' + self.mappingId)

        if not os.path.exists(mappingDir):
            os.makedirs(mappingDir)

        # REFL Images
        preYear, preMonth, preDay, prePathRow = self.LoadImage(prefireId)
        preDate = preYear + preMonth + preDay
        perimYear, perimMonth, perimDay, perimPathRow = self.LoadImage(perimId)
        postYear, postMonth, postDay, postPathRow = self.LoadImage(postfireId)
        postDate = postYear + postMonth + postDay
        perimDate = perimYear + perimMonth + perimDay

        # Get Image clip output names
        preReflClip = os.path.join(mappingDir,
                                   (mtbsIdLower + '_' + preDate + '_' +
                                    self.GetSensor(prefireId) + '_refl.tif'))

        if os.path.exists(preReflClip):
            preFireRefl = preReflClip.replace(mappingDir, '')
            preSensorType = prefireId[0]
            preSensorInfo = (preYear + '-' + preMonth + '-' + preDay +
                             ' / ' + prefireId)
            preReflStmt = ('Subset of Landsat scene used for pre-fire image '
                           '(Bands 1-5, 7; Unsigned 8-bit GeoTIFF)')
        else:
            preFireRefl = 'No pre-fire Landsat image'
            preSensorType = 'Not applicable'
            preSensorInfo = 'Single scene assessment'
            preReflStmt = ('Subset of Landsat scene used for pre-fire image '
                           'not produced.  Single scene assessment')

        postReflClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' + postDate + '_' +
                                     self.GetSensor(postfireId) + '_refl.tif'))
        if os.path.exists(postReflClip):
            postFireRelf = postReflClip.replace(mappingDir, '')
            postReflStmt = ('Subset of Landsat scene used for post-fire image '
                            '(Bands 1-5, 7; Unsigned 8-bit GeoTIFF)')
            postSensorType = postfireId[0]
            postSensorInfo = (postYear + '-' + postMonth + '-' + postDay +
                              ' / ' + postfireId)
        else:
            preSensorType = 'Not applicable'
            preSensorInfo = 'Single scene assessment'

        perimReflClip = os.path.join(mappingDir,
                                     (mtbsIdLower + '_' + perimDate + '_' +
                                      self.GetSensor(perimId) + '_refl.tif'))
        if os.path.exists(perimReflClip):
            perimSensorType = perimId[0]
            perimSensorInfo = (perimYear + '-' + perimMonth + '-' + perimDay +
                               ' / ' + perimId)
        else:
            perimSensorType = 'Not applicable'
            perimSensorInfo = 'Single scene assessment'

        # Clip Post Nbr
        postNbrClip = os.path.join(mappingDir,
                                   (mtbsIdLower + '_' +
                                    postDate + '_nbr.tif'))

        postMaskClip = os.path.join(mappingDir,
                                    (mtbsIdLower + '_' +
                                     postDate + '_gapmask.tif'))
        nbrThresh = postNbrClip.replace('_nbr.tif', '_nbr6.tif')
        # dNBR Images
        dNbrOutDir = os.path.join(self.imgProcPath,
                                  (prePathRow + '_' + preDate + '_' +
                                   postPathRow + '_' + postDate))
        dNbrImage = ('d' + prePathRow + '_' + preDate + '_' +
                     postPathRow + '_' + postDate + '.tif')

        dNbrOutPath = os.path.join(dNbrOutDir, dNbrImage)

        # Clip dNBR location
        dNbrClip = os.path.join(mappingDir,
                                (mtbsIdLower + '_' +
                                 preDate + '_' + postDate + '_dnbr.tif'))

        dNbrMaskClip =\
            os.path.join(mappingDir,
                         (mtbsIdLower + '_' +
                          preDate + '_' + postDate + '_gapmask.tif'))
        dNbrThresh = dNbrClip.replace('_dnbr.tif', '_dnbr6.tif')

        if os.path.exists(dNbrClip):
            threshImage = dNbrThresh
            postFireNbr = dNbrClip.replace(mappingDir, '')
            postNbrStmt = ('dNBR used for burn severity analysis and '
                           'mapping; subset to the fire area '
                           '(Signed 16-bit GeoTIFF)')
        else:
            threshImage = nbrThresh
            postFireNbr = postNbrClip.replace(mappingDir, '')
            postNbrStmt = ('NBR used for burn severity analysis and '
                           'mapping; subset to the fire area '
                           '(Signed 16-bit GeoTIFF)')

        # Get Rows/Cols of OutputImage
        NDV, xsize, ysize, GeoT, Projection, DataType =\
            self.GetGeoInfo(threshImage)
        cols = str(xsize)
        rows = str(ysize)

        # Thematic NBR or dNBR
        if os.path.exists(dNbrThresh):
            thematic = dNbrThresh.replace(mappingDir, '')
            themStmt = ('Thematic dNBR; Derived by thresholding dNBR subset '
                        '(8-bit GeoTIFF)')
        else:
            thematic = nbrThresh.replace(mappingDir, '')
            themStmt = ('Thematic NBR; Derived by thresholding post-fire NBR '
                        'subset (8-bit GeoTIFF)')

        if os.path.exists(dNbrThresh):
            gapMask = dNbrMaskClip.replace(mappingDir, '')
        else:
            gapMask = postMaskClip.replace(mappingDir, '')

        # Create Fire Shapefile
        if os.path.exists(dNbrOutPath):
            burnShp = (mtbsIdLower + '_' + preDate + '_' +
                       postDate + '_burn_bndy.shp')
        else:
            burnShp = (mtbsIdLower + '_' + postDate + '_burn_bndy.shp')
        burnBndy = os.path.join(mappingDir, burnShp)
        # Mask Shapefile
        maskShp = burnShp.replace('_burn_bndy.shp', '_mask.shp')

        # Get WGS 84 coords
        # Make sure pixel center
        WgsLr = WGSCoordXfrm.TransformPoint(
            float(xmax) - HALFCELL, float(ymin) + HALFCELL)
        WgsUl = WGSCoordXfrm.TransformPoint(
            float(xmin) + HALFCELL, float(ymax) - HALFCELL)

        nLat = str(round(WgsUl[1], 7))
        wLon = str(round(WgsUl[0], 7))
        sLat = str(round(WgsLr[1], 7))
        eLon = str(round(WgsLr[0], 7))

        # Calculate Degrees, Minutes, Seconds
        nLatSplit = nLat.split('.')
        nLatDeg = nLatSplit[0]
        nLatMin =\
            str(int(round(float('0.' + (nLatSplit[1])[0:2]) * MINPERDEG, 5)))
        nLatSec = str(round(float('0.00' + (nLatSplit[1])[2:]) * SECPERDEG, 5))
        nLatDMS = (nLatDeg + ' ' + nLatMin + ' ' + nLatSec)

        wLonSplit = wLon.split('.')
        wLonDeg = wLonSplit[0]
        wLonMin =\
            str(int(round(float('0.' + (wLonSplit[1])[0:2]) * MINPERDEG, 5)))
        wLonSec = str(round(float('0.00' + (wLonSplit[1])[2:]) * SECPERDEG, 5))
        wLonDMS = (wLonDeg + ' ' + wLonMin + ' ' + wLonSec)

        sLatSplit = sLat.split('.')
        sLatDeg = sLatSplit[0]
        sLatMin =\
            str(int(round(float('0.' + (sLatSplit[1])[0:2]) * MINPERDEG, 5)))
        sLatSec = str(round(float('0.00' + (sLatSplit[1])[2:]) * SECPERDEG, 5))
        sLatDMS = (sLatDeg + ' ' + sLatMin + ' ' + sLatSec)

        eLonSplit = eLon.split('.')
        eLonDeg = eLonSplit[0]
        eLonMin =\
            str(int(round(float('0.' + (eLonSplit[1])[0:2]) * MINPERDEG, 5)))
        eLonSec = str(round(float('0.00' + (eLonSplit[1])[2:]) * SECPERDEG, 5))
        eLonDMS = (eLonDeg + ' ' + eLonMin + ' ' + eLonSec)

        fixCentLat = str(round((float(nLat) + float(sLat)) / 2.0, 5))
        centLatSplit = fixCentLat.split('.')
        centLatDeg = centLatSplit[0]
        centLatMin =\
            str(int(round(float('0.' + (centLatSplit[1])[0:2]) * MINPERDEG,
                          5)))
        centLatSec =\
            str(round(float('0.00' + (centLatSplit[1])[2:]) * SECPERDEG, 5))
        centLatDMS = (centLatDeg + ' ' + centLatMin + ' ' + centLatSec)

        fixCentLon = str(round((float(eLon) + float(wLon)) / 2.0, 5))
        centLonSplit = fixCentLon.split('.')
        centLonDeg = centLonSplit[0]
        centLonMin =\
            str(int(round(float('0.' + (centLonSplit[1])[0:2]) * MINPERDEG,
                          5)))
        centLonSec =\
            str(round(float('0.00' + (centLonSplit[1])[2:]) * SECPERDEG, 5))
        centLonDMS = (centLonDeg + ' ' + centLonMin + ' ' + centLonSec)

        templateMetaFile = os.path.join(self.parentPath,
                                        'templates',
                                        'template_metadata.txt')
        metaFile = burnBndy.replace('_burn_bndy.shp', '_metadata.txt')
#        tempMeta = open(templateMetaFile, 'r')
#        metadataOut = open(metaFile, 'w')
        try:
            with open(templateMetaFile, 'r') as tempMeta,\
                    open(metaFile, 'w') as metadataOut:
                for line in tempMeta:
                    if 'PubDate' in line:
                        metadataOut.write(line.replace('PubDate', finalPub))
                    elif 'Fire_Id' in line:
                        metadataOut.write(line.replace('Fire_Id', mtbsId))
                    elif 'Fire_Name' in line:
                        metadataOut.write(line.replace('Fire_Name', fireName))
                    elif 'F_Date' in line:
                        metadataOut.write(line.replace(
                            'F_Date',
                            (calendar.month_name[int(fireMonth)] + ' ' +
                             fireDay + ', ' + fireYear)))
                    elif 'Assess_Type' in line:
                        metadataOut.write(
                            line.replace('Assess_Type', predStrat))
                    elif 'Fire_Acres' in line:
                        metadataOut.write(
                            line.replace('Fire_Acres', str(fireAcres)))
                    elif 'Fire_Pr' in line:
                        metadataOut.write(line.replace(
                            'Fire_Pr', str(firePath) + '/' + str(fireRow)))
                    elif 'Pre_Sensor_Type' in line:
                        metadataOut.write(
                            line.replace(
                                'Pre_Sensor_Type', preSensorType).replace(
                                'Pre_Sensor_Info', preSensorInfo))
                    elif 'Post_Sensor_Type' in line:
                        metadataOut.write(
                            line.replace(
                                'Post_Sensor_Type', postSensorType).replace(
                                'Post_Sensor_Info', postSensorInfo))
                    elif 'Perimeter_Sensor_Type' in line:
                        metadataOut.write(
                            line.replace('Perimeter_Sensor_Type',
                                         perimSensorType).replace(
                                'Perimeter_Sensor_Info', perimSensorInfo))
                    # Get center pixel
                    elif 'Fix_Ulx' in line:
                        metadataOut.write(
                            line.replace(
                                'Fix_Ulx', str(float(xmin) + HALFCELL)))
                    elif 'Fix_Uly' in line:
                        metadataOut.write(
                            line.replace(
                                'Fix_Uly', str(float(ymax) - HALFCELL)))
                    elif 'Fix_Lrx' in line:
                        metadataOut.write(
                            line.replace(
                                'Fix_Lrx', str(float(xmax) - HALFCELL)))
                    elif 'Fix_Lry' in line:
                        metadataOut.write(
                            line.replace(
                                'Fix_Lry', str(float(ymin) + HALFCELL)))
                    elif 'Fix_Ymax' in line:
                        metadataOut.write(line.replace('Fix_Ymax', ymax))
                    elif 'Fix_Rows' in line:
                        metadataOut.write(line.replace('Fix_Rows', rows))
                    elif 'Fix_Cols' in line:
                        metadataOut.write(line.replace('Fix_Cols', cols))
                    # WGS conversion
                    elif 'Fix_Nlat' in line:
                        metadataOut.write(
                            line.replace('Fix_Nlat', nLat).replace(
                                'Nlat_Degrees_Minutes_Seconds', nLatDMS))
                    elif 'Fix_Slat' in line:
                        metadataOut.write(
                            line.replace('Fix_Slat', sLat).replace(
                                'Slat_Degrees_Minutes_Seconds', sLatDMS))
                    elif 'Fix_Elon' in line:
                        metadataOut.write(
                            line.replace('Fix_Elon', eLon).replace(
                                'Elon_Degrees_Minutes_Seconds', eLonDMS))
                    elif 'Fix_Wlon' in line:
                        metadataOut.write(
                            line.replace('Fix_Wlon', wLon).replace(
                                'Wlon_Degrees_Minutes_Seconds', wLonDMS))
                    elif 'Fix_Centlat' in line:
                        metadataOut.write(
                            line.replace('Fix_Centlat', fixCentLat).replace(
                                'Centlat_Degrees_Minutes_Seconds', centLatDMS))
                    elif 'Fix_Centlon' in line:
                        metadataOut.write(
                            line.replace('Fix_Centlon', fixCentLon).replace(
                                'Centlon_Degrees_Minutes_Seconds', centLonDMS))
                    elif 'dnbr_offset' in line:
                        metadataOut.write(
                            line.replace('dnbr_offset', str(dNbrOffset)))
                    elif 'No_Thresh' in line:
                        metadataOut.write(
                            line.replace('No_Thresh', str(noThresh)))
                    elif 'Increased_Thresh' in line:
                        metadataOut.write(
                            line.replace('Increased_Thresh', str(incThresh)))
                    elif 'Low_Thresh' in line:
                        metadataOut.write(
                            line.replace('Low_Thresh', str(lowThresh)))
                    elif 'Mod_Thresh' in line:
                        metadataOut.write(
                            line.replace('Mod_Thresh', str(modThresh)))
                    elif 'High_Thresh' in line:
                        metadataOut.write(
                            line.replace('High_Thresh', str(highThresh)))
                    elif 'PreFireRefl' in line:
                        metadataOut.write(
                            line.replace('PreFireRefl', preFireRefl))
                    elif 'PreRefl_Statement' in line:
                        metadataOut.write(
                            line.replace('PreRefl_Statement', preReflStmt))
                    elif 'PostFireRefl' in line:
                        metadataOut.write(
                            line.replace('PostFireRefl', postFireRelf))
                    elif 'PostRefl_Statement' in line:
                        metadataOut.write(
                            line.replace('PostRefl_Statement', postReflStmt))
                    elif 'PostFireNbr' in line:
                        metadataOut.write(
                            line.replace('PostFireNbr', postFireNbr))
                    elif 'PostNbr_Statement' in line:
                        metadataOut.write(
                            line.replace('PostNbr_Statement', postNbrStmt))
                    elif 'Thematic' in line:
                        metadataOut.write(line.replace('Thematic', thematic))
                    elif 'Them_Statement' in line:
                        metadataOut.write(
                            line.replace('Them_Statement', themStmt))
                    elif 'GapMask' in line:
                        metadataOut.write(line.replace('GapMask', gapMask))
                    elif 'Burn_Bndy' in line:
                        metadataOut.write(line.replace('Burn_Bndy', burnShp))
                    elif 'Mask_Bndy' in line:
                        metadataOut.write(line.replace('Mask_Bndy', maskShp))
                    elif 'mapping_comments' in line:
                        metadataOut.write(
                            line.replace('mapping_comments', str(comments)))
                    elif 'Perim_comments' in line:
                        metadataOut.write(
                            line.replace('Perim_comments', str(perimComment)))
                    elif 'sd_offset' in line:
                        metadataOut.write(
                            line.replace('sd_offset', str(sdOffset)))
                    else:
                        metadataOut.write(line)
        except:
            QtGui.QMessageBox.warning(None,
                                      "Metadata creation failed",
                                      "Metadata creation failed",
                                      QtGui.QMessageBox.Ok)
            raise IOError
