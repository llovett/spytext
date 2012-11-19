#!/usr/bin/env python

import re, os, time

# Where mail goes when sent to your "*.cs.oberlin.edu" account
MAIL_FILE=os.environ['HOME']+"/mail/mbox"

# How often to look at new messages (in seconds)
TIME_INTERVAL=1.0

# How many messages received so far (so we can track when we get new messages)
Received=0

def parseMails(contents):
    ''' Parses the contents of the mbox file into individual mails.
    '''
    mails = [{}]
    lines = contents.split("\n")
    i = 0

    def unfilled(field):
        try:
            return len(mails[-1][field]) == 0
        except KeyError:
            return True

    while i < len(lines):
        line = lines[i]
        if "Date: " in line and unfilled('date'):
            d = re.search("Date:(.*)", line)
            mails[-1]['date'] = d.group(1) if d else ""
        if "From: " in line and unfilled('from'):
            f = re.search("From:.*(<.*\.(edu|com|net|org)>)", line)
            mails[-1]['from'] = f.group(1)[1:-1] if f else ""
        if "boundary=" in line:
            delim = re.search("boundary=\"?([^\"]*)\"?", line).group(1)
            # Find the text/plain content
            while "text/plain" not in line.lower():
                i += 1
                line = lines[i]
            i += 1
            line = lines[i]
            # Grab the content
            linebuff = []
            while "--{}".format(delim) not in line:
                linebuff.append(line)
                i += 1
                line = lines[i]
            # At end-of-message? If not, go there.
            while "--{}--".format(delim) not in line:
                i += 1
                line = lines[i]
            # Put contents in message
            mails[-1]['content'] = ("\n".join(linebuff)).strip()
            mails.append({})
        i += 1
    # Don't return the empty dictionary at the end of the list
    return mails[:-1]

def main():
    global Received
    while True:
        try:
            with open(MAIL_FILE, "r") as mails:
                print "### RESULTS ###"
                for mail in parseMails(mails.read())[Received:]:
                    print 30*'-'
                    print "FROM: {}".format(mail['from'])
                    print "DATE: {}".format(mail['date'])
                    print "CONTENT: {}".format(mail['content'])
                    Received += 1
            time.sleep(TIME_INTERVAL)
        except KeyboardInterrupt, SystemExit:
            print "Exiting..."
            break

if __name__ == '__main__':
    main()
