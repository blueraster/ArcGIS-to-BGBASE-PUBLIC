import sys
import os
import re
import json
from ast import literal_eval as leval
import requests
from requests.auth import HTTPBasicAuth
from urllib import request, parse
from datetime import datetime as dt
import env
import config as c
import Arc_to_BGBase_field_map as a2b

TOKEN = None

def write_to_log(message, log=c.log_file, priority='low'):
    # Set config.verbose_logging to True when debugging
    print(message)
    if c.verbose_logging or priority == 'high':
        with open(c.log_file, 'a') as log:
            log.write('\n{}'.format(message))

def generate_token():
    data = {
        'username': c.username,
        'password': c.password,
        'client': 'referer',
        'referer': c.referer,
        'expiration': 300,  # 5 minutes
        'f': 'json'
    }

    url = c.token_endpoint
    headers = c.arc_headers
    r = requests.post(url, data=data, headers=headers, verify=c.verify)
    print(r.text)
    r.raise_for_status()
    if 'error' in r.json().keys():
        raise ValueError(r.json()['error'])

    global TOKEN
    TOKEN = r.json()['token']

def get_arc_query_fields(fld_map, table, unmapped_flds=[]):
    write_to_log('get_arc_query_fields: table={}'.format(table))
    write_to_log('get_arc_query_fields: unmapped_fields={}'.format(unmapped_flds))
    flds = unmapped_flds
    for key, value in fld_map.items():
        if key.lower()==table.lower():
            for key2, value2 in value.items():
                flds.append(key2)
    
    flds_str = ','.join(flds)
    write_to_log('get_arc_query_fields: flds_str={}'.format(flds_str))
    return flds_str

def query_arc(endpoint, flds, where, get_geom=True):
    url_query = endpoint + '/query'

    data = {'f': 'json',
            'where': where,
            'outFields' : flds,
            'returnGeometry' : get_geom,
            'token': TOKEN}
    write_to_log('query_arc: url_query={}'.format(url_query))
    write_to_log('query_arc: data={}'.format(data))
    r = requests.post(url_query, data=data, headers=c.arc_headers, verify=c.verify)
    write_to_log('query_arc: r={}'.format(r.content))
    try:
        return r.json()['features']
    except Exception as e:
        write_to_log('ERROR QUERYING ARC', priority='high')
        write_to_log(url_query)
        write_to_log(data)
        write_to_log(c.arc_headers)
        write_to_log(r.content)
        write_to_log(e, priority='high')

        raise ValueError(e)

def build_field_map_a2b(fld_map, block):
    write_to_log('calling build_field_map_a2b')
    body = {}
    for key, value in fld_map.items():
        for key2, value2 in value.items():
            #if value2['bg_block'] == block:
            if block in value2['bg_block']:
                if not key in body:
                    body[key]={}
                body[key][key2] = value2['bg_fld']

    return body

def get_unique_valid_pcIDs(arc_response):

    write_to_log('calling get_unique_valid_pcIDs')
    pcID_unique = []
    for response in arc_response:
        pcID = response['attributes'][c.pcID_fld]

        #if pcID is not None and re.match(regex_pattern, pcID):
        if pcID is not None and pcID not in pcID_unique and re.match(c.pcID_regex, pcID):
            pcID_unique.append(pcID)
            #print('UNIQUE PCID: {}'.format(pcID))
    return [str(pcID) for pcID in pcID_unique]

def populate_bg_block(arc_response, arc_source_table, a2b_map):
    # This is where the remapping actually takes place

    pop_block = {}

    #print('\nSOURCE TABLE ({}):\n{}'.format(arc_source_table, json.dumps(a2b_map[arc_source_table], indent=2)))

    for arc_fld, bg_fld, in a2b_map[arc_source_table].items():
        value = arc_response['attributes'][arc_fld]
        if not value:
            value = ''
        
        # Convert millisecond date to mm/dd/yyyy format
        if arc_fld.lower()=='editdate':
            value = dt.utcfromtimestamp(int(value)/1000).strftime('%m/%d/%Y')
        if arc_fld.lower()=='inspectiondate':
            value = millisecond_to_mmddyyy(int(value))

        # Set the default value for PlantDateQualifier
        if arc_fld.lower()=='plantdatequalifier':
            value = c.plant_dt_qual_default

        pop_block[bg_fld] = value
        #print('ARC FLD: {}  BG FLD: {}  VALUE: {}'.format(arc_fld, bg_fld, value))
    return pop_block

