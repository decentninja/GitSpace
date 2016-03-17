from IO.websocket_server import WebsocketServer
import os
import sys

IP = '0.0.0.0'
PORT = 8080

mock_setup_json_short = "{'name': 'GitSpace', 'users': 'powie'}"

mock_setup_json = '{"data":[{"name":"decentninja/GitSpace","users":[{"username": "decentninja", "image": "https://avatars.githubusercontent.com/u/900740?v=3", "name": "Andreas Linn"}, {"username": "viclarsson", "image": "https://avatars.githubusercontent.com/u/4243380?v=3", "name": "Victor Larsson"}, {"username": "Zercha", "image": "https://avatars.githubusercontent.com/u/4265058?v=3", "name": "Zercha"}, {"username": "matlon", "image": "https://avatars.githubusercontent.com/u/4280152?v=3", "name": "matlon"}, {"username": "powion", "image": "https://avatars.githubusercontent.com/u/4322541?v=3", "name": "Paulina"}, {"username": "alan93", "image": "https://avatars.githubusercontent.com/u/6649125?v=3", "name": "alan93"}, {"username": "Jogol", "image": "https://avatars.githubusercontent.com/u/6697929?v=3", "name": "Jonathan Golan"}, {"username": "adhag", "image": "https://avatars.githubusercontent.com/u/6747487?v=3", "name": "Adrian Häggvik"}]}]}'

def new_client(client, server):
    # TODO: Get init state to send to client.
    print('App has connected.', file=sys.stderr)
    server.out_queue.put(('{"message": {"command": "internal_state"}}', client['repo_id']))
    server.send_message(client, server.in_queue.get())

def recv_message(client, server, message):
    server.out_queue.put((message, client['repo_id']))
    response = server.in_queue.get()
    if response == 'internal':
        print('App command has been processed.', file=sys.stderr)
    elif response == 'internal_error':
        pass
    else:
        server.send_message(client, response)
        print('App command has been processed.', file=sys.stderr)

def serve(out_queue, in_queue):
    print("Creating Websocket server...", file=sys.stderr)
    server = WebsocketServer(PORT, out_queue, in_queue, host=IP)
    print("Websocket server created, starting...", file=sys.stderr)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(recv_message)
    server.run_forever()
