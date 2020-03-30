# ArcGIS BG-BASE Sync

This GitHub repo contains the Python scripts that synchronize living plant collections records in an ArcGIS Enterprise Geodatabase based on the ArcGIS Parks and Gardens Information Model with a BG-BASE living plant collections database.

### Background
ArcGIS BG-BASE Sync is a powerful set of tools for managed landscapes using BG-BASE to maintain plant records and Esri ArcGIS software for mapping, visualizing and sharing information for internal workflows or to the public through maps and applications.

Through a grant from the <a href="http://www.imls.gov/">Institute of Museum and Library Services (IMLS)</a>, in cooperation with <a href="http://bg-base.com/">BG-BASE</a>, the <a href="http://www.apgg.org/">Alliance of Public Gardens GIS</a>, and <a href="http://www.blueraster.com/">Blue Raster</a>, <a href="http://www.mountauburn.org/">Mount Auburn Cemetery</a> facilitated the development of a set of tools to synchronize plant records between BG-BASE and <a href="http://www.esri.com/">Esri’s</a> ArcGIS platform.

The ArcGIS BG-BASE Sync set of tools allows staff to create new, or update existing records in the office using ArcGIS Desktop, or in the field using Collector for ArcGIS. New records and updates are sent back to BG-BASE on a desired schedule. Similarly, new records and updates from BG-BASE can be synced backed to ArcGIS. This solution thus reduces the time and effort required to curate multiple databases.


### Technical Details
##### Arc_to_BGBase_sync.py
The primary Python script selects updates made in the ArcGIS Parks and Gardens Information Model geodatabase and sends them to BG-BASE based on the field mapping in Arc_to_BGBase_field_map.py.

##### Arc_to_BGBase_field_map.py 
The field mapping script serves as a crosswalk between the attribute field in the ArcGIS Parks and Gardens Information Model and BG-BASE.

##### config.py
The configuration script contains URLs, headers, fields, and variables.

ArcGIS BG-BASE Sync can be scheduled to synchronize ArcGIS plant records data to BG-BASE hourly or the schedule of choice.


### Contact Information
For more information about the ArcGIS BG-BASE Sync solution, and for assistance in configuring it at your institution, please contact us by phone or email.

##### Blue Raster
Christopher Gabris
cgabris@blueraster.com
+1 (703) 678-4314
www.blueraster.com

##### Alliance for Public Gardens GIS
Brian Morgan

bjmorgan@apgg.org | +1 (530) 902-1138 | www.apgg.org