def arc_response_to_bg_block(arc_response, arc_source_table, a2b_map):
    if len(arc_response)==0:
        return {}

    if arc_source_table not in a2b_map:
        return {}

    pcID_dict = {}
    pcID_unique_list = get_unique_valid_pcIDs(arc_response)

    # Loop through each record returned from arc query
    for record in arc_response:
        pcID = record['attributes'][c.pcID_fld]

        if pcID in pcID_unique_list:
            if pcID not in pcID_dict:
                pcID_dict[pcID] = []
            bg_block = populate_bg_block(record, arc_source_table, a2b_map)  # Returns dict
            bg_block['OID'] = record['attributes']['OBJECTID']
            write_to_log('arc_response_to_bg_block: bg_block={}'.format(bg_block))
            # Add x/y/z from ArcGIS geometry
            if block == a2b.location:
                try:
                    bg_block = add_geometry_for_bgbase(bg_block, record['geometry'], a2b.geom)
                except:
                    bg_block = {'x': 0, 'y': 0} # If geometry doesn't exist (would cause script to fail), set x,y at null island.
                    # This is a possible error!

            pcID_dict[pcID].append(bg_block)
    write_to_log('arc_response_to_bg_block: pcID_dict={}'.format(pcID_dict))
    return pcID_dict

def combine_arc_response_values(pc_vals, pm_vals):
    pcID_unique = set([pcID for vals in [pc_vals, pm_vals] for pcID in vals.keys()])
    combined_dict = {}

    # For each unique PlantCenterID create a list of dictionaries (i.e. records) to
    # send to BG-Base by combining Plant Center and Plant Maintenance query responses 
    for pcID in pcID_unique:
        combined_dict[pcID] = []

        try: pc_record = pc_vals[pcID] if len(pc_vals[pcID])>0 else None
        except: pc_record = None
        try: pm_record = pm_vals[pcID] if len(pm_vals[pcID])>0 else None
        except: pm_record = None

        # there will only ever be one pc_record but there could be multiple pm_records
        if pc_record is not None and pm_record is not None:
            for pm_rec in pm_record:
                combined_sub_dict = {}
                combined_sub_dict.update(pc_record[0])
                combined_sub_dict.update(pm_rec)
                combined_sub_dict['pc_OID'] = pc_record[0]['OID']
                combined_sub_dict['pm_OID'] = pm_rec['OID']
                combined_dict[pcID].append(combined_sub_dict)
        elif pc_record is None and pm_record is not None:
            for pm_rec in pm_record:
                combined_dict[pcID].append(pm_rec)
                combined_dict[pcID][-1]['pc_OID'] = None
                combined_dict[pcID][-1]['pm_OID'] = pm_rec['OID']
        elif pc_record is not None and pm_record is None:
            combined_dict[pcID].append(pc_record[0])
            combined_dict[pcID][-1]['pc_OID'] = pc_record[0]['OID']
            combined_dict[pcID][-1]['pm_OID'] = None

    return combined_dict

def query_bgbase(pcID, block):
    write_to_log('querying BG base for validation...')
    acc, qual = pcID.split('*')
    info_url = c.api_info_url.format(env.post_ip_address, acc, qual)
    print('sending request to {}'.format(info_url))
    print(c.arc_headers)
    print(c.verify)
    print('username: {}, pwd: {}'.format(env.user, env.pwd))
    r = requests.get(info_url,
                     headers=c.arc_headers,
                     auth=HTTPBasicAuth(env.user, env.pwd),
                     verify=c.verify)
    print(r)
    try:
        print('query_bgbase: r.json.embedded={}'.format(r.json()['_embedded']))
        print('query_bgbase: api_name.block={}'.format(a2b.api_name[block]))
        [group] = [g for g in r.json()['_embedded']['group'] if g['name'] == a2b.api_name[block]]
        print('query_bgbase: group={}'.format(group))
        print('query_bgbase: group.embedded.history={}'.format(group['_embedded']['history']))
    except Exception as e:
        write_to_log('query_bgbase: error={}'.format(e))
        write_to_log(r.json())
        write_to_log(a2b.api_name[block])
        raise ValueError(str(e))
    return group['_embedded']['history']

