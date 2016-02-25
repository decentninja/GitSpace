#!/usr/bin/env python

import json
import socket

class Client():
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))

    def send_JSON(self, json_obj):
        json_string = '\x02' + json.dumps(json_obj) + '\x03'
        self.socket.send(json_string.encode('utf-8'))

    def close(self):
        self.socket.close()
