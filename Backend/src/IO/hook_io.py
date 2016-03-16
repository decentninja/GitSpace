from http.server import BaseHTTPRequestHandler, HTTPServer
import git_parsing
import json
import socketserver
import requests
import os
import sys

IP = '0.0.0.0'
PORT = 5000
hook_dicts = {}

def get_name_from_hook(hook):
    pass


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
        length = int(self.headers['Content-Length'])
        text = str(self.rfile.read(length))
        print(text)
        with open('hook_example','w+') as f:
            print(text,file=f)
        post_data = json.loads(text)[0]
        git_parsing.hook_to_updates(post_data)
        self_set_headers()
        # You now have a dictionary of the post data

def new_hook_client(queue):
    PORT = 5000

    Handler = HookRequestHandler

    httpd = socketserver.TCPServer(("", PORT), Handler)

    print("Hook server up at:", PORT)
    httpd.serve_forever()

if __name__ == '__main__':
    import time
    from multiprocessing import Process, Queue
    new_hook_client(Queue())