def validate_arc_response_values(vals, block):

    required_fields = [vals['bg_fld'] for fieldmap in [a2b.field_map['pc'], a2b.field_map['pm']] for vals in fieldmap.values()
                       if vals['bg_block'] == block and vals['required']]

    valid_vals = {}
    errors = []
    error_pc_OIDs = []
    error_pm_OIDs = []
    for plantCenterID, attrs in vals.items():
        for attr in attrs:
            if all(req_field in attr.keys() and attr[req_field] for req_field in required_fields):
                # query bg-base to get the latest item in this block for this ID
                # first, check if this record is a complete duplicate of that item, if so, continue without adding to valid vals and add notification to errors
                # if not a duplicate, check if the date is different from that item, if so, add this to valid vals, otherwise add an error message
                latest_vals = query_bgbase(plantCenterID, block)
                write_to_log('\nlatest values for {}:'.format(block), priority='high')
                write_to_log(json.dumps(latest_vals, indent=2), priority='high')
                if not latest_vals:
                    write_to_log('no recent values', priority='high')
                    continue   
                latest_val = latest_vals[0]
                [date_field] = [field for field in attr.keys() if field[-3:] == '_dt']
                if not all(str(latest_val[field]) == str(attr[field])
                           # if not (field == date_field and isinstance(field, int)) else str(latest_val[field]) == millisecond_to_mmddyyy(attr[field])
                           for field in attr.keys()
                           if field in latest_val.keys() and latest_val[field] and not isinstance(attr[field], float)):
                    
                    # not duplicate!

                    # attr_date = attr[date_field] if isinstance(attr[date_field], str) else millisecond_to_mmddyyy(attr[date_field])
                    if not str(latest_val[date_field]) == str(attr[date_field]):
                        # not same date!
                        # passed validation, add attributes to valid vals list
                        if plantCenterID in valid_vals.keys():
                            valid_vals[plantCenterID].append(attr)
                        else:
                            valid_vals[plantCenterID] = [attr]
                    else:
                        error_pc_OIDs.append(attr['pc_OID'])
                        error_pm_OIDs.append(attr['pm_OID'])
                        errors.append('PlantCenterID {} has the same date as the latest item, please change the following: {}'.format(plantCenterID, {date_field: attr[date_field]}))
                else:
                    errors.append('PlantCenterID {} has already been uploaded to block {}'.format(plantCenterID, block))
            else:
                error_pc_OIDs.append(attr['pc_OID'])
                error_pm_OIDs.append(attr['pm_OID'])
                errors.append('PlantCenterID {} contains a record with {} fields missing or invalid: {}'.format(plantCenterID, required_fields, attr))

    return valid_vals, errors, error_pc_OIDs, error_pm_OIDs, required_fields

def get_global_IDs_for_log_file(body):    
    # These two try/except statements get global IDs for the Plant Center 
    # and Plant Maintenance records, then deletes them from the POST body. 
    # This allows the global IDs to be written to a log file, while not 
    # being written to the BG-Base POST body.
    globalID_dict = {}
    try: 
        globalID_dict['PlantMaintenance'] = body['pm_globalID'] 
        del body['pm_globalID']
    except:
        pass
    try: 
        globalID_dict['PlantCenter'] = body['pc_globalID'] 
        del body['pc_globalID']
    except:
        pass

    return globalID_dict, body

def prepare_labels(all_labels, url):
    if 'need' in url.lower():
        labels = all_labels[c.need_label_field]
        which_label = 'Need Labels'
    else:
        labels = all_labels[c.has_label_field]
        which_label = 'Has Labels'
    return labels, which_label

