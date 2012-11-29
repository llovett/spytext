#!/usr/bin/env python

# TODO: differentiate between "i spy x at y", "is it z", and "mission"
#               -- reply accordingly

import email
import mailbox
import smtplib
from email.mime.text import MIMEText
import os, time
from random import choice, shuffle

# Where mail goes when sent to your "*.cs.oberlin.edu" account
#MAIL_FILE=os.environ['HOME']+"/mail/mbox"
MAIL_FILE=os.environ['HOME']+"/mbox"

# Prepositions to acknowledge
Prepositions = ("at","inside","in","on top of","on","next to","under","between")
Articles = ("a","an","the")

# How often to look at new messages (in seconds)
TIME_INTERVAL=1.0

# How many messages received so far (so we can track when we get new messages)
Received=0

# I-Spy "database" (holds information about objects that have been spied,
# where they were observered, and who has been/is on a mission to go find
# them).
SpyData = []

def parseMails():
    ''' Parses the contents of the mbox file into individual mails.
    '''

    mails = mailbox.mbox(MAIL_FILE)
    results = []
    for message in mails:
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                results.append({})
                results[-1]["content"] = part.get_payload()
                results[-1]["from"] = message['from']
                results[-1]["subject"] = message['Subject']
    
    return results

def addSpyMission(message, creator):
    ''' Takes in a message in the form of:
    
    I spy _____ (preposition) _____.

    Where the first blank is an object of interested that was
    observed, and the second blank is the location of the object. The
    case of this string is unimportant, nor are the number of
    prepositions (we'll just use the first one), or any puctuation /
    extra whitespace.

    'creator' is the creator of this mission. We track this so that we
    don't end up assigning this mission to the same person who made
    it.

    Returns a string that can be sent back as a text to the user who
    submitted this mission or None if nothing need be sent back.
    '''
    # Characters that we don't want to see in incoming messages. These will
    # be removed before being processed.
    bad_characters = "!\\:;`~@#$%^&*()_+=/,.<>\"'"
    message = message.translate(None, bad_characters)

    # Various prepositions we'll accept to separate the object from the place.
    prep = -1
    for i in xrange(len(Prepositions)):
        if " {} ".format(Prepositions[i]) in message:
            prep = i
            break

    # Not a valid message
    if prep < 0:
        return "Try texting \"i spy OBJECT at PLACE\""

    # Convert to prepositional string
    prep = " {} ".format(Prepositions[prep])
    spiedObject, prep, spiedLocation = [s.strip() for s in message.partition(prep)]

    # Remove "i spy" from the spied object, and any leading article (i.e., "the", "a", "an")
    sow = spiedObject.split()[2:]
    if sow[0] in Articles:
        sow = sow[1:]
    spiedObject = (" ".join(sow)).strip()

    # Add preposition to location, so it's more descriptive
    spiedLocation = prep + " " + spiedLocation

    # Add item and location to the set of spy missions!
    SpyData.append( {
            "item" : None,
            "location" : spiedLocation,
            "explorers" : set(),
            "creator": creator,
            "message": message
            } )
    
def giveMission(who):
    '''
    Assigns a spy mission to the person given by the parameter,
    'who'. The assignment takes place such that the person is not the
    creator of their own mission, and they have not performed this
    mission before.
    '''
    mission = None
    shuffle(SpyData)
    for d in SpyData:
        if d['creator'] != who and who not in d['explorers']:
            mission = d
            break
    if not mission:
        # This person has either created or participated in every
        # mission we have, so give a random one.
        mission = choice(SpyData)

    # Assign the mission, and give a mission statement
    mission['explorers'].add(who)
    return mission['message']

def missionGuess(who, guess):
    '''
    Checks to see if 'guess' matches up with the object currently
    being searched for in the user's mission. Returns an appropriate
    response message based on success.
    '''
    userMissions = [m for m in SpyData if who in m['explorers']]
    shortMessage = [word for word in guess.lower().split() if word not in Articles and word not in Prepositions]
    for mission in [m['object'] for m in userMissions]:
        guessCorrect = len(set(shortMessage) & set(mission.split())) >= len((mission.split()+1)/2)
        if guessCorrect:
            return "{} ---- you got it!".format(mission)
    return "nope."
    
def processMsg(mailMessage):
    content = mailMessage['content'].lower().strip()
    if content.startswith("i spy"):
        addSpyMission(content, mailMessage['from'])
    elif content.startswith("mission"):
        return giveMission(mailMessage['from'])
    elif content.startswith("is it"):
        return missionGuess(mailMessage['from'], content)
        # TODO: process the guess
        pass

def replyMail(mailMessage):
    content = mailMessage['content'].lower().strip()
    if content.startswith("i spy"):
        responseMsg = addSpyMission(content, mailMessage['from'])
    elif content.startswith("mission"):
        responseMsg = giveMission(mailMessage['from'])
    elif content.startswith("is it"):
        # TODO: process the guess
        pass

    text = "I HAVE RESPONDED!\n"+mailMessage['content']
    me = "spytext@localhost"
    you = mailMessage['from']
    response = MIMEText(text)

    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], response.as_string())
    s.quit()

# def main():
#     global Received
#     while True:
#         try:
#             mails = parseMails()
#             print "### RESULTS ###"
#             for mail in mails[Received:]:
#                 print 30*'-'
#                 print "SUBJECT: {}".format(mail['subject'])
#                 print "FROM: {}".format(mail['from'])
#                 print "CONTENT: {}".format(mail['content'])
#                 Received += 1
#                 replyMail(mail)

#             time.sleep(TIME_INTERVAL)
#         except KeyboardInterrupt, SystemExit:
#             print "Exiting..."
#             break


def main():
    # Dummy missions from the machine
    machineName = "andr0id"
    dummies = ["I spy an emergency pole between two buildings",
               "I spy something yellow and black near Stevenson",
               "I spy a message in chalk."]
    for d in dummies:
        addSpyMission(d, machineName)
    
    # Prompt nice for testing
    myName = "me"
    while len(myName) > 0:
        myName = raw_input("Give a name > ")
        msg = "asdf"
        while len(msg) > 0:
            msg = raw_input("... Enter a message: ")
            if msg == "info":
                print str(SpyData)
            else:
                print processMsg({"from":myName,"content":msg})
        
if __name__ == '__main__':
    main()
