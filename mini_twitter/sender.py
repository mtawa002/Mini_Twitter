from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, timeout, error
import sys
import json
from check import ip_checksum
import getpass
import os
import threading
import time
import datetime

send_sock = socket(AF_INET, SOCK_STREAM)
send_sock.settimeout(5)
dest = ('127.0.0.1', 4394)
send_sock.connect(dest)

def Offline_Msg(cli):
    os.system('clear')
    has_answered = False

    while not has_answered:
        send_sock.sendall(ip_checksum("Offline_messages_request") + 'Offline_messages_request')
        try:
            message  = send_sock.recv(4096)
        except timeout:
            print '\tTimeout - Sever busy'
            continue
        else:
            has_answered = True
            ret = json.loads(message)
            MsgList = ret["msglist"]
            print '\n\t********************'
            print '\n\t' + cli + ' List of Messages:'
            print '\n\t'
            if MsgList == 'No Messages Received':
                print MsgList
            else:
                for i in range(0, len(MsgList)):
                    print MsgList[i]
            print '\n'
    menu(cli)
    return

def Edit_Sub(cli):
    os.system('clear')
    print("""\n
    \t1. Add Subscription
    \t2. Delete Subscription
    """)
    choice = int(raw_input('\n\tEnter Your Choice: '))
    if choice == 1:
        send_sock.sendall(ip_checksum('Subscribe') + 'Subscribe')
        friend = raw_input('\n\tEnter Friend to Subscribe to: ')

        has_succeeded = False
        while not has_succeeded:
            send_sock.sendall(cli+friend)
            reply = send_sock.recv(4096)
            if reply == 'success':
                has_succeeded = True
            
    elif choice == 2:
        send_sock.sendall(ip_checksum('Unsubscribe') + 'Unsubscribe')
        reply = send_sock.recv(4096)
        list = json.loads(reply)
        sublist = list["list"]

        if sublist == 'No followers':
            print '\tNo user to Unsubscribe from'
        else:
            for l in sublist:
                print l
            friend = raw_input('\n\tEnter Friend to Unsubcribe from: ')
    
            has_succeeded = False
            while not has_succeeded:
                send_sock.sendall(cli+friend)
                reply = send_sock.recv(4096)
                if reply == 'success':
                    has_succeeded = True
    menu(cli)
    return

def Post_Msg(cli):
    os.system('clear')
    tweet = raw_input('\tEnter your tweet: ')
    send_sock.sendall(ip_checksum('Post Tweet') + 'Post Tweet')
    send_sock.sendall(cli + ': ' + tweet)
    menu(cli)
    return

def Hashtag_Search(cli):
    os.system('clear')
    send_sock.sendall(ip_checksum('Hashtag Search') + 'Hashtag Search')
    hashtag = raw_input('\tEnter the hashtag to search for: ')
    send_sock.sendall(hashtag)
    reply = send_sock.recv(4096)
    msg = json.loads(reply)
    hashList = msg["hashList"]
    print '\n\t' + cli + ' List of tweets containing ' + hashtag + ':'
    if hashList == 'No Tweets Found':
        print hashList
    else:
        for i in range(0, len(hashList)):
            print hashList[i]
    print '\n'
    menu(cli)
    return

def See_followers(cli):
    os.system('clear')
    send_sock.sendall(ip_checksum('See Followers') + 'See Followers')
    reply = send_sock.recv(4096)
    msg = json.loads(reply)
    subList = msg["subList"]
    print '\n\t' + cli + ' List of Followers: '
    if subList == 'No Followers':
        print subList
    else:
        for i in range(0, len(subList)):
            print subList[i]
    print '\n'
    menu(cli)
    return

def Send_Msgs(cli):
    os.system('clear')
    send_sock.sendall(ip_checksum('Send Message') + 'Send Message')
    destinator = raw_input('\n\tEnter destinator: ')
    msg = raw_input('\tEnter Message: ')

    while len(msg) > 140:
        print '\n\tMessage longer than 140 characters -- try again'
        msg = raw_input('\tEnter Message: ')
    
    has_succeeded = False
    while not has_succeeded:
        send_sock.sendall(destinator + cli + ': ' + msg)
        reply = send_sock.recv(4096)
        if reply == 'success':
            has_succeeded = True
    menu(cli)
    return

