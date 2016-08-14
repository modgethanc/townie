#!/usr/bin/python

'''
2015-2016 era ~endorphant

cndorphant bot core.
'''

import os
import random
import re
import time
import inflect

import chatter
import vtils
import beat

## bot globals

mark = 0
mine = 0
interval = 0
haunting = False
hauntChannel = ''
bones = []
ghost = ''
hauntcolor = ''
lastmsg = int(time.time())

p = inflect.engine()

BOTNAME = "cndorphbot"
ADMIN   = "endorphant"

def said(channel, user, now, msg):
    '''
    Called whenever someone speaks and did not address bot.
    '''

    global lastmsg
    global haunting
    global ghost

    response = []

    if msg.find("!rollcall") != -1:
        response.append("cndorphbot here! i'm pretty useless, but i'm doing my best. !leaderboard, !exhume {username} {yyyy-mm-dd}, !banish, !silphscope")

    elif msg.find("!leaderboard") != -1:
        response.extend(tildeboard(channel))

    elif msg.find("!tildeboard") != -1:
        response.extend(tildeboard(channel))

    elif msg.find("!exhume") != -1:
        response.extend(loadGhost(channel, user, msg))

    elif msg.find("!silphscope") != -1:
        if haunting:
            response.append("we're being haunted by "+ghost)
        else:
            response.append("there aren't any ghosts around!")

    elif msg.find("!banish") != -1:
        if haunting:
            haunting = False
            response.append("GHOST HAS BEEN BANISHED")
        else:
            response.append(user + ": i don't detect the presence of any ghosts...")

    elif msg.find("!beat") != -1:
        response.append(str(beat.main()))

    if haunting and channel == hauntChannel:
        roll = random.randrange(0,99)
        print("hauntroll: "+str(roll))
        if roll < 90:
            if len(response) < 1:
                time.sleep(2)

            response.append(haunt(channel))

    lastmsg = now

    return response

def addressed(channel, user, now, msg):
    '''
    Called when bot is addressed.
    '''

    global mark
    global mine

    response = []

    if msg.find("botsnack") != -1:
        response.append("thanks <3.")

    elif msg.find("mine some tildes") != -1:
         if user == "endorphant":
            mine = now
            response.append("roger!")
            response.append("!tilde")
         else :
            response.append("you're not the boss of me, buddy")

    elif msg.find("time") != -1:
        response.append(str(now))

    elif msg.find("<3") != -1:
        response.append(":)")

    elif msg.find("sync") != -1:
        response.append(str(mark))

    elif msg.find("mark") != -1:
        mark = now
        response.append("sync!")

    elif msg.find(":(") != -1:
        response.append("cheer up, friend, it can't be so bad")

    elif msg.find(":)") != -1:
        response.append(":D")

    elif msg.find("report") != -1:
        response.append("!tildescore")

    elif msg.find("beg") != -1:
        response.append("!tilde")

    #elif msg.find("!leaderboard") != -1:
    #    response.extend(tildeboard(channel))

    #elif msg.find("!tildeboard") != -1:
    #    response.extend(tildeboard(channel))

    #elif msg.find("commands") != -1:
    #    response.append(user + ": you can't tell me what to do!")

    #elif msg.find("get out") != -1:
    #    response.append(user + ": okay :(")
    #    ircsock.send("PART " + channel + "\n")

    elif msg.find("join") != -1:
        response.append(user + ": k")
        split = msg.split(" ");
        for x in split:
            if x.find("#") != -1:
                joinchan(x)

    elif msg.find("Answer with numbers") != -1:
        ans = doMath(msg)
        response.append(ans)

    else:
        if user != "tildebot":
            response.append(user + ": not sure what you meant by that...")

    return response

def seen(parsed):
    '''
    Called when someone joins a channel.
    '''

    global lastmsg

    if parsed.get("nick") != BOTNAME and parsed.get("channel") in ["#bots", "#bot_test"]:
        greeting = random.choice(["hi", "hey", "hello", "good morning", "good evening", "welcome"])
        diff = parsed.get("time") - lastmsg

        time.sleep(1)
        return parsed.get("nick") + ": "+greeting+"! the last time i heard from anyone else in here was "+vtils.pretty_time(diff)+" ago. "

    else:
        return

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
    global hauntcolor
    global hauntChannel
    hauntcolor = "\x03" + random.choice(['4', '8', '9', '11', '12', '13'])

    response = []

    split = messageText.split(' ')
    pattern = '^((19|20)\d{2})-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])$'

    if len(split) != 3 or not re.match(pattern, split[2]):
        response.append("valid format for this command is \"!exhume {username} {yyyy-mm-dd}\" or else i'll get confused @_@ ")
    else:
        if not os.path.isfile(loadLogs(split[2])):
            response.append("i don't have records from that date; try a different one, sorry :\\ ")
        else:
            scavengeBones(split[1], split[2])
            if len(bones) < 1:
                #print len(bones)
                response.append("i didn't find any of "+split[1]+"'s bones. are you sure that's a real person who showed up on "+split[2]+"?")
            else:
                hauntChannel = channel
                response.append("i found "+str(len(bones))+" "+p.plural("bone", len(bones))+" belonging to "+split[1]+". if that's not enough, try a different date.")

    return response

def haunt(channel):
    global bones
    global haunting

    if len(bones) == 0:
        haunting = False
        return "        ... the ghost fades away with a gentle moan ..."
    else:
        return "\x03" + random.choice(['4', '8', '9', '11', '12', '13']) + bones.pop(0) + " ..."

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
    response = []

    with open("/home/krowbar/Code/irc/tildescores.txt", "r") as scorefile:
        for idx,score in enumerate(scorefile):
            #print idx
            #print score
            board.append(score.strip("\n").split("&^%"))

    board.sort(key=lambda entry:int(entry[1]), reverse=True)

    response.append("top five tilde scores:")

    for x in range (0, 5):
        entry = board[x]
        response.append(entry[0] + " with " + entry[1] + " tildes")

    return response
