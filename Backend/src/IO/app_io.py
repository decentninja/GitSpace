from IO.websocket_server import WebsocketServer

IP = '0.0.0.0'
PORT = 8080

mock_setup_json_short = "{'name': 'GitSpace', 'users': 'powie'}"

mock_setup_json = '{"data":[{"name":"decentninja/GitSpace","users":[{"username": "decentninja", "image": "https://avatars.githubusercontent.com/u/900740?v=3", "name": "Andreas Linn"}, {"username": "viclarsson", "image": "https://avatars.githubusercontent.com/u/4243380?v=3", "name": "Victor Larsson"}, {"username": "Zercha", "image": "https://avatars.githubusercontent.com/u/4265058?v=3", "name": "Zercha"}, {"username": "matlon", "image": "https://avatars.githubusercontent.com/u/4280152?v=3", "name": "matlon"}, {"username": "powion", "image": "https://avatars.githubusercontent.com/u/4322541?v=3", "name": "Paulina"}, {"username": "alan93", "image": "https://avatars.githubusercontent.com/u/6649125?v=3", "name": "alan93"}, {"username": "Jogol", "image": "https://avatars.githubusercontent.com/u/6697929?v=3", "name": "Jonathan Golan"}, {"username": "adhag", "image": "https://avatars.githubusercontent.com/u/6747487?v=3", "name": "Adrian Häggvik"}]}]}'

def new_client(client, server):
    # TODO: Get init state to send to client.
    server.send_message(client, mock_setup_json)

def recv_message(client, server, message):
    server.queue.put((message, client['repo_id']))

def serve(queue):
    server = WebsocketServer(PORT, queue, host=IP)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(recv_message)
    server.run_forever()
