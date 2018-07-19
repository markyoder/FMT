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
 This script initializes the plugin, making it known to QGIS.
Modified: Feb 16, 2018: Changed event mapping tool to fire mapping tool, PEP8
"""


def name():
    return "FMT plugin"


def description():
    return "Fire Mapping Tool"


def version():
    return "Version 0.1"


def qgisMinimumVersion():
    return "1.0"


def classFactory(iface):
    # load FMT class from file FMT
    from FMT import FMT
    return FMT(iface)
