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

mark = 0
mine = 0 
interval = 0

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#bot_test',
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
  ircsock.send("PRIVMSG "+ channel +" :cndorphant here! i'm pretty useless, but i'm doing my best.\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :endorphant\n") # user authentication
  ircsock.send("NICK "+ botnick +"\n")

  joinchan(channel)

def addressed(msg, channel, user, time):
    global mark
    global mine

    if msg.find("botsnack") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": thanks <3.\n")

    elif msg.find("mine some tildes") != -1:
         if user == "endorphant":
            mine = time
            ircsock.send("PRIVMSG "+ channel +" :"+ user + ": roger!\n")
            ircsock.send("PRIVMSG "+ channel +" :!tilde\n")
         else :
            ircsock.send("PRIVMSG "+ channel +" :"+ user + ": you're not the boss of me, buddy\n")

    elif msg.find("time") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": "+ time +"\n")

    elif msg.find("<3") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": :)\n")

    elif msg.find("sync") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": "+ mark+"\n")

    elif msg.find("mark") != -1:
        mark = time
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": sync!\n")

    elif msg.find(" :(") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": cheer up, friend, it can't be so bad\n")

    elif msg.find(" :)") != -1:
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": :D\n")

    elif msg.find("report") != -1:
        ircsock.send("PRIVMSG "+ channel +" :!tildescore\n")

    elif msg.find("beg") != -1:
        ircsock.send("PRIVMSG "+ channel +" :!tilde\n")

    elif msg.find("tildeboard") != -1:
        tildeboard(channel)

    elif msg.find("commands") != -1:
        ircsock.send("PRIVMSG " + channel + " :" + user + ": you can't tell me what to do!\n")

    elif msg.find("get out") != -1:
        ircsock.send("PRIVMSG " + channel + " :" + user + ": okay :(\n")
        ircsock.send("PART " + channel + "\n")

    elif msg.find("join") != -1:
        ircsock.send("PRIVMSG " + channel + " :" + user + ": k\n")
        split = msg.split(" ");
        for x in split:
            if x.find("#") != -1:
                #ircsock.send("PRIVMSG " + channel + " :" + user + ": you mean " + x +", right?\n")
                joinchan(x)

    #elif user == "tildebot" and ircmsg.find(":cndorphant: ") != -1:
    elif msg.find("Answer with numbers") != -1:
        ans = doMath(msg)
        ircsock.send("PRIVMSG "+ channel +" :"+ ans + "\n")

    else:
        ircsock.send("PRIVMSG "+ channel +" :" + user + ": not sure what you meant by that...\n")

def get_user_from_message(msg):
  try:
    i1 = msg.index(':') + 1
    i2 = msg.index('!')
    return msg[i1:i2]
  except ValueError:
    return ""

def doMath(problem):
    ans = ''
    var1 = 0
    var2 = 0
    op = 0
    calc = ''
    
    add = ["and ", "plus ", "sum ", "add "]
    sub = ["minus ", "subtract ", "take away ", "less "]
    mult = ["times ", "multiply ", "multiplied by ", "product "]
    div = ["divided by ", "over "]
    power = ["to the "]

    parse = problem.split(' ')
    print parse 
    for word in parse:
        if parseNumber(word):
            if var1 == 0:
                var1 = parseNumber(word)
                print var1
            else:
                var2 = parseNumber(word)
                print var2
        elif var1 != 0:
            if var2 == 0:
                calc += word + " "

    print calc

    if calc in add:
        ans = var1 + var2
    elif calc in sub:
        ans = var1 - var2
    elif calc in mult:
        ans = var1 * var2
    elif calc in div:
        ans = var1 / var2
    elif calc in power:
        ans = var1 ** var2
    else:
        ans = "beats me, i'm not good at math"

    #ans = str(var1) + " " + calc + str(var2)

    return str(ans)

def parseNumber(word):
    num = False
    if word.find("one") != -1:
        num = 1
    elif word.find("two") != -1:
        num = 2
    elif word.find("three") != -1:
        num = 3
    elif word.find("four") != -1:
        num = 4
    elif word.find("five") != -1:
        num = 5
    elif word.find("six") != -1:
        num = 6
    elif word.find("seven") != -1:
        num = 7
    elif word.find("eight") != -1:
        num = 8
    elif word.find("nine") != -1:
        num = 9

    return num

def tildeboard(channel):
    board = []
    with open("/home/krowbar/Code/irc/tildescores.txt", "r") as scorefile:
        for idx,score in enumerate(scorefile):
            board.append(score.strip("\n").split("&^%"))

    board.sort(key=lambda entry:int(entry[1]), reverse=True)

    ircsock.send("PRIVMSG " + channel + " :top five tilde scores:\n")

    for x in range (0, 5):
           entry = board[x]
           ircsock.send("PRIVMSG " + channel + " :" + entry[0] + " with " + entry[1] + " tildes\n") 

def listen():
  global mine
  global interval

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

    if ircmsg.find(":cndorphant: ") != -1:
       addressed(messageText, channel, user, time)

    if mine > 0:
        interval = int(time)-int(mine)

    if interval >= 60*60:
        mine = time
        ircsock.send("PRIVMSG "+ channel +" :!tilde\n")

    sys.stdout.flush()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
