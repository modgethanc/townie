#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import sys
from optparse import OptionParser
import fileinput
import random

import formatter
import get_users
import mentions
import pretty_date
import inflect

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#tildetown',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='cndorphant',
                  help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()

p = inflect.engine()

def ping():
  ircsock.send("PONG :pingis\n")

def sendmsg(chan , msg):
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n")

def joinchan(chan):
  ircsock.send("JOIN "+ chan +"\n")

def rollcall(channel):
    ircsock.send("PRIVMSG "+ channel +" :cndorphant here! i'm pretty useless.\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :endorphant\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def get_user_from_message(msg):
  try:
    i1 = msg.index(':') + 1
    i2 = msg.index('!')
    return msg[i1:i2]
  except ValueError:
    return ""

def listen():
  mark = 0
  mine = 0 
  interval = 0

  while 1:

    ircmsg = ircsock.recv(2048)
    ircmsg = ircmsg.strip('\n\r')

    if ircmsg.find("PING :") != -1:
      ping()

    formatted = formatter.format_message(ircmsg)

    if "" == formatted:
      continue

    # print formatted

    split = formatted.split("\t")
    time = split[0]
    user = split[1]
    command = split[2]
    channel = split[3]
    messageText = split[4]

    if ircmsg.find(":!rollcall") != -1:
      rollcall(channel)

    if ircmsg.find("PING :") != -1:
      ping()

    if ircmsg.find(":cndorphant: botsnack") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": thanks <3.\n")

    if ircmsg.find(":cndorphant: time") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": "+ time +"\n")

    if ircmsg.find(":cndorphant: sync") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": "+ mark+"\n")

    if ircmsg.find(":cndorphant: mark") != -1:
        mark = time
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": sync!\n")

    if ircmsg.find(":cndorphant: mine some tildes") != -1:
        if user == "endorphant":
                mine = time
                ircsock.send("PRIVMSG "+ channel +" :"+ user + ": roger!\n")
                ircsock.send("PRIVMSG "+ channel +" :!tilde\n")
        else :
                ircsock.send("PRIVMSG "+ channel +" :"+ user + ": you're not the boss of me, buddy\n")

    if mine > 0:
        interval = int(time)-int(mine)

    if interval >= 60*60:
        mine = time
        ircsock.send("PRIVMSG "+ channel +" :!tilde\n")

    if ircmsg.find(":cndorphant: report") != -1:
        ircsock.send("PRIVMSG "+ channel +" :!tildescore\n")

    if ircmsg.find(":cndorphant") != -1:
        ircsock.send("PRIVMSG "+ channel +" :not sure what you meant by that...\n")
            

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