def post_or_put_to_bgbase(url, body, method):
    if 'label' not in url:
        globalIDs, new_body = get_global_IDs_for_log_file(body)
    else: 
        globalIDs = None
        new_body, which_label = prepare_labels(body, url)

    try:
        if method=='post':
            r = requests.post(url,
                              data=json.dumps(new_body),
                              headers=c.bg_headers,
                              auth=HTTPBasicAuth(env.user, env.pwd),
                              verify=c.verify)
        elif method=='put':
            r = requests.put(url,
                              data=json.dumps(new_body),
                              headers=c.bg_headers,
                              auth=HTTPBasicAuth(env.user, env.pwd),
                              verify=c.verify)

        if r.status_code==201:
            write_to_log('      Success, <{}>'.format(r.status_code))
            if 'label' not in url:
                for ArcTable, gID in globalIDs.items(): 
                    write_to_log('        Global ID {}: {}'.format(ArcTable, gID), priority='high')
                    write_to_log(json.dumps(dict(filter(lambda elem: len((str(elem[1]))) != 0, new_body.items()))), indent=2, priority='high')
            else:
                write_to_log('        Success at labels:  {}: {}'.format(which_label,  new_body))
            write_to_log('        {}'.format(dict(filter(lambda elem: len(str(elem[1])) != 0, new_body.items()))), priority='high')
            return True
        else:
            write_to_log('      Failed to update BG-Base, status code: {}'.format(r.status_code))
            write_to_log('      {}'.format(dict(filter(lambda elem: len(str(elem[1])) != 0, new_body.items()))), priority='high')

            if 'label' not in url:
                for ArcTable, gID in globalIDs.items(): 
                    write_to_log('        Global ID {}: {}'.format(ArcTable, gID))
                    write_to_log(json.dumps(dict(filter(lambda elem: len(str(elem[1])) != 0, new_body.items())), indent=2), priority='high')
            else:
                write_to_log('        Failed at labels:  {}: {}'.format(which_label,  dict(filter(lambda elem: len(str(elem[1])) != 0, new_body.items()))), priority='high')
            return False

    except Exception as e:
        write_to_log('Error POSTing or PUTing to BG-Base', priority='high')
        write_to_log('url: {}'.format(url), priority='high')
        write_to_log('body: {}'.format(dict(filter(lambda elem: len(str(elem[1])) != 0, new_body.items()))), priority='high')
        write_to_log('Exception: {}'.format(e), priority='high')
        return False

def loop_records_to_send_to_bgbase(data, raw_url, method):
    n=0
    success_pcIDs = []
    fail_pcIDs = []
    for pcID, attributes in data.items():
        n+=1
        acc, qual = pcID.split('*')
        url = raw_url.format(env.post_ip_address, acc, qual)
        write_to_log('    {} URL: {}'.format(n, url))

        i=1
        if 'label' in url:
            result = post_or_put_to_bgbase(url, attributes, method)
            if result:
                success_pcIDs.append(pcID)
            else:
                fail_pcIDs.append(pcID)
        else:
            for attr in attributes:
                # if 'check_dt' in attr:
                #     attr['check_dt'] = millisecond_to_mmddyyy(attr['check_dt'])
                result = post_or_put_to_bgbase(url, attr, method)
                if not result:
                    fail_pc_OIDs.append(attr['pc_OID'])
                    fail_pm_OIDs.append(attr['pm_OID'])
            i+=1
    return fail_pc_OIDs, fail_pm_OIDs

def get_objectIDs(response):
    OIDs = []
    for r in response:
        oid = r['attributes'][c.OID_fld]
        OIDs.append(oid)
        #print(oid)
    return OIDs

