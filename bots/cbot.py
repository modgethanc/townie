#!/usr/bin/python

'''
2015-2016 era ~endorphant

this is the old cndorphbot source, ganked from a bunch of stuff all over
tilde.town. it's pretty messy; i'll clean it up someday.

this is probably not the best example if you're looking to roll your own bot;
~endorphant/projects/plaintxtmines/bin/ircbot.py is probably a better bot to
reference!

for reference:
http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
'''

import socket
import os
import sys
import random
import re
import time

import cndorphbot
import beat
import ircformatter

mark = 0
mine = 0
interval = 0
haunting = False
bones = []
ghost = ''
WPM = 120

## irc data

BOTNAME = ""
ADMIN   = ""
SERVER = ""
DEFAULTCHANS = []

CHANNELS = []
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## structural functions

def load():
    '''
    Parse config file.

    Expected format:
    IRC.SERVERNAME.NET
    #DEFAULTCHAN,#DEFAULTCHAN2,#DEFAULTCHAN3
    BOTNAME
    ADMINNAME
    '''

    global BOTNAME, ADMIN, SERVER, DEFAULTCHANS

    configfile = open("ircconfig", "r")
    config = []
    for x in configfile:
        config.append(x.rstrip())
    configfile.close()

    BOTNAME = config[2]
    ADMIN   = config[3]
    SERVER = config[0]
    DEFAULTCHANS = config[1].split(',')

def start():
    '''
    Connects and starts listening.
    '''

    load()
    connect(SERVER, DEFAULTCHANS, BOTNAME)
    listen()
    return ircsock

def reload(sock):
    '''
    TODO: Call reload on all loaded modules.
    '''

    global ircsock

    ircsock = sock
    listen()

### irc functions
def send(msg):
    '''
    Wraps the message by encoding it to bytes, then sends it.
    '''

    ircsock.send(msg.encode('ascii'))

def ping():
    '''
    Pongs the server.
    '''

    send("PONG :pingis\n")

def joinchan(chan):
    '''
    Joins named channel, and adds it to global channel list.
    '''

    global CHANNELS

    CHANNELS.append(chan)
    send("JOIN "+ chan +"\n")

def part(chan):
    '''
    Leaves named channel, and removes it from the global channel list.
    '''

    global CHANNELS

    CHANNELS.remove(chan)
    send("PART "+ chan +"\n")

def connect(server, channel, botnick):
    '''
    Connects to server, naming itself and owner, and automatically joins list
    of channels.
    '''

    ircsock.connect((server, 6667))
    send("USER "+botnick+" "+botnick+" "+botnick+" :"+ADMIN+"'s bot\n")
    send("NICK "+botnick+"\n")

    for chan in DEFAULTCHANS:
        joinchan(chan)

def disconnect():
    '''
    Disconnects from server.
    '''

    send("QUIT " + "bye!" + "\n")
    ircsock.close()

def say_now(channel, msg, nick=""):
    '''
    Sends message to single channel, with optional nick addressing, and no
    delay.
    '''

    if nick == channel: #don't repeat nick if in PM
      nick = ""
    elif nick:
      nick += ": "

    send("PRIVMSG "+channel+" :"+nick+msg+"\n")

def say(channel, msg, nick=""):
    '''
    With typing speed simulator, sends message to single channel with
    optional nick addressing.
    '''

    words = len(msg)/5.0
    cpm = WPM / 60
    delay = words / cpm

    time.sleep(delay)

    say_now(channel, msg, nick)

def multisay(channel, msglist, nick=""):
    '''
    Takes a list of messages to send, and sends them with simulated typing
    speed.
    '''

    for x in msglist:
        say(channel, x, nick)

def wall(msg, nick=""):
    '''
    Sends a single message to all CHANNELS with simulated typing speed, and
    optional nick addressing.
    '''

    for x in CHANNELS:
        say(x, msg, nick)

def multiwall(msglist, nick=""):
    '''
    Takes a list of messages to send, and sends them to all channels
    with simulated typing speed, nd optional nick addressing.
    '''
    for x in msglist:
        wall(x, nick)

##############
def admin_panel():
    return

##############

def listen():
    '''
    A loop for listening for messages.
    '''
    while 1:
        msg = ircsock.recv(2048)
        if msg:
            try:
                handle(msg.decode('ascii'))
            except UnicodeDecodeError:
                continue

