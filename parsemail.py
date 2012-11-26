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
    prepositions = ("at","inside","in","on top of","on","next to","under")
    prep = -1
    for i in xrange(len(prepositions)):
        if " {} ".format(prepositions[i]) in message:
            prep = i
            break

    # Not a valid message
    if prep < 0:
        return "Try texting \"i spy OBJECT at PLACE\""

    # Convert to prepositional string
    prep = " {} ".format(prepositions[prep])
    spiedObject, prep, spiedLocation = [s.strip() for s in message.partition(prep)]

    # Remove "i spy" from the spied object, and any leading article (i.e., "the", "a", "an")
    sow = spiedObject.split()[2:]
    articles = ("a","an","the")
    if sow[0] in articles:
        sow = sow[1:]
    spiedObject = (" ".join(sow)).strip()

    # Add preposition to location, so it's more descriptive
    spiedLocation = prep + " " + spiedLocation

    # Add item and location to the set of spy missions!
    SpyData.append( {
            "item" : spiedObject,
            "location" : spiedLocation,
            "explorers" : set(),
            "creator": creator
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
    return "i spy {} {}".format(mission['item'], mission['location'])

def replyMail(mailMessage):
    content = mailMessage['content'].lower().strip()
    if content.startsWith("i spy"):
        addSpyMission(content, mailMessage['from'])
    elif content.startsWith("mission"):
        # TODO: give a mission
        pass
    elif content.startsWith("is it"):
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
    msg = "asdf"
    while len(msg) > 0:
        msg = raw_input("Enter a message: ")
        addSpyMission(msg, "me")
    print str(SpyData)

if __name__ == '__main__':
    main()
