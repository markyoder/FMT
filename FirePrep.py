"""
/***************************************************************************
Name		     : FirePrep
Description          : Fire Prep functions for QGIS FMT Plugin
copyright            : (C) 2017 by Cheryl Holen
email                : cheryl.holen.ctr@usgs.gov
Created              : Oct 13, 2017
Updated              : Oct 23, 2017 - Corrected check dnbrImg to dnbrOutPath
                       Jan 2, 2018 - Path Row values to 3 digits
                       Jan 17, 2018 - Close projTemp and remove projInFile
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

    Fire Prep for Open Source MTBS

    References:
    http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
    http://landsathandbook.gsfc.nasa.gov/pdfs/L5TMLUTIEEE2003.pdf

"""
import os
from osgeo import ogr
from osgeo import gdal
from osgeo import osr
from osgeo.gdalconst import GA_ReadOnly
from PyQt4 import QtGui
from pyspatialite import dbapi2 as sqlite


class FirePrep():
    def __init__(self, mappingId, parentPath):
        self.parentPath = parentPath
        self.mappingId = mappingId
        self.img_src_path =\
            os.path.join(self.parentPath, 'img_src', 'landsat')
        self.img_proc_path =\
            os.path.join(self.parentPath, 'img_proc', 'landsat')
        self.evtProdsPath =\
            os.path.join(self.parentPath, 'event_prods', 'fire')

    def LoadImage(self, imgId):
        imgYr = None
        imgMth = None
        imgDay = None
        imgPathRow = None
        if imgId:
            imgYr = imgId[7:11]
            imgMth = imgId[11:13]
            imgDay = imgId[13:15]
            imgPathRow = imgId[1:4] + imgId[4:7]

            return imgYr, imgMth, imgDay, imgPathRow

    # Get Projection from image
    def GetProj(self, img):
        ds = gdal.Open(img)
        rProj = ds.GetProjectionRef()
        ds = None
        del ds
        return rProj

    def GetGeoInfo(self, FileName):
        srcDs = gdal.Open(FileName, GA_ReadOnly)
        NDV = srcDs.GetRasterBand(1).GetNoDataValue()
        xsize = srcDs.RasterXSize
        ysize = srcDs.RasterYSize
        geoXfrm = srcDs.GetGeoTransform()
        proj = osr.SpatialReference()
        proj.ImportFromWkt(srcDs.GetProjectionRef())
        dType = srcDs.GetRasterBand(1).DataType
        dType = gdal.GetDataTypeName(dType)
        return NDV, xsize, ysize, geoXfrm, proj, dType

    def CreateShp(self, shape_name, shape_loc, image_loc):
        if not os.path.exists(shape_loc):
            driver = ogr.GetDriverByName("ESRI Shapefile")
            dataSrc = driver.CreateDataSource(shape_loc)
            srs = osr.SpatialReference()
            srs.ImportFromWkt(self.GetProj(image_loc))

            if not shape_name.endswith('_mask.shp'):
                layer = dataSrc.CreateLayer("Fire", srs, ogr.wkbPolygon)
                fieldId = ogr.FieldDefn("Id", ogr.OFTInteger)
                fieldId.SetWidth(6)
                layer.CreateField(fieldId)

                fieldArea = ogr.FieldDefn("Area", ogr.OFTReal)
                fieldArea.SetWidth(18)
                layer.CreateField(fieldArea)

                fieldPerim = ogr.FieldDefn("Perimeter", ogr.OFTReal)
                fieldPerim.SetWidth(18)
                layer.CreateField(fieldPerim)

                fieldAcres = ogr.FieldDefn("Acres", ogr.OFTReal)
                fieldAcres.SetWidth(18)
                layer.CreateField(fieldAcres)

                fieldFire = ogr.FieldDefn("Fire_ID", ogr.OFTString)
                fieldFire.SetWidth(30)
                layer.CreateField(fieldFire)

                fieldName = ogr.FieldDefn("Fire_Name", ogr.OFTString)
                fieldName.SetWidth(50)
                layer.CreateField(fieldName)

                fieldYear = ogr.FieldDefn("Year", ogr.OFTInteger)
                fieldYear.SetWidth(4)
                layer.CreateField(fieldYear)

                fieldMonth = ogr.FieldDefn("StartMonth", ogr.OFTInteger)
                fieldMonth.SetWidth(4)
                layer.CreateField(fieldMonth)

                fieldDay = ogr.FieldDefn("StartDay", ogr.OFTInteger)
                fieldDay.SetWidth(4)
                layer.CreateField(fieldDay)

                fieldCon = ogr.FieldDefn("Confidence", ogr.OFTString)
                fieldCon.SetWidth(6)
                layer.CreateField(fieldCon)

                fieldCom = ogr.FieldDefn("Comment", ogr.OFTString)
                fieldCom.SetWidth(80)
                layer.CreateField(fieldCom)

                feature = ogr.Feature(layer.GetLayerDefn())
                feature.Destroy()
                dataSrc.Destroy()
            else:
                layer = dataSrc.CreateLayer("Fire", srs, ogr.wkbPolygon)

                fieldId = ogr.FieldDefn("Id", ogr.OFTInteger)
                fieldId.SetWidth(6)
                layer.CreateField(fieldId)

                fieldArea = ogr.FieldDefn("Area", ogr.OFTReal)
                fieldArea.SetWidth(18)
                layer.CreateField(fieldArea)

                fieldPerim = ogr.FieldDefn("Perimeter", ogr.OFTReal)
                fieldPerim.SetWidth(18)
                layer.CreateField(fieldPerim)

                fieldDes = ogr.FieldDefn("Descript", ogr.OFTString)
                fieldDes.SetWidth(30)
                layer.CreateField(fieldDes)
                feature = ogr.Feature(layer.GetLayerDefn())
                feature.Destroy()
                dataSrc.Destroy()

    def ProcessFirePrep(self):
        table1 = 'Fires'
        table2 = 'Mappings'
        # FIXME - database reads/writes should be in their own class
        dbDir = os.path.dirname(os.path.realpath(__file__))
        dbName = 'FireInfo.sqlite'
        dbFile = os.path.join(dbDir, dbName)
        dbMap = sqlite.connect(dbFile)

        cursorMap = dbMap.cursor()

        sql = "SELECT * FROM " + table2 + ' WHERE id = ' + self.mappingId

        query = cursorMap.execute(sql)

        fetch = cursorMap.fetchone()
        fire_id = str(fetch[1])
        preFireId = str(fetch[6])
        postFireId = str(fetch[10])
        perimId = str(fetch[12])

        sql = "SELECT * FROM " + table1 + ' WHERE id = ' + str(fire_id)

        query = cursorMap.execute(sql)
        fetch = cursorMap.fetchone()

        mtbsId = fetch[1]

        fire_date = fetch[4]
        StrFireDate = str(fire_date).split('-')
        FireYear = StrFireDate[0]

        # Make Folder
        mappingDir = os.path.join(self.evtProdsPath,
                                  FireYear,
                                  mtbsId.lower(),
                                  'mtbs_' + self.mappingId)

        if not os.path.exists(mappingDir):
            os.makedirs(mappingDir)

        # REFL Images
        preYear, preMonth, preDay, prePathRow = self.LoadImage(preFireId)
        perimYear, perimMonth, perimDay, perimPathRow = self.LoadImage(perimId)
        postYear, postMonth, postDay, postPathRow = self.LoadImage(postFireId)
        preDate = preYear + preMonth + preDay
        postDate = postYear + postMonth + postDay

        postRefl = os.path.join(self.img_src_path,
                                postPathRow,
                                postFireId,
                                postFireId + '_REFL.TIF')
        preRefl = os.path.join(self.img_src_path,
                               prePathRow,
                               preFireId,
                               preFireId + '_REFL.TIF')
        perimRefl = os.path.join(self.img_src_path,
                                 perimPathRow,
                                 perimId,
                                 perimId + '_REFL.TIF')

        postNbr = os.path.join(self.img_src_path,
                               postPathRow,
                               postFireId,
                               postFireId + '_NBR.TIF')

        preNbr = os.path.join(self.img_src_path,
                              prePathRow,
                              preFireId,
                              preFireId + '_NBR.TIF')

        perimNbr = os.path.join(self.img_src_path,
                                perimPathRow,
                                perimId,
                                perimId + '_NBR.TIF')

        dnbrOutDif =\
            os.path.join(self.img_proc_path,
                         (prePathRow + '_' + preDate + '_' +
                          postPathRow + '_' + postDate))
        dnbrImg = ('d' + prePathRow + '_' + preDate + '_' +
                   postPathRow + '_' + postDate + '.tif')

        dnbrOutPath = os.path.join(dnbrOutDif, dnbrImg)

        NDV, xsize, ysize, geoXfrm, Projection, DataType =\
            self.GetGeoInfo(postRefl)
        proj4 = Projection.ExportToProj4()

        if os.path.exists(dnbrOutPath):
            if os.path.exists(perimRefl):
                templateTemp =\
                    os.path.join(self.parentPath,
                                 'templates', 'dnbr_perim_template.qgs')
                projInFile =\
                    os.path.join(self.parentPath,
                                 'templates', 'dnbr_perim_template_copy.qgs')
            else:
                templateTemp =\
                    os.path.join(self.parentPath,
                                 'templates', 'dnbr_template.qgs')
                projInFile =\
                    os.path.join(self.parentPath,
                                 'templates', 'dnbr_template_copy.qgs')
        else:
            if os.path.exists(perimRefl):
                templateTemp =\
                    os.path.join(self.parentPath,
                                 'templates', 'ss_perim_template.qgs')
                projInFile =\
                    os.path.join(self.parentPath,
                                 'templates', 'ss_perim_template_copy.qgs')
            else:
                templateTemp =\
                    os.path.join(self.parentPath,
                                 'templates', 'ss_template.qgs')
                projInFile =\
                    os.path.join(self.parentPath,
                                 'templates', 'ss_template_copy.qgs')

        with open(os.path.join(templateTemp)) as infile, \
                open(os.path.join(projInFile), 'w') as outfile:
            for line in infile:
                if '<proj4>Insert_Proj4</proj4>' in line:
                    insertString = '<proj4>'+str(proj4)+'</proj4>'
                    outfile.write(insertString)
                else:
                    outfile.write(line)

        # Create Fire Shapefile
        if os.path.exists(dnbrOutPath):
            burnShp = (mtbsId.lower() + '_' +
                       preDate + '_' +
                       postDate + '_burn_bndy.shp')
        else:
            burnShp = (mtbsId.lower() + '_' +
                       postDate + '_burn_bndy.shp')
        burnBndy = os.path.join(mappingDir, burnShp)

        if not os.path.exists(burnBndy):
            self.CreateShp(burnShp, burnBndy, postNbr)
        else:
            QtGui.QMessageBox.warning(None,
                                      "Shapefile creation",
                                      burnShp + " already exists!",
                                      QtGui.QMessageBox.Ok)

        # Create Mask Shapefile
        maskShp = burnShp.replace('_burn_bndy.shp', '_mask.shp')
        maskBndy = os.path.join(mappingDir, maskShp)

        if not os.path.exists(maskBndy):
            self.CreateShp(maskShp, maskBndy, postNbr)
        else:
            QtGui.QMessageBox.warning(None,
                                      "Shapefile creation",
                                      maskShp + " already exists!",
                                      QtGui.QMessageBox.Ok)

        # Create QGIS project and add data
        projOutFile = burnBndy.replace('_burn_bndy.shp', '.qgs')

        if not os.path.exists(projOutFile):
            projTemp = open(projInFile, 'r')
            projOut = open(projOutFile, 'w')

            for line in projTemp:
                if 'Path_PreSceneNbr' in line:
                    projOut.write(line.replace('Path_PreSceneNbr',
                                               preNbr.replace(os.sep, '/')))
                elif 'Path_PostSceneNbr' in line:
                    projOut.write(line.replace('Path_PostSceneNbr',
                                               postNbr.replace(os.sep, '/')))
                elif 'Path_PerimSceneNbr' in line:
                    projOut.write(line.replace('Path_PerimSceneNbr',
                                               perimNbr.replace(os.sep, '/')))
                elif 'Path_PreSceneRefl' in line:
                    projOut.write(line.replace('Path_PreSceneRefl',
                                               preRefl.replace(os.sep, '/')))
                elif 'Path_PostSceneRefl' in line:
                    projOut.write(line.replace('Path_PostSceneRefl',
                                               postRefl.replace(os.sep, '/')))
                elif 'Path_PerimSceneRefl' in line:
                    projOut.write(line.replace('Path_PerimSceneRefl',
                                               perimRefl.replace(os.sep, '/')))
                elif 'Path_PostScenedNBR' in line:
                    projOut.write(line.replace('Path_PostScenedNBR',
                                               dnbrOutPath.replace(os.sep,
                                                                   '/')))
                elif 'Path_Burn_Bndy' in line:
                    projOut.write(line.replace('Path_Burn_Bndy',
                                               burnBndy.replace(os.sep, '/')))
                elif 'Path_Mask' in line:
                    projOut.write(line.replace('Path_Mask',
                                               maskBndy.replace(os.sep, '/')))
                elif 'PreSceneNbr' in line:
                    projOut.write(line.replace('PreSceneNbr',
                                               preFireId + '_NBR.TIF'))
                elif 'PreSceneRefl' in line:
                    projOut.write(line.replace('PreSceneRefl',
                                               preFireId + '_REFL.TIF'))
                elif 'PostSceneNbr' in line:
                    projOut.write(line.replace('PostSceneNbr',
                                               postFireId + '_NBR.TIF'))
                elif 'PostSceneRefl' in line:
                    projOut.write(line.replace('PostSceneRefl',
                                               postFireId + '_REFL.TIF'))
                elif 'PerimSceneNbr' in line:
                    projOut.write(line.replace('PerimSceneNbr',
                                               perimId + '_NBR.TIF'))
                elif 'PerimSceneRefl' in line:
                    projOut.write(line.replace('PerimSceneRefl',
                                               perimId + '_REFL.TIF'))
                elif 'PostScenedNbr' in line:
                    projOut.write(line.replace('PostScenedNBR', dnbrImg))
                elif 'BurnBndy' in line:
                    projOut.write(line.replace('BurnBndy', burnShp))
                elif 'FireMask' in line:
                    projOut.write(line.replace('FireMask', maskShp))
                else:
                    projOut.write(line)
            projOut.close()
            projTemp.close()
            os.remove(projInFile)

        QtGui.QMessageBox.information(None,
                                      "Fire Prep Complete",
                                      'Fire prep is Complete',
                                      QtGui.QMessageBox.Ok)
