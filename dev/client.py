import socket

IP_ADDR, PORT, BUFFER_SIZE = '10.1.130.208', 2000, 4096

def pingServer(request):
    skt = socket.socket()
    try:
        skt.connect((IP_ADDR, PORT))
        # print('connected to server at ' + IP_ADDR + ':' + str(PORT))
        # connect
        data = skt.recv(BUFFER_SIZE).decode()
        # request
        # <akarsh : allocate>
        # <akarsh : status>
        # <akarsh : getfen>
        # <akarsh : setfen : rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR>
        # <akarsh : exit>
        req = '<' + request + '>'
        skt.send(str.encode(req))
        # response
        resp = skt.recv(BUFFER_SIZE).decode()
        # acknowledgement
        skt.send(str.encode('<done>'))
        # disconnect
        data = skt.recv(BUFFER_SIZE).decode()
        skt.close()
        # print('disconnected to server')
        return resp
    except socket.error as e:
        print(str(e))
        return None

if __name__ == '__main__':
    print(pingServer(input()))