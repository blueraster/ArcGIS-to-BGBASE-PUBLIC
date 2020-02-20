# Arc-to-BGBase

This repo holds the Python 3 scripts that sync ArcGIS Enterprise Geodatabase Data at Mount Auburn Cemetery data BG-Base.

### Script logic
*Arc_to_BGBase_sync.py* is the main file. It calls *Arc_to_BGBase_field_map.py* to get the Arc to BG-Base field map, and *config.py* for URLs, headers, fields needed that are not in the field mapping, and additional variables.

### Script setup plan
Scheduled task to sync Arc to BG-Base hourly. 

### Background
Through a Federal Grant from IMLS, BGBASE (http://www.bg-base.com/), the Alliance of Public Gardens GIS (APGG https://www.publicgardens.org/resources/alliance-public-gardens-gis) and Blue Raster (https://www.blueraster.com/) teamed up to develop a set of tools to sync plant records in BGBASE and ArcGIS.

This allows Mount Auburn Cemetery staff to make edits in Desktop GIS, or in the field using Collector for ArcGIS and have those updates sync back to BGBASE. Similiarly, new records created in BGBASE or updates to exisiting records would also sync to the ArcGIS Enterprise Geodatabase.

This sync was developed from 2018 to 2020 and is a powerful tool for any Garden using BGBASE to maintain plant records and Esri ArcGIS software for mapping, visualizing and sharing information for internal workflows or to the public through maps and applications.
