import json
import queue
import select
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

id_mappings = {'gitspace' : {'owner' : 'decentninja', 'repo' : 'GitSpace'}}

clients = {}

mock_json = {'hello' : 'hi'}

class Main():
    def __init__(self):
        self.clients = {}
        self.states = {}
        self.init_states()
        self.init_frontend()
        self.init_app()

    def init_states(self):
        for key in id_mappings:
            self.states[key], _ = git.get_init(id_mappings[key]['owner'],
                                               id_mappings[key]['repo'])

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
        self.clients[client_id] = [c for c in self.clients[client_id] if self.send(c, json_obj)]

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
                message = json.loads(message)
                print(message)
            except queue.Empty:
                return

    def init_client(self, new_client, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = []
        self.clients[client_id].append(new_client)
        print(self.states[client_id], file=sys.stderr)
        self.send(new_client, self.states[client_id])

    def close(self):
        self.app_server.join()

    def main(self):
        print('Server is up and running!', file=sys.stderr)
        try:
            while 1:
                self.find_clients()
                self.send_webhook_updates()
                self.read_app_commands()
                #time.sleep(1)
        except KeyboardInterrupt:
            self.close()

if __name__ == '__main__':
    main = Main()
    main.main()
