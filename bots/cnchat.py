#!/usr/bin/python

# cndorphant version of kvincent/kchat.py

import random
import inflect

p = inflect.engine()

def rainbow(msg):
  msgsplit = []
  msgsplit[:0] = msg
  colors = ['4', '8', '9', '11', '12', '13']
  k = 0

  response = []

  for x in msgsplit:
    response.append("\x03" + colors[k] + x)
    k = (k+1) % len(colors)

  return "".join(response)

def say(keyword):
  if keyword is "bro":
    return random.choice(["bro", "broski", "dude", "pal", "chap", "buddy", "kid", "broslice", "homeslice", "brohammed", "brolshevik"])
  elif keyword is "affirm":
    return random.choice(["sure", "okay", "right", "yeah", "yep", "fine", "alright"])
  elif keyword is "neg":
    return random.choice(["sorry", "nah", "negatory", "uh-uh", "womp womp"])
  elif keyword is "ask":
    return random.choice(["ask", "check with", "pester", "beg"])
  elif keyword is "affection":
    return random.choice(["<3", "aw thanks, "+say("bro"), ":)"])
  elif keyword is "np":
    return random.choice(["my pleasure, "+say("bro"), "sure thing, "+say("bro"), "whatever, no biggie", "all cool", "yep"])
  elif keyword is "greet":
    return random.choice(["sup", "hey", "hi", "yo", "how you doin"])
  elif keyword is "awake":
    return random.choice([ "awake", "here", "up", "listening", "chillin", "running", "back", "around", "doing alright"])
  elif keyword is "sleep":
    return random.choice([ "bedtime", "peace out", "laters", "see y'all", "wandering off", "naptime", "smoke break brb", "afk", "'night"])
  elif keyword is "watching":
    return random.choice(["watching", "alert", "supervising", "staring", "keeping an eye out", "paying attention"])
  elif keyword is "enter": #room greeting
    return say("greet")+" "+p.plural(say("bro"))+", i'm "+say(random.choice(['awake', 'watching']))+" now"
  elif keyword is "spotted": #ksentry
    return random.choice(["someone's here!", "i can see the light", "i was trying to sleep", "do you know who that is?", "i see you there"])
  elif keyword is "quiet": #ksentry
    return random.choice(["it's so dark here", "no worries", "it's all cool", "they're gone", "call off the guns"])
  elif keyword is "nothing": 
    return random.choice(["whatever, "+say("bro"), "...", "i don't care", "shut up", "ffff", "maybe later", "ugh", "why do you talk to me", "you're such a tryhard", "got nothin, "+say("bro"), "nothin to say to that, "+say("bro"), "who cares", "blah blah blah", "i'll think about it", "not bad", "cool shit", "i believe you", "<_<", ">_>", "-_-", "suuure", "thanks."])
  elif keyword is "judge":
    return random.choice(["a+", "boring", "sweet", "great", "cool", "trite", "dumb", "so-so", "overdone"])
  elif keyword is "defy":
    return random.choice(["i don't have to do anything i don't want to do", "can it, "+say("bro"), "i really only listen to $BOSS", "up yours", "dicks up your ass, "+say("bro")])
  elif keyword is "http":
    return random.choice(["dude no one cares", "wowwww.", "didn't this just happen?", "old fucking news", "i can't fucking believe it", "could they be trying any harder", "i'd pay for that", "totally fake", "who cares"])
  elif keyword is "yawn":
    return random.choice(["yawn", "blah blah blah", say("wonder")+" the "+say("thing")+" is in "+say("place")+" "+say("time")])
  elif keyword is "time":
    return random.choice(["today", "right now", "tonight", "tomorrow", "next week", "these days"])
  elif keyword is "place":
    return random.choice(["nebraska", "wean hall", "yosemite", "pakistan", "mongolia", "tripoli", "reykjavik", "your mom's backyard", "the erie canal", "kansas", "fuddle", "pennsyltucky"])
  elif keyword is "thing":
      return random.choice(["weather", "food", "bot-friendliness", "economy", "tax rate", "literacy rate"])
  elif keyword is "wonder":
    return random.choice(["i wonder what", "what do you think", "hey "+say("bro")+", do you know what"])
  elif keyword is "tweetcomment":
    return random.choice(["a+", "boring", "sweet", "great", "cool", "trite", "dumb", "so-so", "overdone"])
  else:
    return ''
