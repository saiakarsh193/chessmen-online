import socket

IP_ADDR, PORT, BUFFER_SIZE = '10.1.130.208', 2000, 4096

skt = socket.socket()

try:
    skt.connect((IP_ADDR, PORT))
    print('connected to server at ' + IP_ADDR + ':' + str(PORT))
    # connect
    data = skt.recv(BUFFER_SIZE).decode()
    # request
    # <akarsh : allocate>
    # <akarsh : status>
    # <akarsh : getfen>
    # <akarsh : setfen : rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR>
    # <akarsh : exit>
    req = '<' + input() + '>'
    skt.send(str.encode(req))
    # response
    resp = skt.recv(BUFFER_SIZE).decode()
    print(resp)
    # acknowledgement
    skt.send(str.encode('<done>'))
    # disconnect
    data = skt.recv(BUFFER_SIZE).decode()
    skt.close()
    print('disconnected to server')
except socket.error as e:
    print(str(e))