def update_DataSource_field(url, OIDs, headers, new_value):
    # where = ("PlantCenterID IN {} AND ({})".format(tuple(pcIDs), c.where) if len(pcIDs) > 1
    #          else "PlantCenterID = '{}' AND ({})".format(pcIDs[0], c.where))
    # update_attrs = query_arc(url, 'OBJECTID', where, get_geom=False)
    # OIDs = [attr['OBJECTID'] for attr in update_attrs]

    update_url = url + '/updateFeatures'
    update_body = []
    for oid in OIDs:
        attributes = {'attributes':{'OBJECTID':  oid, 
                                    'DataSource': new_value}}
        update_body.append(attributes)

    #print(json.dumps(update_body, indent=2))
    
    data = {'f': 'json',
            'features': json.dumps(update_body),
            'token': TOKEN}

    r = requests.post(update_url, data=data, headers=headers, verify=c.verify)
    print('\n{}'.format(r))
    print('\n{}'.format(r.url))
    print('\n{}'.format(json.dumps(json.loads(r.text), indent=2)))

def millisecond_to_mmddyyy(milli):
    s = milli/1000
    d = dt.fromtimestamp(s).strftime('%m/%d/%Y')
    return d

def add_geometry_for_bgbase(bg_block, arc_geom, geom_dict):
    for arc_fld, bg_fld in geom_dict.items():        
        if arc_fld in arc_geom:
            bg_block[bg_fld] = arc_geom[arc_fld]
        else:
            bg_block[bg_fld] = None
    return bg_block

def query_plant_label(endpoint, flds, arc_response):
    if not arc_response:
        return []

    pcIDs = get_unique_valid_pcIDs(arc_response)
    write_to_log('pcIDs: {}'.format(pcIDs))
    # where_label = c.label_where.format(tuple(pcIDs))
    where_label = ("PlantCenterID IN {}".format(tuple(pcIDs)) if len(pcIDs) > 1
                   else "PlantCenterID = '{}'".format(pcIDs[0]))
    write_to_log('where_label: {}'.format(where_label))
    pl_response = query_arc(endpoint, flds, where_label, get_geom=False)

    return pl_response

def pl_response_to_bg_block(pl_response, haslabelfield, needlabelfield):
    bg_label_block = {}

    for record in pl_response:
        pcID = record['attributes']['PlantCenterID']
        has_label = record['attributes'][haslabelfield]
        need_label = record['attributes'][needlabelfield]
        
        # Initialize dictionary of pdIDs and label dictionaries to hold lists of labels
        if pcID not in bg_label_block:
            bg_label_block[pcID] = {}
            bg_label_block[pcID][haslabelfield] = []
            bg_label_block[pcID][needlabelfield] = []

        # If HasLabelType exists, it is appended to a list of Has Labels for that PC ID
        if has_label:
            bg_label_block[pcID][haslabelfield].append(has_label)

        # If NeedLabelType exists, it is appended to a list of Need Labels for that PC ID
        if need_label:
            bg_label_block[pcID][needlabelfield].append(need_label)

    return bg_label_block

def get_plant_center_update_feature(pm_attr, pm_flds, pc_attr, pc_flds, geom):
    feature = {
        'attributes': {
            'OBJECTID': int(pc_attr['OBJECTID']),
            'GlobalID': pc_attr['GlobalID']
            # 'PlantCondition': pm_attr['PlantCondition']
        },
        'geometry': geom
    }
    for from_fld, to_fld in pm_flds.items():
        feature['attributes'][to_fld] = pm_attr[from_fld]
    for from_fld, to_fld in pc_flds.items():
        feature['attributes'][to_fld] = pc_attr[from_fld]
    return feature

def update_plant_center_features(update_features):
    payload = {
        'features': json.dumps(update_features),
        'token': TOKEN,
        'f': 'json'
    }
    headers = c.arc_headers
    url = c.pc_endpoint + '/updateFeatures' + '?' + parse.urlencode(payload)
    r = requests.post(url, verify=c.verify)
    if 'error' in r.json().keys():
        write_to_log('ERROR QUERYING ARC')
        write_to_log(url)
        write_to_log(payload)
        write_to_log(r.content)
        raise ValueError(r.json()['error'])
    assert all(record['success'] for record in r.json()['updateResults'])

