from IO.websocket_server import WebsocketServer

IP = '127.0.0.1'
PORT = 8080

mock_setup_json = "{'name': 'GitSpace', 'users': 'powie'}"

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