def Del_Friend_Msgs(cli):
    os.system('clear')
    send_sock.sendall(ip_checksum('Del_Friend_Msgs') + 'Del_Friend_Msgs')
    friend = raw_input("\tEnter friend whose messages to delete: ")
    
    has_succeeded = False
    while not has_succeeded:
        send_sock.sendall(cli + ':' + friend)
        reply = send_sock.recv(4096)
        if reply == 'success':
            has_succeeded = True
    menu(cli)
    return

def Del_All_Msgs(cli):
    os.system('clear')
    send_sock.sendall(ip_checksum('Del_All_Msgs') + 'Del_All_Msgs')
    has_succeeded = False
    while not has_succeeded:
        reply = send_sock.recv(4096)
        if reply == 'success':
            has_succeeded = True
    menu(cli)
    return

def read_choice(cli):
    print '\n\t****************************'
    choice = int(raw_input('\n\tPick a menu option: '))
    print '\n\t****************************'
    if choice == 1:
        Offline_Msg(cli)
    elif choice == 2:
        Edit_Sub(cli)
    elif choice == 3:
        Post_Msg(cli)
    elif choice == 4:
        print '\n\t***GoodBye***\n\tLogging You Out'
        has_received = False
        while not has_received:
            send_sock.sendall(ip_checksum('Logging Out') + 'Logging Out')
            reply = send_sock.recv(4096)
            if reply == 'success':
                has_received = True
                send_sock.close()
    elif choice == 5:
        Hashtag_Search(cli)
    elif choice == 6:
        See_followers(cli)
    elif choice == 7:
        Send_Msgs(cli)
    elif choice == 8:
        Del_Friend_Msgs(cli)
    elif choice == 9:
        Del_All_Msgs(cli)

def menu(cli):
    print("""\n
    \t**********************
    \t1. See Offline Messages
    \t2. Edit Subscriptions
    \t3. Post Tweets
    \t4. Logout
    \t5. Hashtag Search
    \t6. See Followers
    \t7. Send Messages
    \t8. Delete Messages From A Friend
    \t9. Delete All Messages
    \t**********************
    """)
    read_choice(cli)

def tweets_and_msgs_handler(cli, live_sock):
    st = datetime.datetime.now().strftime("%A, %d, %B, %Y, %I:%M%p")
    print st + ' Welcome ' + cli
    
    msg = live_sock.recv(4096)
    ret = json.loads(msg)
    twt_list = ret["tweetlist"]
    print 'You have ' + str(len(twt_list)) + ' Unread tweets:'
    for l in twt_list:
        print l

    while True: 
        try:
            m = live_sock.recv(4096)
        except timeout:
            continue
        else:
            if m[:8] == 'live_msg':
                print m[8:]
            elif m[:8] == 'live_twt':
                print m[8:]
    return

def authenticate():
    os.system('clear')
    print '\t***************************'
    cli_name = raw_input('\tUsername: ')
    cli_pwd = getpass.getpass('\tPassword: ')
    print '\t***************************'

    print '\n\t****Waiting for server to authenticate your login****\n'

    authentication = cli_name
    authentication += ':' + cli_pwd
    
    ans_received = False
    
    while not ans_received:
        send_sock.sendall(ip_checksum(authentication) + authentication)
        try:
            message = send_sock.recv(4096)
        except timeout:
            print 'Timeout occured -- Server Busy'
            continue
        else:
            if not message[:2] == ip_checksum(message[2:]):
                continue #resend the authentication to server
            else:
                ans_received = True
                if message[2:] == 'Valid':
                    os.system('clear')
                    print '\n\tSuccessful Login!! -- Welcome ' + cli_name
                    
                    live_sock = socket(AF_INET, SOCK_STREAM)
                    live_sock.connect(dest)
                    
                    t = threading.Thread(target = tweets_and_msgs_handler, args=(cli_name, live_sock, ))
                    t.daemon = True
                    t.start()
                    menu(cli_name)
                elif message[2:] == 'Invalid':
                    print '\n\tError: Name or Password entered is invalid -- Try again'
                    authenticate()
    send_sock.close()

authenticate()
