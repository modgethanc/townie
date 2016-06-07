#!/usr/bin/python

'''
this chunk of code came from somewhere in the tilde.town irc botpile. i have no
idea who started it! please feel free to claim credit.

this version last modified by ~endorphant

'''

import time
import re

def format_message(message):
    '''
    Takes a raw line of input from IRC and splits it up, returning a
    tab-delineated string in the following order:

    [0] current time as int
    [1] username (truncates to 9 characters due to current
        tilde.town server settings)
    [2] irc command ('PRIVMSG', 'JOIN', 'TOPIC', etc.)
    [3] #channel (includes #)
    [4] full message
    [5] current display nick
    [6] current time as float
    '''

    # deprecated pattern:
    # pattern = r'^:.*\!~(.*)@.* (.*) (.*) :(.*)'

    pattern = r'^:(.*)\!(.*)@.* (.*) (.*) :(.*)'
    floatnow = time.time()
    now = int(floatnow)
    matches = re.match(pattern, message)
    if not matches:
        return ''

    nick = matches.group(1).strip()
    username = matches.group(2).strip()
    if username.find("~") == 0:
        username.strip('~')
    command = matches.group(3).strip()
    channel = matches.group(4).strip()
    message = matches.group(5).strip()

    return "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (now, username, command, channel,
            text, nick, floatnow)

def parse_split(message):
    '''
    Runs through the parser and returns it as a list. See parser for list ordering.
    '''

    formatted = format_message(message)

    if formatted:
        return formatted.split("\t")
    else:
        return []

def parse_dict(message):
    '''
    A more complete message parser that returns a dict, and
    conditionally formats based on whether or not each piece of
    information can be extracted from the message.
    '''

    parsed = {}

    parsed.update({"floatnow":time.time()})
    parsed.update({"time":int(parsed.get("floatnow"))})

    idSplitter = message.split('!')
    if len(idSplitter) > 1:
        username = idSplitter[1].split('@')[0]
        if username.find('~') == 0:
            ## remove ~ from username
            username = username[1:]
        parsed.update({"username": username})
        if len(idSplitter[0].split(':')) > 1:
            parsed.update({"nick":idSplitter[0].split(':')[1]})

    process = message.split(" ")
    if len(process) > 1:
        parsed.update({"command":process[1]})
    if len(process) > 2:
        parsed.update({"channel":process[2]})
    if len(process) > 3:
        text = " ".join(process[3:])
        if re.match("^:", text):
            text = text[1:]
        parsed.update({"message":text})

    return parsed
