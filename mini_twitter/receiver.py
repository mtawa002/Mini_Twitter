import socket
import sys
import threading
import json
from check import ip_checksum

cli_list = [['c1', 'Marcel'], ['c2', 'Nick'], ['c3', 'Tom']]
MsgList = [[], [], []] # (clientname - message)
off_list_tweets = [[], [], []]
connections = [[], [], []]
subList = [[], [], []]
tweetList = []
threads = []
msg_count = 0

try:
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print '\tReceive Socket created'
except socket.error, msg:
    print '\tFailed to create socket. Error code : ' + str(msg[0]) + ' Message: ' + msg[1]
    sys.exit()

dest = ('127.0.0.1', 4394)

try:
    recv_sock.bind(dest)
except socket.error, msg:
    print '\tBind failed. Error code : ' + str(msg[0]) + ' Message: ' + msg[1]
    sys.exit()

recv_sock.listen(10)
connection, address = socket.socket(socket.AF_INET, socket.SOCK_STREAM), []

def user_id(name):
    if name == 'c1':
        return 0
    elif name == 'c2':
        return 1
    elif name == 'c3':
        return 2

def send_offline_tweets(name):
    msg = json.dumps({"tweetlist" :off_list_tweets[user_id(name)]})
    connections[user_id(name)][1].sendall(msg)
    for l in off_list_tweets[user_id(name)]:
        off_list_tweets[user_id(name)].remove(l)

def user_handler(name, connection):
    user = user_id(name)
    send_offline_tweets(name)

    while True:
        #connection, address = recv_sock.accept()
        message = connection.recv(4096)
        print '\tclient request: ' + name + ' ' + message[2:]
    
        if not message:
            break
            
        elif message[:2] == ip_checksum(message[2:]):
            if message[2:] == 'Offline_messages_request':
                user = user_id(name)
                if len(MsgList[user]) == 0:
                    msg = json.dumps({"msglist" :'No Messages Received'})
                else:
                    msg = json.dumps({"msglist" :MsgList[user]})
                connection.sendall(msg)

            elif message[2:] == 'Send Message':
                message = connection.recv(4096)
                hdr = message[:2]
                if len(connections[user_id(hdr)]) == 0:
                    MsgList[user_id(hdr)].append(message[2:])
                else:
                    connections[user_id(hdr)][1].sendall('live_msg' + message[2:])
                connection.sendall('success')

            elif message[2:] == 'Post Tweet':
                tweet = connection.recv(4096)
                tweetList.append(tweet)
                for j in range(0, len(connections)):
                    st = 'c' + str(j)
                    if  st in subList[user_id(name)]:
                        if len(connections[j]) == 0:
                            off_list_tweets[j].append(tweet)
                        else:                       
                            connections[j][1].sendall('live_twt'+tweet)              
            
            elif message[2:] == 'Del_Friend_Msgs':
                message = connection.recv(4096)
                temp = []
                temp = message.split(':')
                user = temp[0]
                friend = temp[1]
                a = user_id(name)
                lst = MsgList[a]
                for l in lst:
                    if l[:2] == friend:
                        MsgList[a].remove(l)
                connection.sendall('success')

            elif message[2:] == 'Del_All_Msgs':
                a = user_id(name)
                lst = MsgList[a]
                for l in lst:
                    MsgList[a].remove(l)
                connection.sendall('success')
            
            elif message[2:] == 'Subscribe':
                msg = connection.recv(4096)
                friend = msg[2:]
                me = msg[:2]
                subList[user_id(friend)].append(me)
                connection.sendall('success')

            elif message[2:] == 'Unsubscribe':
                unsub = []
                for i in range(0, len(subList)):
                    if name in subList[i]:
                        unsub.append('c'+str(i))
                if len(unsub) == 0:
                    msg = json.dumps({"list" : 'No followers'})
                    connection.sendall(msg)
                else:
                    msg = json.dumps({"list" : unsub})
                    connection.sendall(msg)

                    msg = connection.recv(4096)
                    friend = msg[2:]
                    me = msg[:2]                
                    subList[user_id(friend)].remove(me)
                    connection.sendall('success')
            
            elif message[2:] == 'See Followers':
                if len(subList[user_id(name)]) == 0:
                    msg = json.dumps({"subList" : 'No Followers'})
                else:
                    msg = json.dumps({"subList" : subList[user_id(name)]})
                connection.sendall(msg)
            
            elif message[2:] == 'Hashtag Search':
                msg = connection.recv(4096)
                hashList = []
                for i in range(0, len(tweetList)):
                    if msg in tweetList[i]:
                        hashList.append(tweetList[i])
                if len(hashList) == 0:
                    msg = json.dumps({"hashList" : 'No Tweets Found'})
                else:
                    msg = json.dumps({"hashList" : hashList})
                connection.sendall(msg)

            elif message[2:] == 'Logging Out':
                connection.sendall('success')
                connection.close()
                for c in  connections[user_id(name)]:
                    connections[user_id(name)].remove(c)
                return
    return

def login_verification():
    msg_count = 0
    while True:
        connection, address = recv_sock.accept()
        message = connection.recv(4096)

        checksum = message[:2]
        if not ip_checksum(message[2:]) == message[:2]:
            continue
        else:
            s = message[2:]

            temp  = []
            temp = s.split(':')
            if len(temp) == 2:
                name, password = temp[0], temp[1]
            
                found = False
                for cli in cli_list:
                    if cli == [name, password]:
                        found = True
                        break
                if not found:
                    connection.sendall(ip_checksum('Invalid') + 'Invalid')
                    print '\n\t' + name + ' Connection attempt failed\n'
                else:
                    print '\n\t' + name + ' Successfully Logged in\n'
                    
                    connection.sendall(ip_checksum('Valid') + 'Valid')
                    connections[user_id(name)].append(connection)
                    recv_sock.listen(1)

                    live_sock, address = recv_sock.accept()
                    connections[user_id(name)].append(live_sock)
                    
                    print len(connections[user_id(name)])
                    print '\t' + name + ' Live socket connected'
                    #recv_sock.listen(5)

                    t = threading.Thread(target = user_handler, args=(name, connection,))
                    t.daemon = True
                    threads.append(t)
                    t.start()

    recv_sock.close()

login_verification()
