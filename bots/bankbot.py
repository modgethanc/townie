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
parser.add_option("-c", "--channel", dest="channel", default='#bot_test',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='bankbot',
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
    ircsock.send("PRIVMSG "+ channel +" :Welcome to the Automated Tilde Teller. !balance, !deposit x, !withdraw x, !pay nick x.\n")

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

def tildeboard(channel):
    board = []
    with open("/home/krowbar/Code/irc/tildescores.txt", "r") as scorefile:
        for idx,score in enumerate(scorefile):
            board.append(score.strip("\n").split("&^%"))

    board.sort(key=lambda entry:int(entry[1]), reverse=True)

    ircsock.send("PRIVMSG " + channel + " :Top Five Tilde Miners:\n")

    for x in range (0, 5):
           entry = board[x]
           ircsock.send("PRIVMSG " + channel + " :" + entry[0] + " with " + entry[1] + " tildes\n") 

def getMined(user):
    with open("tildescores.txt", "r") as scorefile:
        for idx,score in enumerate(scorefile):
            person = score.strip("\n").split("&^%")
            if(person[0] == user):
                return person[1]

def balance(channel, user):
        with open("tildeaccounts.txt", "r+") as accountfile:
                accounts = accountfile.readlines()
                accountfile.seek(0)
                accountfile.truncate()
                for account in accounts:
                        entry = account.strip("\n").split("&^%")
                        if (entry[0] == user):
                                ircsock.send("PRIVMSG " + channel + " :" + user + ": " + entry[1] + "T banked, " + entry[2] + "T cash in hand") 
                                return
                ircsock.send("PRIVMSG " + channel + " :"+ user + ": No account found. Please open a TildeBank account with !newaccount.")

def newAccount(channel, user):

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

    if ircmsg.find(":bankbot: botsnack") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": I do not accept bribes.\n")

    if ircmsg.find(":!tildeboard") != -1:
            tildeboard(channel)

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
