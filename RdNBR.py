"""
/***************************************************************************
Name		     : RdNBR creation
Description          : RdNBR creation functions for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Oct 18, 2017
Updated              :
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

    RdNBR creation for Open Source MTBS

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""

import os
from osgeo import gdal
import numpy as np
from pyspatialite import dbapi2 as sqlite
from PyQt4 import QtGui


class RdNBR():
    def __init__(self, mappingId, parentPath, offCalc):
        self.mappingId = mappingId
        self.offCalc = offCalc
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

    def RdNBRProcess(self):
        table1 = 'Fires'
        table2 = 'Mappings'

        sql = ("SELECT * FROM " + table2 + ' WHERE Id = ' + self.mappingId)
        fetch = self.RunQuery(sql)

        fireId = str(fetch[1])
        prefireId = str(fetch[6])
        postfireId = str(fetch[10])

        sql = ("SELECT * FROM " + table1 + ' WHERE Id = ' + str(fireId))
        fetch = self.RunQuery(sql)

        mtbsId = str(fetch[1])
        mtbsIdLower = mtbsId.lower()
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

        preYear, preMonth, preDay, prePr = self.ExtractImageParams(prefireId)
        postYear, postMonth, postDay, postPr =\
            self.ExtractImageParams(postfireId)
        preDate = preYear + preMonth + preDay
        postDate = postYear + postMonth + postDay

        preNbrClip = os.path.join(mappingDir,
                                  (mtbsIdLower + '_' + preDate + '_nbr.tif'))

        # Clip dNBR location
        dNbrClip = os.path.join(mappingDir,
                                (mtbsIdLower + '_' +
                                 preDate + '_' + postDate + '_dnbr.tif'))

        if not os.path.exists(preNbrClip):
            QtGui.QMessageBox.critical(None,
                                       "RdNBR Error!",
                                       "There is no NBR image to use.\n" +
                                       preNbrClip +
                                       "\n Exiting!",
                                       QtGui.QMessageBox.Ok)
            return
        if not os.path.exists(dNbrClip):
            QtGui.QMessageBox.critical(None,
                                       "RdNBR Error!",
                                       "There is no dNBR image to use.\n" +
                                       dNbrClip +
                                       "\n Exiting!",
                                       QtGui.QMessageBox.Ok)
            return

        # Open Prefire Nbr
        preDs = gdal.Open(preNbrClip)
        preBand = preDs.GetRasterBand(1)
        preRows = preBand.YSize
        preCols = preBand.XSize
        preProj = preDs.GetProjection()
        preGeo = preDs.GetGeoTransform()

        preArr = np.array(preBand.ReadAsArray(0, 0,
                                              preCols,
                                              preRows),
                          dtype=np.float16)

        # Open dNBR imagery
        dNbrDs = gdal.Open(dNbrClip)
        dNbrBand = dNbrDs.GetRasterBand(1)
        dNbrRows = dNbrBand.YSize
        dNbrCols = dNbrBand.XSize

        dNbrArr = np.array(dNbrBand.ReadAsArray(0, 0,
                                                dNbrCols,
                                                dNbrRows),
                           dtype=np.float16)

        # Compute RdNBR array
        # Let numpy handle division by 0, but don't output an error message
        np.seterr(divide='ignore')
        rDnbrArr =\
            (dNbrArr - float(self.offCalc)) / np.sqrt(np.abs(preArr / 1000))

        # Output RdNBR raster
        rDnbrOutPath = dNbrClip.replace('dnbr.tif', 'rdnbr.tif')
        rDnbrGeo = preGeo
        rDnbrProj = preProj

        driver = gdal.GetDriverByName("GTiff")
        rdNbrDs = driver.Create(rDnbrOutPath,
                                preCols,
                                preRows,
                                1, gdal.GDT_Int16)
        rdNbrDs.SetGeoTransform(rDnbrGeo)
        rdNbrDs.SetProjection(rDnbrProj)
        rDnbrBand = rdNbrDs.GetRasterBand(1)
        rDnbrBand.WriteArray(rDnbrArr)

        del rDnbrBand
        dNbrDs = None

        preDs = None
        del preDs
        preBand = None
        del preBand

        preArr = None
        del preArr

        os.remove(preNbrClip)
