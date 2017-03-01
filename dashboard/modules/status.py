'''
Take a python coverage xml file or py.test junit xml file and upload stats to influxdb

Functions used from https://gitlab.com/gigyas/status
'''
from __future__ import print_function, absolute_import
import xml.etree.ElementTree as ET

from dashboard.helper import common


def _parse_xml(xml_tree):
    '''
    Parses xml
    '''
    xml_results = ET.parse(xml_tree)
    return xml_results


def coverage(xml_tree):
    '''
    Parse the xml to get the coverage stats
    '''
    if ET.iselement(xml_tree):
        cov_node = xml_tree
    else:
        cov_node = xml_tree.getroot()

    if cov_node.tag != 'coverage':
        raise ValueError('Input is not valid coverage xml')

    total_coverage = float(cov_node.get('line-rate')) * 100

    lines = cov_node.findall('.//class//line[@hits]')
    hits = []
    misses = []
    for line in lines:
        if int(line.get('hits')) > 0:
            hits.append(line)
        else:
            misses.append(line)

    coverage = {'coverage': total_coverage, 'total_lines': len(lines), 'hits': len(hits), 'misses': len(misses)}
    return coverage


def junit(xml_tree):
    '''
    Parse a py.test JUnit xml and return stats
    '''
    root = xml_tree.getroot()

    if root.tag == 'testsuite':
        test_suites = [root]
    else:
        test_suites = root.findall('.//testsuite')

    for test_suite in test_suites:
        total = test_suite.get('tests')
        errors = test_suite.get('errors')
        failures = test_suite.get('failures')
        skips = test_suite.get('skips')
        duration = test_suite.get('time')
        passing = int(total) - int(errors) - int(failures) - int(skips)

    testresult = {'total': total, 'passing': passing, 'failures': failures, 'errors': errors, 'skips': skips, 'duration': duration}
    return testresult


def parse(xml_tree):
    '''
    Return proper coverage (xml) or junit results
    '''
    tree = ET.parse(xml_tree)
    root = tree.getroot()
    
    coverage_or_junit = {}

    if root.tag  == 'coverage':
        coverage_or_junit = coverage(tree)
    else:
        root.tag == "testsuite" or root.tag == ".//testsuite"
        coverage_or_junit = junit(tree)
    return coverage_or_junit


def run(args):
    '''
    Run coverage functions
    '''
    print('** Status module **')
    coverage_values = {}

    for proj_key,proj_name in common.PROJECTS.iteritems():
        if args.input_file and args.project == proj_name:
            xml = args.input_file
            results = parse(xml)
            if 'coverage' in results:
                coverage_values['coverage'] = results
            else:
                coverage_values['test_results'] = results

            common.parse_results(coverage_values, proj_key, args)

