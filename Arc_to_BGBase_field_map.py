# BGBase blocks
label_has = 'Label Has'
label_need = 'Label Need'
condition = 'Condition Block'
location = 'Location Block'
measurement = 'Measurement Block'

# BGBase API block names
api_name = {
  condition: 'Conditions',
  location: 'Location',
  measurement: 'Measurements'
}

# Arc tables
pm = 'pm' # Plant Maintenance
pc = 'pc' # Plant Center
pl = 'pl' # Plant Label

field_map = {
    pm : {'PlantCondition':            {'bg_fld': 'condition',
                                        'bg_block': condition,
                                        'required': True},
          'CheckDateQualifier':        {'bg_fld': 'check_dt_qual',
                                        'bg_block': condition,
                                        'required': False},
          'InspectionDate':            {'bg_fld': 'check_dt',
                                        'bg_block': condition,
                                        'required': True},
          'ReproductiveStatus':        {'bg_fld': 'reproductive',
                                        'bg_block': condition,
                                        'required': False},
          'VegetativeStatus':          {'bg_fld': 'vegetative',
                                        'bg_block': condition,
                                        'required': False},
          'Comments':                  {'bg_fld': 'check_note',
                                        'bg_block': condition,
                                        'required': False},
          'Inspector':                 {'bg_fld': 'check_by',
                                        'bg_block': condition,
                                        'required': False},
          'PlantMeasuredBy':           {'bg_fld': 'measure_by',
                                        'bg_block': measurement,
                                        'required': True},
          'PlantMeasuredDateQualifier':{'bg_fld': 'measure_dt_qual',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantMeasuredDate':         {'bg_fld': 'measure_dt',
                                        'bg_block': measurement,
                                        'required': True},
          'PlantHeightAccuracy':       {'bg_fld': 'height_accuracy',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantHeight':               {'bg_fld': 'height',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantHeightUnit':           {'bg_fld': 'height_unit',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantDBHAccuracy':          {'bg_fld': 'dbh_accuracy',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantDBH':                  {'bg_fld': 'dbh',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantDBHUnit':              {'bg_fld': 'dbh_unit',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantDBHComments':          {'bg_fld': 'dbh_misc',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantCircumference':        {'bg_fld': 'circumference',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantCrownDiameterAccuracy':{'bg_fld': 'spread_accuracy',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantCrownDiameter':        {'bg_fld': 'spread',
                                        'bg_block': measurement,
                                        'required': False},
          'PlantCrownDiameterUnit':    {'bg_fld': 'spread_unit',
                                        'bg_block': measurement,
                                        'required': False}
    },
    pc : {'PlantCondition':        {'bg_fld': 'condition',
                                    'bg_block': condition,
                                    'required': False},
          'SectionName':           {'bg_fld': 'location',
                                    'bg_block': location,
                                    'required': True},
          'ReferenceGridName':     {'bg_fld': 'grid',
                                    'bg_block': location,
                                    'required': False},
          'CoordinateSystem':      {'bg_fld': 'datum',
                                    'bg_block': location,
                                    'required': False},
          'LocationChangeType':    {'bg_fld': 'change_type',
                                    'bg_block': location,
                                    'required': False},
          'PlantDate':             {'bg_fld': 'plant_dt',
                                    'bg_block': location,
                                    'required': True},
          'PlantDateQualifier':    {'bg_fld': 'plant_dt_qual',
                                    'bg_block': location,  
                                    'required': False},                               
          'NumberOfSpecimens':     {'bg_fld': 'num_plts',
                                    'bg_block': location,
                                    'required': False},
          'XCoordinate':		       {'bg_fld': 'X_COORD',
          							            'bg_block': location,
                                    'required': False},
          'YCoordinate':		       {'bg_fld': 'Y_COORD',
          							            'bg_block': location,
                                    'required': False},
          'ZCoordinate':		       {'bg_fld': 'Z_COORD',
          							            'bg_block': location,
                                    'required': False},
          'PlantHeight':           {'bg_fld': 'height',
                                    'bg_block': measurement,
                                    'required': False},
          'PlantHeightUnit':       {'bg_fld': 'height_unit',
                                    'bg_block': measurement,
                                    'required': False},
          'PlantDBH':              {'bg_fld': 'dbh',
                                    'bg_block': measurement,
                                    'required': False},
          'PlantDBHUnit':          {'bg_fld': 'dbh_unit',
                                    'bg_block': measurement, 
                                    'required': False},                                
          'PlantCircumference':    {'bg_fld': 'circumference',
                                    'bg_block': measurement,
                                    'required': False},
          'PlantCrownDiameter':    {'bg_fld': 'spread',
                                    'bg_block': measurement,
                                    'required': False},
          'PlantCrownDiameterUnit':{'bg_fld': 'spread_unit',
                                    'bg_block': measurement, 
                                    'required': False},                               
          'PlantSex':              {'bg_fld': 'sex',
                                    'bg_block': condition,
                                    'required': False},
          'ContainerType':         {'bg_fld': 'container',
                                    'bg_block': condition,
                                    'required': False},
          'MediumType':            {'bg_fld': 'medium',
                                    'bg_block': condition,
                                    'required': False}
	},
	pl : {'HasLabelType':          {'bg_fld': 'label_have_type',
                                    'bg_block': label_has},
          'NeedLabelType':         {'bg_fld': 'label_need_type',
                                    'bg_block': label_need}
    }
}

# Geometry attributes are returned in Arc query as 'x', 'y', and 'z'. 
# 'x', 'y', and 'z' in this dictionary correspond to the key in the 
# {x:lat, y:lon, z:elev} dictionary pairs returned by an Arc query.
geom = {'x': 'x/latitude',
        'y': 'y/longitude',
        'z': 'z/elevation'}

"""ContainerType and MediumType are not used at Mount Auburn
    'PlantAccession': {'ContainerType': {'bg_fld': 'container',
                                             'bg_block': condition,
                        'MediumType':    {'bg_fld': 'medium',
                                             'bg_block': condition}}}
"""

"""PlantCondition (history) from PlantMaintenance does not need to be moved to BG Condition block.
   Since all entries in BGBase are treated as separate entries, the history is inherently stored.
          'PlantCondition':            {'bg_fld': 'condition',
                                         'bg_block': condition,
"""                                        

"""
'GlobalID':                  {'bg_fld': 'pm_globalID',
                                        'bg_block': [label, condition, measurement]},  # No location because there are no PM fields going to the Location block
'GlobalID':              {'bg_fld': 'pc_globalID',
                                    'bg_block': [condition, location, measurement]},  # No label because there are no PM fields going to the Location block
"""                                    