def handle(msg):
    '''
    Main message handler. Reponds to ping if server pings; otherwise,
    parses incoming message and handles it appropriately.

    If the message was a PM, responds in that PM.

    If the message was from the bot owner, call admin_panel() before
    proceeding.
    '''

    msg = msg.strip('\n\r')
    print(msg)

    if msg.find("PING :") != -1:
        return ping()
    msg = msg.strip('\n\r')

    parsed = ircformatter.parse_dict(msg)
    ## floatnow, time, username, nick, message, channel, command

    print(parsed)

    ## if this is a PM, switch channel for outgoing message
    if parsed.get("channel") == BOTNAME:
        parsed.update({"channel":parsed.get("nick")})

    ## actions on join
    if parsed.get("command") == "JOIN":
        seeSay = cndorphbot.seen(parsed)
        if seeSay:
            say(parsed.get("channel"), seeSay)

    ## actions on privmsg
    if parsed.get("command") == "PRIVMSG":
        ## catch admin command
        if parsed.get("nick") == ADMIN:
            code = admin_panel(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message"))
            if code:
               return

        if parsed.get("message").find(BOTNAME+": ") == 0:
          multisay(parsed.get("channel"), cndorphbot.addressed(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message")[len(BOTNAME)+2:]))#, parsed.get("nick"))
        else:
            multisay(parsed.get("channel"), cndorphbot.said(parsed.get("channel"), parsed.get("nick"), parsed.get("time"), parsed.get("message")))

        ## other privmsg functiosn
        if haunting:
            if random.randrange(0,99)< 50:
                time.sleep(2)
                haunt(channel)


    sys.stdout.flush()

'''
DEPRECATED STUFF
def listen():
  global mine
  global interval
  global haunting

  lastmsg = int(systime.time())

  while 1:

    ircmsg = ircsock.recv(2048)
    ircmsg = ircmsg.strip('\n\r')

    if ircmsg.find("PING :") != -1:
      ping()

    split = ircmsg.split(" ")
    nick = ircmsg.split("!")[0].split(":")[1]

    if split[1] == "PRIVMSG":
        lastmsg = int(systime.time())

    if split[1] == "JOIN":
        #if split[2].split(":")[1] == "#bots":
        if nick != "cndorphbot":
            #seen(split[2].split("#")[1], nick, int(systime.time()), lastmsg)
            seen(split[2], nick, int(systime.time()), lastmsg)

    #formatted = formatter.format_message(ircmsg)

    #if formatted == "":
    #    formatted = "\t\t\t\t"

    split = formatter.parse_split(ircmsg)
    #split = formatted.split("\t")

    while len(split) < 6:
        # padding for assignments
        split.append("")

    time = split[0]
    user = split[1]
    nick = split[5]
    command = split[2]
    channel = split[3]
    messageText = split[4]

    #print command
    print(ircmsg)

    if command == "PRIVMSG" and channel == "#bot_test":
        lastmsg = time

    if mine > 0:
        try:
            interval = int(time)-int(mine)
        except ValueError:
            pass

    if interval >= 60*60:
        mine = time
        ircsock.send("PRIVMSG "+ channel +" :!tilde\n")

    if haunting:
        if random.randrange(0,99)< 50:
            systime.sleep(2)
            haunt(channel)

    #if command == "JOIN":
        #seen(channel, user, time, lastmsg)

    if ircmsg.find(":!rollcall") != -1:
      rollcall(channel)

    elif ircmsg.find(":!leaderboard") != -1:
        tildeboard(channel)

    elif ircmsg.find(":!tildeboard") != -1:
        tildeboard(channel)

    elif ircmsg.find(":!exhume") != -1:
        loadGhost(channel, user, messageText)

    elif ircmsg.find(":!silphscope") != -1:
        if haunting:
            ircsock.send("PRIVMSG "+ channel +" :we're being haunted by "+ghost+"\n")
        else:
            ircsock.send("PRIVMSG "+ channel +" :there aren't any ghosts around!\n")

    elif ircmsg.find(":!banish") != -1:
        if haunting:
            haunting = False
            ircsock.send("PRIVMSG "+ channel +" :GHOST HAS BEEN BANISHED\n")
        else:
            ircsock.send("PRIVMSG "+ channel + " :"+ user + ": i don't detect the presence of any ghosts...\n")

    elif ircmsg.find(":!beat") != -1:
            ircsock.send("PRIVMSG "+ channel +" :"+str(beat.main())+"\n")
    elif ircmsg.find(":cndorphbot: ") != -1 or ircmsg.find(":cndorphbo: ") != -1:
       addressed(messageText, channel, nick, time)

    sys.stdout.flush()
'''
