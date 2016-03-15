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
from repository import Repository
from multiprocessing import Process, Queue

TCP_IP = '0.0.0.0'
TCP_PORT = 5522
BUFFER_SIZE = 1024
DEBUG = False

id_mappings = {'gitspace' : ['decentninja/GitSpace']}

mock_json = {'hello' : 'hi'}

mock_repos = {"decentninja/GitSpace" : {"repo": "GitSpace"},
              "tilatequila/MySpace" : {"repo": "MySpace"}}

def command_json():
    command = {}
    command['api version'] = 1
    command['type'] = 'command'
    return command

class Main():
    def __init__(self, testing = False):
        self.testing = testing
        self.clients = {}
        self.states = {}
        self.init_states()
        print("Revolution complete");
        self.init_frontend()
        print("Final frontier reached");
        self.init_app()
        print("Mainframe activated");

    def init_state(self, client, repo):
        if client not in self.states:
            self.states[client] = {}
        if self.testing:
            self.states[client][repo] = Repository(repo, lookback=1)
        else:
            self.states[client][repo] = Repository(repo)

    def init_states(self):
        for client in id_mappings:
            for repo in id_mappings[client]:
                self.init_state(client, repo)

    def init_frontend(self):
        self.frontend_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.frontend_server.bind((TCP_IP, TCP_PORT))
        self.frontend_server.listen(5)

    def init_app(self):
        self.app_queue = Queue()
        self.app_queue_out = Queue()
        self.app_server = Process(target= app.serve, args=(self.app_queue, self.app_queue_out))
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
            client_id = new_client.recv(1024).decode("utf-8")
            self.init_client(new_client, client_id)

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
            except (KeyError, ValueError):
                print('Received malformed JSON from app.', file=sys.stderr)
                self.app_queue_out.put('internal')
                return
            self.execute_app_command(message, client)

    def execute_app_command(self, message, client):
        try:
            if message['command'] in ['labels', 'repo focus','reset camera',
                                      'activity threshold']:
                json = command_json()
                json['command'] = message['command']
                if message['command'] == 'repo focus':
                    if message['repo'] not in self.states[client]:
                        print("Repo does not exist: %s"%message['repo'], file=sys.stderr)
                        self.app_queue_out.put('internal')
                        return
                    json['repo'] = message['repo']
                elif message['command'] == 'labels':
                    json['labels'] = message['show']
                elif message['command'] == 'activity threshold':
                    json['threshold'] = message['threshold']
                self.send_all(client, json)
                self.app_queue_out.put('internal')
            elif message['command'] == 'repo delete':
                self.delete_repo(message['repo'], client)
            elif message['command'] == 'repo add':
                self.add_repo(message['repo'], client)
            elif message['command'] == 'user activity':
                #self.send_all(client, self.states[client][message['repo']].\
                #        get_user_update(message['username']))
                self.app_queue_out.put('internal')
            elif message['command'] == 'internal_state':
                self.app_queue_out.put(self.make_app_state(client))
        except KeyError as e:
            print('Received malformed JSON from app.', e,file=sys.stderr)
            self.app_queue_out.put('internal')

    def add_repo(self, repo, client):
        # This requires valid repo name.
        self.init_state(client, repo)
        self.send_all(client, self.states[client][repo].get_latest_state())
        self.app_queue_out.put(self.make_app_state(client))

    def delete_repo(self, repo, client):
        if repo not in self.states[client]:
            print("Repo does not exist: %s"%repo, file=sys.stderr)
            return
        del self.states[client][repo]
        command = {}
        command['api version'] = 1
        command['type'] = 'delete'
        command['repo'] = repo
        self.send_all(client, command)
        self.app_queue_out.put(self.make_app_state(client))

    def make_app_state(self, client):
        json_list = []
        for client in self.states:
            for repo in self.states[client]:
                json_list.append(self.states[client][repo].comm_format())
        return json.dumps({"data": json_list}, ensure_ascii=False)

    def init_client(self, new_client, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = []
        self.clients[client_id].append(new_client)
        [self.send(new_client, self.states[client_id][repo].get_latest_state())
                for repo in self.states[client_id]]

    def close(self):
        self.frontend_server.close()
        self.app_queue.close()
        self.app_queue_out.close()
        self.app_server.terminate()
        self.app_server.join()
        print('Server shut down.')

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
