#!/usr/bin/env python
# A simple Python bot to tell jokes.
# For hardmath123.github.io/socket-science-2.html

import socket
import select
import random
import ssl
import sys
import time
from jokes import jokes

if len(sys.argv) != 5:
    print "Usage: python %s <host> <channel (no #)> [--ssl|--plain] <nick>"
    exit(0)

HOST = sys.argv[1]
CHANNEL = "#"+sys.argv[2]
SSL = sys.argv[3].lower() == '--ssl'
PORT = 6697 if SSL else 6667

NICK = sys.argv[4]

plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = ssl.wrap_socket(plain) if SSL else plain

print "Connecting..."

s.connect((HOST, PORT))
def read_loop(callback):
    data = ""
    CRLF = '\r\n'
    while True:
        time.sleep(1)
        try:
            readables, writables, exceptionals = select.select([s], [s], [s]) 
            if len(readables) == 1:
                data += s.recv(512);
                while CRLF in data:
                    message = data[:data.index(CRLF)]
                    data = data[data.index(CRLF)+2:]
                    callback(message)
        except KeyboardInterrupt:
            print "Leaving..."
            s.sendall("PART %s :Bye\r\n"%(CHANNEL))
            s.close()
            exit(0)

print "Registering..."

s.sendall("NICK %s\r\n"%(NICK))
s.sendall("USER %s * * :A joke bot\r\n"%(NICK))


connected = False
def got_message(message):
    print message
    global connected # yes, bad Python style. but it works to explain the concept, right?
    words = message.split(' ')
    if 'PING' in message:
        s.sendall('PONG\r\n') # it never hurts to do this :)
    if words[1] == '001' and not connected:
        # As per section 5.1 of the RFC, 001 is the numeric response for
        # a successful connection/welcome message.
        connected = True
        s.sendall("JOIN %s\r\n"%(CHANNEL))
        print "Joining..."
    elif words[1] == 'PRIVMSG' and words[2] == CHANNEL and '!joke' in words[3] and connected:
        # Someone probably said `!joke`.
        s.sendall("PRIVMSG %s :"%(CHANNEL) + random.choice(jokes) + "\r\n")
read_loop(got_message)