def sync_plant_maintenance_to_plant_center(pm_response):

    pm_attrs = {}
    for pm_record in pm_response:
        pcID = pm_record['attributes']['PlantCenterID']
        if pcID in pm_attrs.keys():
            [date_field] = [field for field in pm_record['attributes'].keys() if field[-4:] == 'Date']
            if pm_record['attributes'][date_field] > pm_attrs[pcID][date_field]:
                pm_attrs[pcID] = pm_record['attributes']
        pm_attrs[pcID] = pm_record['attributes']
        
    if not pm_attrs:
        return

    # get plant center features corresponding to the plant maintenance records
    where = ("PlantCenterID IN {}".format(tuple(pm_attrs.keys())) if len(pm_attrs.keys()) > 1
             else "PlantCenterID = '{}'".format(list(pm_attrs.keys())[0]))
    pc_response = query_arc(c.pc_endpoint, 'OBJECTID,GlobalID,PlantCenterID,PlantCondition', where)

    # combine objectid from plant center feature with condition from plant maintenance record to get update features
    update_features = []
    for plantCenterID, pm_attr in pm_attrs.items():
        pc_records = [pc_record for pc_record in pc_response
                     if pc_record['attributes']['PlantCenterID'].strip() == plantCenterID]
        if not pc_records:
            raise ValueError('No plant center features connected to plant maintenance record with ID {}'.format(plantCenterID))
        if len(pc_records) > 1:
            raise ValueError('Multiple plant center features have same ID {}'.format(plantCenterID))
        pc_attr = pc_records[0]['attributes']
        pc_geom = pc_records[0]['geometry']
        pm_flds = {'PlantCondition': 'PlantCondition'}
        update_features.append(get_plant_center_update_feature(pm_attr, pm_flds, pc_attr, {}, pc_geom))

    write_to_log('Plant center update features:')
    write_to_log(json.dumps(update_features, indent=2))

    update_plant_center_features(update_features)

def update_plant_center_coordinate_fields(pc_response):
    update_features = []
    for pc_record in pc_response:
        pc_attr = pc_record['attributes']
        pc_attr.update(pc_record['geometry'])
        pc_geom = pc_record['geometry']
        pc_flds = {
            'x': 'XCoordinate',
            'y': 'YCoordinate'
        }
        update_features.append(get_plant_center_update_feature(None, {}, pc_attr, pc_flds, pc_geom))

    write_to_log('Plant center update features for coordinates: ')
    write_to_log(json.dumps(update_features, indent=2))

    update_plant_center_features(update_features)



