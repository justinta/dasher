'''
Get data from sonarqube to put into grafana dashboard

TODO: Add some mapping for projects and project keys in sonarqube
'''
from __future__ import print_function, absolute_import
import requests

from dashboard.helper import common

PROJECT_MAP = {'SPX develop': 'SPX',
               'IMX': 'IMX',
               'jarvis develop': 'Jarvis',
               'sundance-api develop': 'Sundance'}


def sonar(api_call, payload={}):
    '''
    Return results from api query
    '''
    req = requests.get('http://10.30.20.123:9000/api/{0}'.format(api_call), params=payload, auth=('admin', 'admin'))
    return req.json()


def get_projectkey(proj_name):
    '''
    gets projects from sonarqube
    '''
    func = 'projects/index'
    projects = sonar(func)

    develop = False
    project_key = None

    for project in projects:
        try:
            split_proj = project['k'].split(':')
            branch = split_proj[2]
            name = split_proj[1]

            if branch.startswith('hotfix') or branch.startswith('release'):
                if name == proj_name.lower():
                    develop = False
                    return project['k']
            elif branch == 'develop':
                if name == proj_name.lower():
                    develop = True
                    project_key = project['k']

        except (KeyError, IndexError):
            continue

    if develop:
        return project_key

    return False


def get_loc(proj_name):
    '''
    Gets the lines of code
    '''
    component_key = get_projectkey(proj_name)

    if component_key:
        func = 'measures/component'
        payload = {'componentKey': component_key, 'metricKeys': 'ncloc'}
        res = sonar(func, payload)

        try:
            value = res['component']['measures'][0]['value']
            return {'loc': value}
        except IndexError:
            return {}

    else:
        return {}


def watermark(proj_name):
    ''' 
    Get QualityGate (watermark) from sonarqube given a project name
    '''
    func = 'qualitygates/project_status'
    project_key = get_projectkey(proj_name)

    if project_key:
        payload = {'projectKey': project_key}
        res = sonar(func, payload)
    else:
        return {}

    ret = res['projectStatus']['status']
    if ret == 'OK':
        ret = 'Passed'
    elif ret == 'ERROR':
        ret = 'Failed'
    return {'status': ret}
    

def run(args):
    '''
    Run sonarqube functions
    '''
    print('** Sonarqube Module **')
    sonar_values = {}

    for proj_key,proj_name in common.PROJECTS.iteritems():
        sonar_values['loc'] = get_loc(proj_name)
        sonar_values['watermark'] = watermark(proj_name)

        common.parse_results(sonar_values, proj_key, args)

