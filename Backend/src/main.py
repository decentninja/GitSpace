# TODO: Split this class up (I guess p4)
import json
import queue
import select
import signal
import socket
import sys
import time
import IO.git_io as git
import IO.app_io as app
from multiprocessing import Process, Queue

TCP_IP = '127.0.0.1'
TCP_PORT = 5522
BUFFER_SIZE = 1024
DEBUG = False

id_mappings = {'gitspace' : {'GitSpace' : 'decentninja'}}

mock_json = {'hello' : 'hi'}

mock_repos = {"GitSpace" : {"repo": "GitSpace"},
              "MySpace" : {"repo": "MySpace"}}

def command_json():
    command = {}
    command['api version'] = 1
    command['type'] = 'command'
    return command

class Main():
    def __init__(self, testing = False):
        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)
        self.testing = testing
        self.clients = {}
        self.states = {}
        self.init_states()
        self.init_frontend()
        self.init_app()

    def init_state(self, client, repo, owner):
        if client not in self.states:
            self.states[client] = {}
        if self.testing:
            self.states[client][repo] = mock_repos[repo]
        else:
            self.states[client][repo], _ = \
                    git.get_init(owner, repo)

    def init_states(self):
        for client in id_mappings:
            for repo in id_mappings[client]:
                self.init_state(client, repo, id_mappings[client][repo])

    def init_frontend(self):
        self.frontend_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.frontend_server.bind((TCP_IP, TCP_PORT))
        self.frontend_server.listen(5)

    def init_app(self):
        self.app_queue = Queue()
        self.app_server = Process(target= app.serve, args=(self.app_queue,))
        self.app_server.start()

    def send(self, conn, json_obj):
      json_string = '\x02' + json.dumps(json_obj) + '\x03'
      try:
        conn.sendall(json_string.encode('utf-8'))
        return True
      except socket.error as msg:
        conn.close()
        return False

    def send_all(self, client_id, json_obj):
        if client_id in self.clients:
            self.clients[client_id] = \
                    [c for c in self.clients[client_id] if self.send(c, json_obj)]

    def find_clients(self):
        readable, writable, errored = select.select([self.frontend_server], [], [], 1)
        for s in readable:
            new_client, address = s.accept()
            # client_id = new_client.recv() We could receive an id att conn.
            self.init_client(new_client, 'gitspace')

    def send_webhook_updates(self):
        # For now sends cute mock JSONs in Debug mode.
        if len (self.clients) > 0 and len(self.clients['gitspace']) > 0 and DEBUG:
            self.send_all('gitspace', mock_json)
            print('sending mock')

    def read_app_commands(self):
        while 1:
            try:
                message, client = self.app_queue.get_nowait()
            except queue.Empty:
                return
            try:
                message = json.loads(message)
                message = message['message']
            except ValueError:
                raise Exception('Received malformed JSON from app.')
            self.execute_app_command(message, client)

    def execute_app_command(self, message, client):
        print(message)
        try:
            if message['command'] in ['labels', 'repo focus','reset camera',
                                      'activity threshold']:
                json = command_json()
                json['command'] = message['command']
                if message['command'] == 'repo focus':
                    if message['repo'] not in self.states[client]:
                        raise Exception("Repo does not exist: %s"%repo)
                    json['repo'] = message['repo']
                elif message['command'] == 'labels':
                    json['labels'] = True
                elif message['command'] == 'activity threshold':
                    json['threshold'] = message['threshold']
                self.send_all(client, json)
            elif message['command'] == 'repo delete':
                self.delete_repo(message['repo'], client)
            elif message['command'] == 'repo add':
                self.add_repo(message['repo'], message['owner'], client)
        except KeyError:
            raise Exception('Received malformed JSON from app.')

    def add_repo(self, repo, owner, client):
        # This requires valid repo name.
        self.init_state(client, repo, owner)
        self.send_all(client, self.states[client][repo])

    def delete_repo(self, repo, client):
        if repo not in self.states[client]:
            raise Exception("Repo does not exist: %s"%repo)
        del self.states[client][repo]
        command = {}
        command['api version'] = 1
        command['type'] = 'delete'
        command['repo'] = repo
        self.send_all(client, command)

    def init_client(self, new_client, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = []
        self.clients[client_id].append(new_client)
        [self.send(new_client, self.states[client_id][repo])
                for repo in self.states[client_id]]

    def close(self):
        self.app_server.terminate()
        self.app_server.join()

    def main(self):
        try:
            while 1:
                self.find_clients()
                self.send_webhook_updates()
                self.read_app_commands()
                #time.sleep(1)
        except KeyboardInterrupt:
            self.close()

if __name__ == '__main__':
    print('Starting server...', file=sys.stderr)
    main = Main()
    print('Server is up and running!', file=sys.stderr)
    main.main()
