import os
import env
import Arc_to_BGBase_field_map as a2b
from datetime import datetime

verbose_logging = False  # change to True for additional info while debugging

##### BG-Base stuff #####
# API URLs
api_info_url = 'http://{}/api/plants/{}/{}'  # POST IP address, Accession, Qualifier
api_location_url = 'http://{}/api/plants/{}/{}/location'  # POST IP address, Accession, Qualifier
api_condition_url = 'http://{}/api/plants/{}/{}/conditions'  # POST IP address, Accession, Qualifier
api_measurement_url = 'http://{}/api/plants/{}/{}/measurements'  # POST IP address, Accession, Qualifier
api_labelNeed_url = 'http://{}/api/plants/{}/{}/labelsneeded'  # POST IP address, Accession, Qualifier
api_labelHas_url = 'http://{}/api/plants/{}/{}/labels'  # PUT IP address, Accession, Qualifier

# BG-Base POST headers
bg_headers = {'content-type': 'application/json'}


##### Arc stuff #####
# Endpoints
pc_endpoint = ''
pm_endpoint = ''
pl_endpoint = ''
mp_endpoint = ''
token_endpoint = ''

# Arc POST headers
arc_headers = {'Content-Type':'application/x-www-form-urlencoded'}

# Non-mapped fields to query for
pc_unmapped = ['OBJECTID', 'GlobalID', 'PlantCenterID', 'EditDate', 'DataSource']
pm_unmapped = ['OBJECTID', 'GlobalID', 'PlantCenterID', 'EditDate', 'DataSource']
pl_unmapped = ['PlantCenterID']

# Arc POST query headers
arc_headers = {'Content-Type':'application/x-www-form-urlencoded'}

# Arc token parameters
username = ''
password = ''

ip = ''

referer = ''
verify = False

# Other stuff
script_path = os.path.dirname(os.path.realpath(__file__))
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
log_file = os.path.join(script_path, 'log - arc to bg-base{}.txt'.format(timestamp))


plant_dt_qual_default = 'D'

blocks = {a2b.condition : api_condition_url, 
          a2b.location : api_location_url,
          a2b.measurement: api_measurement_url,
          a2b.label_need: api_labelNeed_url,
          a2b.label_has: api_labelHas_url}

# Arc fields called in script
pcID_fld = 'PlantCenterID'
OID_fld = 'OBJECTID'
has_label_field = 'HasLabelType'
need_label_field = 'NeedLabelType'

# New value for DataSource field once synced to BG-Base
look_for_ds = 'ArcGIS'
new_ds = 'Synced'

# Where statement for Arc query - DataSource is Null or ArcGIS we push to BG-Base,
# if BG-BASE, we don't push those records
where = "DataSource='ArcGIS'"

# Labels list delimiter
delimiter = ';'

# PlantCenterID regex. Ensures that it is format like [alphanumeric string]*[Letter]
# because the script splits on the '*' at a later point.
pcID_regex = '.*.$'
