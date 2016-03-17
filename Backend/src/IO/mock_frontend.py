import socket


TCP_IP = '127.0.0.1'
TCP_PORT = 5522
BUFFER_SIZE = 10000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send('gitspace'.encode('utf-8'))
n = 0
while n < 300:
    data = s.recv(BUFFER_SIZE)
    print(data)
    n += 1
s.close()