# Main Code
try:
    write_to_log('\n\n[{}] Start run'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S')))

    generate_token()
    write_to_log('TOKEN: {}'.format(TOKEN))

    pc_query_flds = get_arc_query_fields(a2b.field_map, a2b.pc, c.pc_unmapped)
    pm_query_flds = get_arc_query_fields(a2b.field_map, a2b.pm, c.pm_unmapped)    
    pl_query_flds = get_arc_query_fields(a2b.field_map, a2b.pl, c.pl_unmapped)

    write_to_log('\nQuerying plant maintenance endpoint')
    write_to_log('where: {}'.format(c.where))
    pm_response = query_arc(c.pm_endpoint, pm_query_flds, c.where)
    write_to_log('Plant maintenance response:')
    write_to_log(json.dumps(pm_response, indent=2))

    write_to_log('\nSyncing plant center table with plant maintenance response')
    sync_plant_maintenance_to_plant_center(pm_response)

    write_to_log('\nQuerying plant center endpoint')
    pcIDs = [record['attributes']['PlantCenterID'] for record in pm_response]
    where = ("PlantCenterID IN {} OR {}".format(tuple(pcIDs), c.where) if len(pcIDs) > 1
             else "PlantCenterID = '{}' OR {}".format(pcIDs[0], c.where) if len(pcIDs) == 1
             else c.where)
    write_to_log('where: {}'.format(where))
    pc_response = query_arc(c.pc_endpoint, pc_query_flds, where)
    write_to_log('Plant center response:')
    write_to_log(json.dumps(pc_response, indent=2))

    if pc_response:
        write_to_log('\nUpdating coordinate fields in plant center features')
        update_plant_center_coordinate_fields(pc_response)

    write_to_log('\nQuerying plant label endpoint for labels connected to plant center response records')
    pl_response = query_plant_label(c.pl_endpoint, pl_query_flds, pc_response)
    write_to_log('Plant label response:')
    write_to_log(json.dumps(pl_response, indent=2))
    
    write_to_log('\nGot query responses')

    # get OBJECTIDs so the DataSource field can be changed from 'ArcGIS' to 'Synced'
    pc_OIDs = get_objectIDs(pc_response)
    pm_OIDs = get_objectIDs(pm_response)
    write_to_log('Got OIDs')
    write_to_log('\tplant center: {}'.format(pc_OIDs))
    write_to_log('\tplant maintenance: {}'.format(pm_OIDs))


    fail_pc_OIDs, fail_pm_OIDs = [], []

    for block, url in c.blocks.items():
        '''
        For reference, the blocks dict from config.py is:
        blocks = {a2b.condition : api_condition_url, 
          a2b.location : api_location_url,
          a2b.measurement: api_measurement_url,
          a2b.label_need: api_labelNeed_url,
          a2b.label_has: api_labelHas_url}
        '''
        write_to_log('\nBLOCK: {}'.format(block))

        print('##################################')
        
        if block==a2b.label_has or block==a2b.label_need:
            if pl_response:
                pl_values = pl_response_to_bg_block(pl_response, c.has_label_field, c.need_label_field)
                method = 'put' if block == a2b.label_has else 'post'
                success_pcIDs, fail_pcIDs = loop_records_to_send_to_bgbase(pl_values, url, method=method)

        else:
            a2b_map = build_field_map_a2b(a2b.field_map, block)
            pc_values = arc_response_to_bg_block(pc_response, a2b.pc, a2b_map)
            pm_values = arc_response_to_bg_block(pm_response, a2b.pm, a2b_map)
            combined_values = combine_arc_response_values(pc_values, pm_values)

            
            write_to_log('\ncombined values:')
            write_to_log(json.dumps(combined_values, indent=2))
            combined_valid_values, validation_errors, error_pc_OIDs, error_pm_OIDs, required_fields = validate_arc_response_values(combined_values, block)

            fail_pc_OIDs.extend(error_pc_OIDs)
            fail_pm_OIDs.extend(error_pm_OIDs)
            for error in validation_errors:
                write_to_log(error, priority='high')

            write_to_log('\nPlantCenterIDs for upload to BG-Base - {}: {}'.format(block, list(combined_valid_values.keys())), priority='high')

            fail_pc_OIDs_block, fail_pm_OIDs_block = loop_records_to_send_to_bgbase(combined_valid_values, url, method='post')
            fail_pc_OIDs.extend(fail_pc_OIDs_block)
            fail_pm_OIDs.extend(fail_pm_OIDs_block)

        print('##################################')
    
    write_to_log('\n')
    success_pc_OIDs = [pc_OID for pc_OID in pc_OIDs if not pc_OID in fail_pc_OIDs]
    success_pm_OIDs = [pm_OID for pm_OID in pm_OIDs if not pm_OID in fail_pm_OIDs]

    if success_pc_OIDs:
        update_DataSource_field(c.pc_endpoint, success_pc_OIDs, c.arc_headers, c.new_ds)
        write_to_log('  Updating Plant Center for the following successful IDs: {}'.format(success_pc_OIDs))

    if success_pm_OIDs:
        update_DataSource_field(c.pm_endpoint, success_pm_OIDs, c.arc_headers, c.new_ds)
        write_to_log('  Updating Plant Maintenance for the following successful IDs: {}'.format(success_pm_OIDs), priority='high')

    if fail_pc_OIDs:
        write_to_log('  The following Plant Center IDs failed to update across all blocks: {}'.format(list(set(fail_pc_OIDs))), priority='high')

    if fail_pm_OIDs:
        write_to_log('  The following Plant Maintenance IDs failed to update across all blocks: {}'.format(list(set(fail_pm_OIDs))), priority='high')

    write_to_log('\n[{}] Finish'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S')), priority='high')

except Exception as e:
    msg = '[{}] ERROR\n{}'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S'), e)
    write_to_log(msg, priority='high')
