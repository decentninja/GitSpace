#!/usr/bin/env python

import datetime
import requests

# Should stay rather constant
GIT_URL = 'https://api.github.com'
OAUTH_TOKEN = '4a85521efe17ec4ef6eb4c1c76a8a097396880e1'
KEY = {'Authorization':'token '+OAUTH_TOKEN}

# Just examples for now
owner = 'decentninja'
repo = 'GitSpace'
sha = 'master'

# Days to look back for realtime, set to 1 week or 3 weeks (But our repo isn't that old yet)
lookback_days = 3

def get_api_result(*args, **kwargs):
    response = requests.get(*args, headers=KEY, **kwargs)
    if (response.status_code != requests.codes.ok):
        # Error handling TBD
        print('Not OK!')
    result = None
    try:
        jsondata = response.json()
    except ValueError:
        pass # out is already set for this state
    else:
        result = jsondata
    return result

def get_tree(owner, repo, sha):
    return get_api_result('https://api.github.com/repos/'+owner+'/' + repo +\
        '/git/trees/'+ sha +'?recursive=1')

def get_commits_in_span(owner, repo, since, until):
    params = {'since': since.isoformat(),
              'until': until.isoformat()}
    return get_api_result('https://api.github.com/repos/'+owner+'/' + repo +\
        '/commits', params=params)

def find_most_recent_sha(owner, repo, start_date):
    backoff = 1
    commits = []
    since = start_date - datetime.timedelta(days=1)
    commits = get_commits_in_span(owner, repo, since, start_date)
    while (not commits):
        since -= datetime.timedelta(days=backoff)
        backoff *= 2
        commits = get_commits_in_span(owner, repo, since, start_date)
    return commits[0]['sha']

def get_init_state(owner, repo):
    # Get sha for a state 1 week+ ago
    sha = find_most_recent_sha(owner, repo,
        datetime.datetime.now() - datetime.timedelta(days=lookback_days))
    # Get the associated tree
    return get_tree(owner, repo, sha)

def get_init_commits(owner, repo):
    return get_commits_in_span(owner, repo,
        datetime.datetime.now() - datetime.timedelta(days=lookback_days), datetime.datetime.now())

def get_init(owner, repo):
    state = get_init_state(owner, repo)
    updates = get_init_commits(owner, repo)
    # TODO: Parse info to prettier JSON format
    # state, updates = parser.parse_tree_and_commits(state, updates)
    return state, updates

print(get_init(owner, repo))
