#!/usr/bin/env python

# TODO: differentiate between "i spy x at y", "is it z", and "mission"
#               -- reply accordingly

import email
import mailbox

import os, time

# Where mail goes when sent to your "*.cs.oberlin.edu" account

MAIL_FILE=os.environ['HOME']+"/mbox"

# How often to look at new messages (in seconds)
TIME_INTERVAL=1.0

# How many messages received so far (so we can track when we get new messages)
Received=0

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

def main():
    global Received
    while True:
        try:
            mails = parseMails()
            print "### RESULTS ###"
            for mail in mails[Received:]:
                print 30*'-'
                print "SUBJECT: {}".format(mail['subject'])
                print "FROM: {}".format(mail['from'])
                print "CONTENT: {}".format(mail['content'])
                Received += 1
            time.sleep(TIME_INTERVAL)
        except KeyboardInterrupt, SystemExit:
            print "Exiting..."
            break

if __name__ == '__main__':
    main()
