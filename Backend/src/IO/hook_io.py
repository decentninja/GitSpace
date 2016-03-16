from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Queue
import IO.git_parsing
import json
import socketserver
import requests
import os
import sys

IP = '0.0.0.0'
PORT = 5000


# A bad solution to HookRequestHandler being a meta-class
# I don't know how to reach anything outside the instance of
# HookRequestHandler. So I use a global. God have mercy on my soul.
global hook_queue

def get_name_from_hook(hook):
    return hook['repository']['full_name']

class HookRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        print("Hook recieved")
        length = int(self.headers['Content-Length'])
        text = self.rfile.read(length).decode('utf-8')
        post_data = json.loads(text)[0]
        update = git_parsing.hook_to_updates(post_data)
        repo = get_name_from_hook(post_data)
        self_set_headers()
        hook_queue.put(repo, update)
        # You now have a dictionary of the post data

def new_hook_client(queue):
    Handler = HookRequestHandler

    httpd = socketserver.TCPServer(("", PORT), Handler)
    hook_queue = queue
    #hook_dicts[name.split('/')[-1]] = queue
    print("Hook server up at:", PORT)
    httpd.serve_forever()

if __name__ == '__main__':
    import time
    from multiprocessing import Process, Queue
    #new_hook_client(Queue())
    text = '{"ref":"refs/heads/master","before":"1aa745421cffe8c709cd3804de25c52db225b35d","after":"c451ea8ffd816ffa7341ea4c4ec515355b969e42","created":false,"deleted":false,"forced":false,"base_ref":null,"compare":"https://github.com/decentninja/GitSpace/compare/1aa745421cff...c451ea8ffd81","commits":[{"id":"c451ea8ffd816ffa7341ea4c4ec515355b969e42","distinct":true,"message":"mock push\\n\\nSigned-off-by: Zercha <david.maskoo@gmail.com>","timestamp":"2016-03-16T16:27:20+01:00","url":"https://github.com/decentninja/GitSpace/commit/c451ea8ffd816ffa7341ea4c4ec515355b969e42","author":{"name":"Zercha","email":"david.maskoo@gmail.com","username":"Zercha"},"committer":{"name":"Zercha","email":"david.maskoo@gmail.com","username":"Zercha"},"added":[],"removed":[],"modified":["Backend/src/IO/git_io.py"]}],"head_commit":{"id":"c451ea8ffd816ffa7341ea4c4ec515355b969e42","distinct":true,"message":"mock push\\n\\nSigned-off-by: Zercha <david.maskoo@gmail.com>","timestamp":"2016-03-16T16:27:20+01:00","url":"https://github.com/decentninja/GitSpace/commit/c451ea8ffd816ffa7341ea4c4ec515355b969e42","author":{"name":"Zercha","email":"david.maskoo@gmail.com","username":"Zercha"},"committer":{"name":"Zercha","email":"david.maskoo@gmail.com","username":"Zercha"},"added":[],"removed":[],"modified":["Backend/src/IO/git_io.py"]},"repository":{"id":52084130,"name":"GitSpace","full_name":"decentninja/GitSpace","owner":{"name":"decentninja","email":"very@decent.ninja"},"private":true,"html_url":"https://github.com/decentninja/GitSpace","description":"","fork":false,"url":"https://github.com/decentninja/GitSpace","forks_url":"https://api.github.com/repos/decentninja/GitSpace/forks","keys_url":"https://api.github.com/repos/decentninja/GitSpace/keys{/key_id}","collaborators_url":"https://api.github.com/repos/decentninja/GitSpace/collaborators{/collaborator}","teams_url":"https://api.github.com/repos/decentninja/GitSpace/teams","hooks_url":"https://api.github.com/repos/decentninja/GitSpace/hooks","issue_events_url":"https://api.github.com/repos/decentninja/GitSpace/issues/events{/number}","events_url":"https://api.github.com/repos/decentninja/GitSpace/events","assignees_url":"https://api.github.com/repos/decentninja/GitSpace/assignees{/user}","branches_url":"https://api.github.com/repos/decentninja/GitSpace/branches{/branch}","tags_url":"https://api.github.com/repos/decentninja/GitSpace/tags","blobs_url":"https://api.github.com/repos/decentninja/GitSpace/git/blobs{/sha}","git_tags_url":"https://api.github.com/repos/decentninja/GitSpace/git/tags{/sha}","git_refs_url":"https://api.github.com/repos/decentninja/GitSpace/git/refs{/sha}","trees_url":"https://api.github.com/repos/decentninja/GitSpace/git/trees{/sha}","statuses_url":"https://api.github.com/repos/decentninja/GitSpace/statuses/{sha}","languages_url":"https://api.github.com/repos/decentninja/GitSpace/languages","stargazers_url":"https://api.github.com/repos/decentninja/GitSpace/stargazers","contributors_url":"https://api.github.com/repos/decentninja/GitSpace/contributors","subscribers_url":"https://api.github.com/repos/decentninja/GitSpace/subscribers","subscription_url":"https://api.github.com/repos/decentninja/GitSpace/subscription","commits_url":"https://api.github.com/repos/decentninja/GitSpace/commits{/sha}","git_commits_url":"https://api.github.com/repos/decentninja/GitSpace/git/commits{/sha}","comments_url":"https://api.github.com/repos/decentninja/GitSpace/comments{/number}","issue_comment_url":"https://api.github.com/repos/decentninja/GitSpace/issues/comments{/number}","contents_url":"https://api.github.com/repos/decentninja/GitSpace/contents/{+path}","compare_url":"https://api.github.com/repos/decentninja/GitSpace/compare/{base}...{head}","merges_url":"https://api.github.com/repos/decentninja/GitSpace/merges","archive_url":"https://api.github.com/repos/decentninja/GitSpace/{archive_format}{/ref}","downloads_url":"https://api.github.com/repos/decentninja/GitSpace/downloads","issues_url":"https://api.github.com/repos/decentninja/GitSpace/issues{/number}","pulls_url":"https://api.github.com/repos/decentninja/GitSpace/pulls{/number}","milestones_url":"https://api.github.com/repos/decentninja/GitSpace/milestones{/number}","notifications_url":"https://api.github.com/repos/decentninja/GitSpace/notifications{?since,all,participating}","labels_url":"https://api.github.com/repos/decentninja/GitSpace/labels{/name}","releases_url":"https://api.github.com/repos/decentninja/GitSpace/releases{/id}","deployments_url":"https://api.github.com/repos/decentninja/GitSpace/deployments","created_at":1455882237,"updated_at":"2016-02-25T17:36:56Z","pushed_at":1458142042,"git_url":"git://github.com/decentninja/GitSpace.git","ssh_url":"git@github.com:decentninja/GitSpace.git","clone_url":"https://github.com/decentninja/GitSpace.git","svn_url":"https://github.com/decentninja/GitSpace","homepage":null,"size":23018,"stargazers_count":0,"watchers_count":0,"language":"C#","has_issues":true,"has_downloads":true,"has_wiki":true,"has_pages":false,"forks_count":0,"mirror_url":null,"open_issues_count":0,"forks":0,"open_issues":0,"watchers":0,"default_branch":"master","stargazers":0,"master_branch":"master"},"pusher":{"name":"Zercha","email":"david.maskoo@gmail.com"},"sender":{"login":"Zercha","id":4265058,"avatar_url":"https://avatars.githubusercontent.com/u/4265058?v=3","gravatar_id":"","url":"https://api.github.com/users/Zercha","html_url":"https://github.com/Zercha","followers_url":"https://api.github.com/users/Zercha/followers","following_url":"https://api.github.com/users/Zercha/following{/other_user}","gists_url":"https://api.github.com/users/Zercha/gists{/gist_id}","starred_url":"https://api.github.com/users/Zercha/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/Zercha/subscriptions","organizations_url":"https://api.github.com/users/Zercha/orgs","repos_url":"https://api.github.com/users/Zercha/repos","events_url":"https://api.github.com/users/Zercha/events{/privacy}","received_events_url":"https://api.github.com/users/Zercha/received_events","type":"User","site_admin":false}}'
    post_data = json.loads(text)
    print(get_name_from_hook(post_data))
    print(git_parsing.hook_to_updates(post_data))
