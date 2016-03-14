from main import Main
from multiprocessing import Process
from websocket import create_connection

import json
import time
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5522
BUFFER_SIZE = 10000

mock_repos = {"GitSpace" : {"repo": "GitSpace"},
              "MySpace" : {"repo": "MySpace"}}

mock_setup_json = "{'name': 'GitSpace', 'users': 'powie'}"

def json_bytes(json_obj):
    return 'b\'\\x02' + json.dumps(json_obj) + '\\x03\''

def frontend_json(string):
    j_string = string.strip('b\'\\x02').strip('\\x03\'')
    return json.loads(j_string)

def start_server():
    server = Main(testing = True)
    server.main()

try:
    # Start the server
    server = Process(target= start_server)
    server.start()

    # Give server a second or two
    time.sleep(2)

    # Set up connection with frontend
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    setup_state = str(s.recv(BUFFER_SIZE))
    assert frontend_json(setup_state) == mock_repos["GitSpace"], 'Faulty setup state to Frontend.'

    # Connect with app
    ws = create_connection("ws://localhost:8080/websocket")
    result =  ws.recv()
    assert result == mock_setup_json, 'Faulty setup state to app.'

    # Test labels command
    ws.send('{"command": "labels"}')
    response = str(s.recv(BUFFER_SIZE))
    expected = {"api version": 1, "type": "command", "command": "labels", "labels": True}
    assert frontend_json(response) == expected, 'Labels command failed.'

    # Test focus command
    ws.send('{"command": "repo focus", "repo": "GitSpace"}')
    response = str(s.recv(BUFFER_SIZE))
    expected = {"api version": 1, "type": "command", "command": "repo focus", "repo": "GitSpace"}
    assert frontend_json(response) == expected, 'Focus command failed.'

    # Test reset command
    ws.send('{"command": "reset camera"}')
    response = str(s.recv(BUFFER_SIZE))
    expected = {"api version": 1, "type": "command", "command": "reset camera"}
    assert frontend_json(response) == expected, 'Reset command failed.'

    # Test activity command
    ws.send('{"command": "activity threshold", "threshold": 200}')
    response = str(s.recv(BUFFER_SIZE))
    expected = {"api version": 1, "type": "command", "command": "activity threshold", "threshold": 200}
    assert frontend_json(response) == expected, 'Activity command failed.'

    # Test add command
    ws.send('{"command": "repo add", "repo": "MySpace", "owner": "tilatequila"}')
    response = str(s.recv(BUFFER_SIZE))
    assert frontend_json(response) == mock_repos["MySpace"], 'Add command failed.'

    # Test delete command
    ws.send('{"command": "repo delete", "repo": "MySpace"}')
    response = str(s.recv(BUFFER_SIZE))
    expected = {"api version": 1, "type": "delete", "repo": "MySpace"}
    assert frontend_json(response) == expected, 'Delete command failed.'

    print('All tests successful!')
except AssertionError as e:
    print(e)

# Let everything finish up
time.sleep(3)

# Close connections
s.close()
server.terminate()
server.join()
