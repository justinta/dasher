
from __future__ import print_function, absolute_import
import os
import git
import json

from dashboard.helper import common

GIT_REPO_DIR = os.path.abspath(os.getcwd())


def git_log():
    '''
    parses git log
    '''
    g = git.Git(GIT_REPO_DIR)
    log = g.log('--numstat', '--pretty=format:COMMIT%n{"timestamp": %ct}')

    commits = []
    commit = {}

    for com in log.split('COMMIT'):
        for line in com.split('\n'):
            if 'timestamp' in line:
                commit = json.loads(line)
                commit['insertions'] = 0
                commit['deletions'] = 0
                commit['files_changed'] = 0
            elif line not in (u'', '\n'):
                line = line.split('\t')
                commit['insertions'] += int(line[0])
                commit['deletions'] += int(line[1])
                commit['files_changed'] += 1
            else:
                pass
        if not commit:
            pass
        else:
            commits.append(commit)

    return commits


def get_commits(db_uri, proj_name, args):
    log = git_log()

    for commit in log:
        timestamp = commit['timestamp']
        for commit_key,commit_value in commit.iteritems():
            if commit_key == 'timestamp':
                continue
            else:
                payload = common._create_payload('git_commit', proj_name, commit_key, commit_value, timestamp)
                if args.dryrun:
                    print(payload)
                else:
                    common.db_write(db_uri, payload)

def run(args):
    '''
    Run bitbucket functions
    '''
    if args.git_commits:
        print('** Bitbucket module **')
        config = common.get_config()
        db_uri = config.get('influxdb', 'database_uri')

        for proj_key,proj_name in common.PROJECTS.iteritems():
            get_commits(db_uri, proj_name, args)
    else:
        return
