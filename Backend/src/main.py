#!/usr/bin/env python

import IO.json_sockets as js
import IO.git_io as git

TCP_IP_FRONTEND = '127.0.0.1'
TCP_PORT_FRONTEND = 5522

owner = 'decentninja'
repo = 'GitSpace'

class Main():
    def __init__(self):
        self.frontend_client = js.Client(TCP_IP_FRONTEND, TCP_PORT_FRONTEND)

    def send_state_and_updates_frontend(self, state, updates):
        self.frontend_client.send_JSON(state)
        [self.frontend_client.send_JSON(update) for update in updates]

    def on_close(self):
        self.frontend_client.close()

    def main_loop(self):
        self.state, self.updates = git.get_init(owner, repo)
        self.send_state_and_updates_frontend(self.state, self.updates)

        # Listen to controller and do fun things

        # Until we decide to exit

        self.on_close()

if __name__ == '__main__':
    main = Main()
    main.main_loop()
