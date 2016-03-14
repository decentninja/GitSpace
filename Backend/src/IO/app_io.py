from IO.websocket_server import WebsocketServer

IP = '0.0.0.0'
PORT = 8080

mock_setup_json_short = "{'name': 'GitSpace', 'users': 'powie'}"

mock_setup_json = '{"data":[{"name":"GitSpace","users":[{"name":"Dean Martin","mail":"dean@martin.com","image":"https://sc-cdn.scaleengine.net/i/541c25f2434b87947374e4de5ea467461.png"},{"name":"Frank Sinatra","mail":"frank@sinatra.com","image":"https://sc-cdn.scaleengine.net/i/541c25f2434b87947374e4de5ea467461.png"},{"name":"Robbie Williams","mail":"robbie@williams.com","image":"https://sc-cdn.scaleengine.net/i/541c25f2434b87947374e4de5ea467461.png"}]}]}'

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
