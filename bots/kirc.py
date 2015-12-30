#!/usr/bin/python

# kbot; irc interface yanked from modgethanc/kvincent

import socket
import os
import sys
from optparse import OptionParser
import fileinput
import random
import re
import time as systime
import threading

import formatter
import cnchat
import cndorphant

configfile = open("ircconfig", 'r')
config = []
channels = []

for x in configfile:
    config.append(x.rstrip())

configfile.close()

botName = config[2]
admin   = config[3]

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default=config[0], help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default=config[1], help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default=botName, help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

### irc functions

def ping():
  ircsock.send("PONG :pingis\n")

def joinchan(chan):
  channels.append(chan)
  ircsock.send("JOIN "+ chan +"\n")

def part(chan):
  channels.remove(chan)
  ircsock.send("PART "+ chan +"\n")

def connect(server, channel, botnick):
  ircsock.connect((server, 6667))
  ircsock.send("USER "+botnick+" "+botnick+" "+botnick+" :"+admin+"\n")
  ircsock.send("NICK "+botnick+"\n")

  joinchan(channel)

def disconnect():
  ircsock.send("QUIT " +cnchat.say("sleep") + "\n")

def say(channel, msg, nick=""):
  if nick == channel: #don't repeat nick if in PM
    nick = ""
  elif nick:
    nick += ": "

  #print "trying to say: " + channel + ":>" + nick+msg
  #print ":::PRIVMSG "+channel+" :"+nick+msg+":::"
  ircsock.send("PRIVMSG "+channel+" :"+nick+msg+"\n")

def multisay(channel, msglist, nick=""):
 for x in msglist:
   say(channel, x, nick)

def wall(msg):
  global channels
  for x in channels:
    say(x, msg)

def multiwall(msglist):
  global channels
  for x in msglist:
    wall(x)

## misc helpers

## admin

def adminPanel(channel, user, time, msg):
  if msg.find(":!join") != -1:
    say(channel, "k", user)
    split = msg.split(" ")
    for x in split:
      if x.find("#") != -1:
        joinchan(x)
    return "join"

  elif msg.find(":!brb") != -1:
    say(channel, "k bye", user)
    split = msg.split(" ")
    part(channel)
    return "part"

  elif msg.find(":!gtfo") != -1:
    say(channel, "ollie outie broski")
    #print "manual shutdown"
    disconnect()
    return "die"

  elif msg.find(":!names") != -1:
    ircsock.send("NAMES "+channel+"\n")
    return "names"

  elif msg.find(":!channels") != -1:
    chanlist = " ".join(channels)
    say(channel, "i'm in "+chanlist)
    return "names"

  elif msg.find(":!wall") != -1:
    split = msg.split("!wall ")
    wallmsg = "".join(split[1])
    wall(wallmsg)

    return "wall"

### timed functions

def powerhour():
  shot = 10
  lastshot = int(systime.time())+3
  last = lastshot
  wall(cnchat.rainbow("IT'S POWER HOUR TIME EVERYONE"))
  now = int(systime.time())

  print lastshot
  print now

  while 1:
    if shot < 60:
      now = int(systime.time())
      if now-last> 0 :
        #print "tick "+str(now)
        last = now
      if ((now-lastshot) % 60 == 0):
        lastshot = now + 2
        shot += 1
        wall("3")
        systime.sleep(1)
        wall("2")
        systime.sleep(1)
        wall("1")
        systime.sleep(1)
        color = "\x03" + random.choice(['4', '8', '9', '11', '12', '13'])
        wall(color+"SHOT #"+str(shot)+" GO GO GO") 
        #print "shot #"+str(shot)
        #print "last: "+str(lastshot)
        #print "now: "+str(now)
    else:
      wall("power hour is over i hope you're fucking sloshed")
      break 

### fix your threading shit bro

def listen():
  #while 1:
    #try:
    #  thread.start_new_thread(receive(), ())
    #except KeyboardInterrupt:
    #  print "zzz"
    while 1:
      msg = ircsock.recv(2048)
      if msg:
        receive(msg)

def receive(msg):

#  try:
    #while 1:
      #msg = ircsock.recv(2048)
      msg = msg.strip('\n\r')

      print msg

      if msg.find("PING :") != -1:
      #if command == "PING":
        ping()

      msg = msg.strip('\n\r')
      process = msg.split(" ")

      nick = ""

      if len(msg.split("!")[0].split(":")) > 1:
        nick = msg.split("!")[0].split(":")[1]

      time = int(systime.time())
      user = nick
      command = ""
      channel = ""
      mode = ""
      target = ""
      message = ""

      if len(process) > 1:
        command = process[1]
      if len(process) > 2:
        channel = process[2]
      if len(process) > 3:
        if command == "MODE":
          mode = process[3]
          if len(process) > 4:
            target = process[4]
        else:
          message = " ".join(process[3:])
      print "== "+message+"\n"

      #msg = msg.strip('\n\r')
      formatted = formatter.format_message(msg)
      if formatted != "":
        user = formatted.split("\t")[1]

      #if "" == formatted:
      #  continue

      #if formatted == "":
      #    formatted = "\t\t\t\t"

      #split2       = formatted.split("\t")
      #time        = split2[0]
      #user        = split2[1]
      #command     = split2[2]
      #channel     = split2[3] #if you include the :: we can do slicker PM
      #message     = ":"+split2[4]

      #print "command: "+command+"\n"

      if nick != user: #check for weird identity stuff
          user = nick

      if msg.find("JOIN #") != -1:
        ircsock.send("MODE "+channel+" +o "+user+"\n")
        say(channel, cndorphant.seen(channel, user))

      if channel == botName:  #check for PM
        channel = user

      if user == admin:
        code = adminPanel(channel, user, time, message)
        #if code == "die":
        #  break

      if command == "PRIVMSG":
        if msg.find(":"+botName) != -1:
          multisay(channel, cndorphant.addressed(channel, user, time, message), user)
        else:
          multisay(channel, cndorphant.said(channel, user, time, message), user)

      sys.stdout.flush()
#  except KeyboardInterrupt:
#    print "zzz"
#    return

#########################
def start():
  connect(options.server, options.channel, options.nick)
  #listen()
  #thread.start_new_thread(listen(), ())

#start()
