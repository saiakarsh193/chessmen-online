import socket
import threading
import time

from sharedmem import sharedMem
from gameobject import gameObject

IP_ADDR, PORT, BUFFER_SIZE = '10.1.130.208', 2000, 4096

userlist = sharedMem([])
gamelist = sharedMem([])

skt = socket.socket()
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
skt.bind((IP_ADDR, PORT))
print('server binded to ' + IP_ADDR + ':' + str(PORT))
skt.listen(5)

def findUID(uid):
    ufound = False
    userlist.lock()
    for user in userlist.data:
        if(user['uid'] == uid):
            ufound = True
            break
    userlist.unlock()
    return ufound

def getCTime():
    return int(time.time()) % 100000

def allocateUID(uid):
    userlist.lock()
    userlist.data.append({'uid': uid, 'game': None, 'ping': getCTime()})
    userlist.unlock()

def statusUID(uid):
    status = ""
    userlist.lock()
    gamelist.lock()
    for user in userlist.data:
        if(user['uid'] == uid):
            user['ping'] = getCTime()
            if(user['game'] == None):
                status = 'waiting for game'
            else:
                if(user['game'].status == 0):
                    if(user['game'].turn == uid):
                        status = 'your turn'
                    else:
                        status = 'opponent turn'
                else:
                    status = 'game stopped'
            break
    gamelist.unlock()
    userlist.unlock()
    return status

def getFEN(uid):
    fen = 'no game created'
    userlist.lock()
    gamelist.lock()
    for user in userlist.data:
        if(user['uid'] == uid):
            if(user['game'] != None):
                fen = user['game'].color(user['uid']) + ' :: ' + user['game'].fen
            break
    gamelist.unlock()
    userlist.unlock()
    return fen

def setFEN(uid, fen):
    status = ''
    userlist.lock()
    gamelist.lock()
    for user in userlist.data:
        if(user['uid'] == uid):
            if(user['game'] != None):
                if(user['game'].status == 0):
                    if(user['game'].turn == uid):
                        user['game'].update(fen)
                        status = 'updated fen'
                    else:
                        status = 'not your turn'
                else:
                    status = 'game stopped'
            else:
                status = 'no game created'
            break
    gamelist.unlock()
    userlist.unlock()
    return status

def exitUID(uid):
    userlist.lock()
    gamelist.lock()
    for ind, user in enumerate(userlist.data):
        if(user['uid'] == uid):
            if(user['game'] != None):
                user['game'].status -= 1
            userlist.data.pop(ind)
            break
    gamelist.unlock()
    userlist.unlock()

def getSummary():
    summary = ''
    userlist.lock()
    gamelist.lock()
    summary += '(users online: ' + str([(user['uid'], -1 if user['game'] == None else 0) for user in userlist.data]) + ')'
    summary += '(games running: ' + str([(game.summary(), game.status) for game in gamelist.data]) + ')'
    gamelist.unlock()
    userlist.unlock()
    return summary

def maintainer():
    # remove unresponsive uid
    userlist.lock()
    rmusers = [user['uid'] for user in userlist.data if(getCTime() - user['ping'] > 100)]
    userlist.unlock()
    for user in rmusers:
        exitUID(user)
    # remove finished/stopped games
    gamelist.lock()
    gamelist.data = [game for game in gamelist.data if(game.status > -2)]
    gamelist.unlock()
    # allocate game
    userlist.lock()
    uid1 = ""
    uid2 = ""
    for user in userlist.data:
        if(user['game'] == None):
            if(uid1 == ''):
                uid1 = user['uid']
            elif(uid2 == ''):
                uid2 = user['uid']
    if(uid1 != '' and uid2 != ''):
        gobj = gameObject(uid1, uid2)
        gamelist.lock()
        gamelist.data.append(gobj)
        gamelist.unlock()
        for user in userlist.data:
            if(user['uid'] == uid1 or user['uid'] == uid2):
                user['game'] = gobj
    userlist.unlock()

def clientThread(client, address):
    # print('client ' + address[0] + ':' + str(address[1]) + ' connected')
    maintainer()
    # connect
    client.send(str.encode('<connected>'))
    # request
    req = client.recv(BUFFER_SIZE).decode()
    req = req[1:-1]
    sreq = req.split(":")
    sreq = [sq.strip().lower() for sq in sreq]
    uid = sreq[0]
    comm = sreq[1]
    payload = sreq[2] if len(sreq) == 3 else ""
    # response
    resp = '<invalid command>'
    if(comm == 'allocate'):
        if(findUID(uid)):
            resp = '<uid already allocated>'
        else:
            allocateUID(uid)
            resp = '<uid allocated>'
    elif(comm == 'status'):
        if(findUID(uid)):
            resp = '<' + statusUID(uid) + '>'
        else:
            resp = '<uid unallocated>'
    elif(comm == 'exit'):
        if(findUID(uid)):
            exitUID(uid)
            resp = '<uid exited>'
        else:
            resp = '<uid unallocated>'
    elif(comm == 'getfen'):
        if(findUID(uid)):
            resp = '<' + getFEN(uid) + '>'
        else:
            resp = '<uid unallocated>'
    elif(comm == 'setfen'):
        if(findUID(uid)):
            resp = '<' + setFEN(uid, payload) + '>'
        else:
            resp = '<uid unallocated>'
    elif(comm == 'summary'):
        if(uid == 'dev'):
            resp = '<' + getSummary() + '>'
        else:
            resp = '<unauthorized uid>'
    client.send(str.encode(resp))
    # acknowledgement
    ack = client.recv(BUFFER_SIZE).decode()
    # disconnect
    client.send(str.encode('<disconnected>'))
    client.close()
    # print('client ' + address[0] + ':' + str(address[1]) + ' disconnected')

while True:
    (client, address) = skt.accept()
    threading.Thread(target = clientThread, args = (client, address)).start()