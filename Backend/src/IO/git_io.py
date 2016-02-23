#!/usr/bin/env python

import requests

URL = 'https://api.github.com'
OAUTH_TOKEN = '4a85521efe17ec4ef6eb4c1c76a8a097396880e1'
KEY = {'Authorization':'token '+OAUTH_TOKEN}

owner = 'decentninja'
repo = 'GitSpace'

def get_master_tree(owner, repo):
    return get_api_result('https://api.github.com/repos/'+owner+'/' + repo +'/git/trees/master?recursive=1')

def get_api_result(*args):
    response = requests.get(*args, headers=KEY)
    # if (response.status_code != requests.codes.ok):
    # Error handling TBD
    result = None
    try:
        jsondata = response.json()
    except ValueError:
        pass # out is already set for this state
    else:
        result = jsondata
    return result

print(get_master_tree(owner, repo))
