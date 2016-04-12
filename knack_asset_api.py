#!/usr/bin/python
__Author__ = 'Clay Michaels'

import requests # to hit the API
import json # to parse and construct API calls
import sqlite3 # DB to hold downloaded train car, router, cellular WAN data from API
from pprint import pprint # debug printing

APP_ID   = '<SNIPPED API APP ID>'
APP_KEY  = '<SNIPPED API APP KEY>'
BASE_URL = 'https://api.knackhq.com/v1/objects'
HEADER = { 'X-Knack-Application-Id':APP_ID,
            'X-Knack-REST-API-Key':APP_KEY }

OBJECT_DICT = {'vehicles':{'object':'object_12', 'fields':{'car_ref':'field_246',
                                                           'car_type':'field_247',
                                                           'car_id_number':'field_248', # This ISN'T the DB ID
                                                           'train_id':'field_249',
                                                           'designation':'field_250',
                                                           'fleet':'field_251',
                                                           'id':'id'}},
               'modification_record':{'object':'object_13', 'fields':{'fk_car_ref':'field_252','fk_project':'field_253', 'modification_date':'field_254','notes':'field_256'}}, # date: "08/07/2014"
               'ccu_assignment':{'object':'object_15', 'fields':{'fk_car_ref':'field_266',
                                                                 'fk_ccu_ref':'field_267'}},
               'ccu_build':{'object':'object_16', 'fields':{'firmware':'field_271',
                                                            'ccu_ip':'field_269',
                                                            'ccu_ref':'field_268',
                                                            'ccu_mac':'field_270',
                                                            'conf':'field_274',
                                                            'id':'id'}},
               'project_reference':{'object':'object_18', 'fields':{}},
               'ccu_wan':{'object':'object_20','fields':{'customer':'field_386',
                                                         'carrier':'field_387',
                                                         'ctn':'field_325',
                                                         'imei':'field_324',
                                                         'iccid':'field_463',
                                                         'wannumber':'field_317',
                                                         'wan_id':'id',
                                                         'ccu_ref':'field_414'}},}

print('START!')
db = sqlite3.connect('/home/automation/scripts/clayScripts/knack_asset_api/api_dump.db')
cursor = db.cursor()
try:
    # get CCU, Car, and assignment tables
    tables = {}
    for obj in ['ccu_assignment', 'ccu_build', 'vehicles', 'ccu_wan' ]: # 
        cursor.execute('DROP TABLE IF EXISTS %s' % (obj))
        columns = [col for col in sorted(OBJECT_DICT[obj]['fields'].keys())]
        query = 'CREATE TABLE %s (%s);' % (obj, ','.join(col for col in sorted(OBJECT_DICT[obj]['fields'].keys())))
        cursor.execute(query)
        options = '%s/%s/records' % (BASE_URL, OBJECT_DICT[obj]['object'])
        #options = '%s/%s/records' % (BASE_URL, OBJECT_DICT[obj]['object']) # for getting records on a new object
        #options = '%s/%s/fields' % (BASE_URL, OBJECT_DICT[obj]['object']) # for getting fields on a new object
        parameters = {'rows_per_page': '5000'}
        r = requests.get(options, headers=HEADER, params=parameters)
        #print(r.url)
        #pprint(json.loads(r.text)['records'])
        #pprint(json.loads(r.text)['fields'])
        #pprint(columns)
        for record in json.loads(r.text)['records']:
            row = []
            for key, value in sorted(OBJECT_DICT[obj]['fields'].items()):
                try:
                    row.append(str(record[OBJECT_DICT[obj]['fields'][key] + '_raw'][0]['identifier']))
                except:
                    try:
                        row.append(str(record[OBJECT_DICT[obj]['fields'][key] + '_raw']['url'].replace('http://','')))
                    except:
                        row.append(str(record[OBJECT_DICT[obj]['fields'][key]]))
            #pprint(row)
            query = 'INSERT INTO %s (%s) VALUES ("%s")' % (obj, ','.join(columns), '","'.join(row))
            #print(query)
            cursor.execute(query)
        #pprint(cursor.execute('select * from %s' % (obj)).fetchall())
    db.commit()
    db.close()
except ValueError:
    print('REQUEST ERROR!')
    print('HTTP status code:%s' % (r.status_code))
    print('HTTP error:%s' % (r.text))
except Exception as error:
    print('ERROR:%s' % (error))
    try:
        pprint(row)
    except NameError:
        pass
    try:
        print(query)
    except NameError:
        pass

print('DONE!')
