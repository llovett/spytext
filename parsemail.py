#!/usr/bin/env python

import re, os, threading, time

# Where mail goes when sent to your "*.cs.oberlin.edu" account
MAIL_FILE=os.environ['HOME']+"/mail/mbox"

# How often to look at new messages (in seconds)
TIME_INTERVAL=1.0

# How many messages received so far (so we can track when we get
# new messages)
Received=0

# Thread that we can stop/kill easily, so we can shut this down
# when we need to.
class MailThread (threading.Thread):
    def __init__(self,*args,**kwargs):
        super(MailThread, self).__init__(*args,**kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        if not self.stopped():
            super(MailThread, self).run()

def findSender(mail):
    # A very lazy regular expression to pull out sender's email.
    # This assumes that emails in the 'mbox' file are valid.
    result = re.search("From:.*(<.*\.(edu|com|net|org)>)", mail)
    return result.group(1)[1:-1] if result else ""

def findContents(mail):
    # Grabs MIME-type, contents, and trailing '--'
    mimeAndContent = re.search("Content-Type: text/plain.*--", mail, re.MULTILINE | re.DOTALL)
    if not mimeAndContent:return ""
    # Remove first and last lines, get only the content this way
    return "\n".join(mimeAndContent.group(0).split("\n")[1:-1]).strip()

def main():
    global Received
    while True:
        with open(MAIL_FILE, "r") as mails:
            # Read through all the new mails, but exclude the "empty mail" at the
            # end, due to the way we're splitting here (just white space as last
            # element of this list)
            for mail in re.split("--.*--", mails.read())[Received:-1]:
                print "SENDER: {}".format(findSender(mail))
                print "CONTENTS: {}".format(findContents(mail))
                Received += 1
        time.sleep(TIME_INTERVAL)

if __name__ == '__main__':
    theThread = None
    try:
        theThread = MailThread(target=main).start()
    except KeyboardInterrupt, SystemExit:
        print "Exiting..."
        theThread.stop()
        theThread.join()
        
