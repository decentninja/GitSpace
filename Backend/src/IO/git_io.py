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
import IO.git_parsing as git_parsing

# Should stay rather constant
GIT_URL = 'https://api.github.com'
OAUTH_TOKEN = '4a85521efe17ec4ef6eb4c1c76a8a097396880e1'
KEY = {'Authorization':'token '+OAUTH_TOKEN}

# Number of days to look back for realtime, set to 1 week or 3 weeks
# (But our repo isn't that old yet)
lookback_days = 20

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
        if int(response.headers.get('X-RateLimit-Remaining')) < 3000:
            print('WARNING Rate Limit:',response.headers.get('X-RateLimit-Remaining'))
    return result

def get_tree(repo, sha):
    return get_api_result('https://api.github.com/repos/'+ repo +\
        '/git/trees/'+ sha +'?recursive=1')

def get_commits_in_span(repo, since, until):
    commits = []
    last_sha = 'none'
    while True:
        params = {'since': since.isoformat(),
                  'until': until.isoformat()}
        new_commits = (get_api_result('https://api.github.com/repos/' + repo +\
                '/commits',params=params))
        if len(new_commits) == 0:
            break
        earliest = new_commits[-1]
        sha = new_commits[-1]['sha']
        if sha == last_sha:
            break
        last_sha = sha
        time = git_parsing.parse_git_time_format(earliest['commit']['committer']['date'])
        date = datetime.datetime.fromtimestamp(time)
        if len(commits) > 0:
            if new_commits[0]['sha'] ==\
                  commits[-1]['sha']:
                new_commits=new_commits[1:]
        commits+=new_commits
        until = date
    return commits


def get_full_commitinfo(repo, commit):
    return get_api_result('https://api.github.com/repos/'+ repo +\
        '/commits/' + commit['sha'])

def find_most_recent_sha(repo, start_date):
    backoff = 1
    commits = []
    since = start_date - datetime.timedelta(days=backoff)
    commits = get_commits_in_span(repo, since, start_date)
    while (not commits):
        since -= datetime.timedelta(days=backoff)
        backoff *= 2
        commits = get_commits_in_span(repo, since, start_date)
    return (commits[0]['sha'],commits[0]['commit']['committer']['date'])

def get_init_state(repo, time_now):
    # Get sha for a state 1 week+ ago
    sha,time = find_most_recent_sha(repo,
        time_now - datetime.timedelta(days=lookback_days))
    # Get the associated tree
    return get_tree(repo, sha),time

def get_init_commits(repo, time_now):
    commits = get_commits_in_span(repo,
        time_now - datetime.timedelta(days=lookback_days),
        time_now)
    return commits

def get_init(repo):
    time_now = datetime.datetime.now()
    state,time = get_init_state(repo,time_now)
    updates = [get_full_commitinfo(repo, c) for c in
        get_init_commits(repo, time_now)]
    state_parsed = git_parsing.parse_raw_state(state,time = time, name=repo)
    #updates arrive in reversed order
    update_parsed = git_parsing.parse_raw_updates(updates[::-1])
    return git_parsing.update_state(state_parsed,update_parsed), update_parsed

if __name__ == '__main__':
    repo = 'decentninja/GitSpace'
    state,updates = get_init(repo)
