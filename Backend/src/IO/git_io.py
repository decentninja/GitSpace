#!/usr/bin/env python
'''
TODO-list:
- I don't really like the passing around of owner+repo, but we will probably
  need to handle several repos, so it's there for now.
- Getting details on every commit takes a good while even for out little repo,
  since it's an HTTP request each. We may have to deal with load times being
  a bit slow. We should send the updates one by one in a later iteration.
'''

import datetime
import requests
import git_parsing

# Should stay rather constant
GIT_URL = 'https://api.github.com'
OAUTH_TOKEN = '4a85521efe17ec4ef6eb4c1c76a8a097396880e1'
KEY = {'Authorization':'token '+OAUTH_TOKEN}

# Number of days to look back for realtime, set to 1 week or 3 weeks
# (But our repo isn't that old yet)
lookback_days = 13

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

def get_full_commitinfo(owner, repo, commit):
    return get_api_result('https://api.github.com/repos/'+owner+'/' + repo +\
        '/commits/' + commit['sha'])

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
        datetime.datetime.now() - datetime.timedelta(days=lookback_days),
        datetime.datetime.now())

def get_init(owner, repo):
    state = get_init_state(owner, repo)
    updates = [get_full_commitinfo(owner, repo, c) for c in
        get_init_commits(owner, repo)]
    state_parsed = git_parsing.parse_raw_state(state)
    update_parsed = git_parsing.parse_raw_updates(updates)
    return state_parsed, updates

if __name__ == '__main__':
    owner = 'decentninja'
    repo = 'GitSpace'
    get_init(owner, repo)
