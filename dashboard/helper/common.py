import os
import sys
import time
import requests
import argparse
import ConfigParser

from datetime import datetime


PROJECTS = {'SPX': 'SPX',
            'IMX': 'IMX',
            'Galaxy': 'Galaxy',
            'Jarvis': 'Jarvis',
            'Cloud_Services': 'Sundance',
            'Cloud_to_Cloud': 'Bluffdale',
            'ShadowControl': 'ShadowControl'}


def _correct_year(date):
    '''
    corrects the year that JIRA returns
    ex.
        01/01/16 -> 01/01/2016
    '''
    split_date = date.split('/')
    tmp = split_date[2].split(' ')
    tmp[0] = '20' + tmp[0]
    split_date[2] = ' '.join(tmp)

    return '/'.join(split_date)


def _create_payload(measurement, tag, field, field_value, timestamp=None):
    '''
    Formats the payload to send to influxdb. 

    measurement: String that describes data stored in the associated fields
    tag: Value of 'project' tag key
    field: Key part of key-value pair to store metadata
    field_value: Actual data for the field key
    timestamp: Integer to specify the time the data is inserted
    '''
    if field in ('name', 'start', 'end', 'status', 'state', 'build'):
        payload = '{0},project={1} {2}="{3}" {4}'.format(measurement, tag, field, field_value, timestamp)
    else:
        payload = '{0},project={1} {2}={3} {4}'.format(measurement, tag, field, field_value, timestamp)
    return payload


def db_write(db_uri, payload):
    try:
        r = requests.post(db_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed\n")
        sys.exit(5)


def parseargs():
    '''
    CLI arguments parser
    '''
    parser = argparse.ArgumentParser(description='Options for Dashboard')

    parser.add_argument('-i', '--input-file', help='XML file to parse')
    parser.add_argument('-p', '--project', help='The Project running this script')
    parser.add_argument('-g', '--git-commits', help='Get git commits for a project', action='store_true', default=False)
    parser.add_argument('-n', '--dryrun', help='Parse file and display data without sending', action='store_true', default=False)
    parser.add_argument('-m', '--module', help='Run a specified module', nargs='?', default='all')
    parser.add_argument('-M', '--modules', help='Run a list specified modules', nargs='?', default=[])

    args = parser.parse_args()
    return args


def convert_to_datetime(jdate):
    '''
    Converts date string from JIRA to datetime object
    '''
    date = _correct_year(jdate)
    try:
        format_string = '%d/%b/%Y %I:%M %p'
        datetime_obj = datetime.strptime(date, format_string)
    except ValueError:
        format_string = '%d/%b/%Y'
        datetime_obj = datetime.strptime(date, format_string)
    return datetime_obj


def get_config():
    '''
    Gets login information from dashboar.conf
    '''
    conf = os.path.join(os.path.expanduser('~'), '.dashboard.conf')
    conf_parser = ConfigParser.ConfigParser()
    conf_parser.readfp(open(conf))

    if not conf_parser:
        print('No config file found!\nPut \'.dashboard.conf\' in home directory')
        sys.exit(3)

    return conf_parser


def parse_results(value_dict, project_key, args):
    '''
    parse the results and write to database or print the payload

    '''
    config = get_config()
    db_uri = config.get('influxdb', 'database_uri')
    tstamp = int(time.time() * 10 ** 9)
    
    for measurement,data in value_dict.iteritems():
        for field,field_val in data.iteritems():
            payload = _create_payload(measurement, project_key, field, field_val, tstamp)
            if args.dryrun:
                print(payload)
            else:
                db_write(db_uri, payload)
