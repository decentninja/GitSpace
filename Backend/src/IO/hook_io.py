from http.server import BaseHTTPRequestHandler, HTTPServer
import git_parsing
import urllib
import socketserver
import requests
import os
import sys

IP = '0.0.0.0'
PORT = 5000

class HookRequestHandler(BaseHTTPRequestHandler):
    def __init__(self,queue):
        self.queue = queue
        super().__init__()

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
        text = self.rfile.read(length).decode('utf-8')
        with open('hook_example','w+') as f:
            print(text,file=f)
        post_data = urllib.parse.parse_qs(text)
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