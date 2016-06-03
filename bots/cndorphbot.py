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
from optparse import OptionParser
import fileinput
import random
import re
import time as systime

import beat
import ircformatter as formatter
import inflect

#import get_users
#import mentions
#import pretty_date

mark = 0
mine = 0
interval = 0
haunting = False
bones = []
ghost = ''

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#bots',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='cndorphbot',
                  help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()

p = inflect.engine()


### meta

def ping():
  ircsock.send("PONG :pingis\n")

def sendmsg(chan , msg):
  ircsock.send("PRIVMSG "+ chan +" :"+ msg +"\n")

def joinchan(chan):
  ircsock.send("JOIN "+ chan +"\n")

def rollcall(channel):
  ircsock.send("PRIVMSG "+ channel +" :cndorphbot here! i'm pretty useless, but i'm doing my best. !leaderboard, !exhume {username} {yyyy-mm-dd}, !banish, !silphscope\n")

def connect(server, channel, botnick):
  nick = botnick
  botnick = "cndorphant"
  ircsock.connect((server, 6667))
  ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :endorphant's bot\n")
  ircsock.send("NICK "+ nick+"\n")

  joinchan(channel)

####

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

    elif msg.find("!leaderboard") != -1:
        tildeboard(channel)

    elif msg.find("!tildeboard") != -1:
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
                joinchan(x)

    elif msg.find("Answer with numbers") != -1:
        ans = doMath(msg)
        ircsock.send("PRIVMSG "+ channel +" :"+ ans + "\n")

    else:
        if user != "tildebot":
            ircsock.send("PRIVMSG "+ channel +" :" + user + ": not sure what you meant by that...\n")

####

def seen(channel, user, time, lastmsg):
    #print time
    if user != "cndorphbot" and channel == "#bots":
        greeting = random.choice(["hi", "hey", "hello", "good morning", "good evening", "welcome"])
        diff = int(time) - int(lastmsg)
        comment = "you're just in time for the chatter!"
        if diff > 60*60:
            comment = "i don't know if anyone's actually watching."
        elif diff > 60*5:
            comment = "maybe you can kick things up a notch!"

        systime.sleep(3)
        comment = ""
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": "+greeting+"! the last time i heard from anyone else in here was "+timeformat(diff)+" ago. "+comment+"\n")

def timeformat(time):
    m, s = divmod(time, 60)
    if m > 0:
        return p.no("minute", m)
    else:
        return p.no("second", s)

#### ghostmode
def loadLogs(date):
   return "logs/#tildetown tilde"+date+".txt"

def scavengeBones(corpse, date):
    global ghost
    global bones
    global haunting

    ghost = corpse
    bones = []
    logfile = open(loadLogs(date), 'r')

    for x in logfile:
        pattern = '<.'+corpse
        #if x.find(corpse+"> ") != -1:
        if re.search(pattern, x):
            line = x.rstrip().split("> ")
            line.pop(0)
            j = ''
            bones.append(j.join(line))

    haunting = True

def loadGhost(channel, user, messageText):
    split = messageText.split(' ')
    pattern = '^((19|20)\d{2})-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])$'

    if len(split) != 3 or not re.match(pattern, split[2]):
        ircsock.send("PRIVMSG "+ channel +" :"+ user + ": valid format for this command is \"!exhume {username} {yyyy-mm-dd}\" or else i'll get confused @_@ \n")
    else:
        if not os.path.isfile(loadLogs(split[2])):
            ircsock.send("PRIVMSG "+ channel +" :"+ user + ": i don't have records from that date; try a different one, sorry :\\ \n")
        else:
            scavengeBones(split[1], split[2])
            if len(bones) < 1:
                #print len(bones)
                ircsock.send("PRIVMSG "+ channel +" :"+ user + ": i didn't find any of "+split[1]+"'s bones. are you sure that's a real person who showed up on "+split[2]+"?\n")
            else:
                ircsock.send("PRIVMSG "+ channel +" :"+ user + ": i found "+str(len(bones))+" "+p.plural("bone", len(bones))+" belonging to "+split[1]+". if that's not enough, try a different date.\n") 

def haunt(channel):
    global bones
    global haunting
    if len(bones) == 0:
        haunting = False
        ircsock.send("PRIVMSG "+ channel +" :        ... the ghost fades away with a gentle moan ...\n")
    else:
        ircsock.send("PRIVMSG "+ channel +" :"+ "\x03" + random.choice(['4', '8', '9', '11', '12', '13']) + bones.pop(0) + " ...\n")

#### tildebot captcha

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
    for word in parse:
        if parseNumber(word):
            if var1 == 0:
                var1 = parseNumber(word)
            else:
                var2 = parseNumber(word)
        elif var1 != 0:
            if var2 == 0:
                calc += word + " "

   # print calc

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
            #print idx
            #print score
            board.append(score.strip("\n").split("&^%"))

    board.sort(key=lambda entry:int(entry[1]), reverse=True)

    ircsock.send("PRIVMSG " + channel + " :top five tilde scores:\n")

    for x in range (0, 5):
           entry = board[x]
           ircsock.send("PRIVMSG " + channel + " :" + entry[0] + " with " + entry[1] + " tildes\n") 

#######

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

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen()
