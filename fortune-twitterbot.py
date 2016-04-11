#! /usr/bin/python
from twython import Twython 
# Get our credentials from authentication.py. These consist of 4 vars,
# APP_KEY, APP_SECRET, OAUTH_TOKEN, and OAUTH_TOKEN_SECRET
from authentication import *
import subprocess
import datetime
import time

def main():
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    startup = True 
    lastCheck = time.time()
    statusUpdate = time.time()
    running = True 
    while running:
        if startup:
            # Set a limit for how far back we read. Things that were sent to us
            # before we powered on won't get read.
            startTime = datetime.datetime.utcnow().isoformat()
            limitTweet = twitter.update_status(status="Powered on at " +
                                               startTime)
            lastRead = datetime.datetime.strptime(limitTweet['created_at'],
                                                  '%a %b %d %H:%M:%S %z %Y')
            startup = False
            selfCheckTime = time.time()

        if (time.time() - lastCheck >= 90):
            # Every minute and a half, create a dictionary consisting of each
            # user's handle and the request they make. 
            lastCheck = time.time()
            userRequests = [] 
            mentions = twitter.get_mentions_timeline()
            for i in mentions:
                tweetTimestamp = datetime.datetime.strptime(i['created_at'],
                                                  '%a %b %d %H:%M:%S %z %Y')
                if tweetTimestamp <= lastRead:
                    # Stop if we've read this tweet already.
                    break
                else:
                    user = '@' + i['user']['screen_name'] + ' '
                    request = i['text']
                    userRequests.append({'user':user, 'request':request,
                                         'timestamp':tweetTimestamp})

            # Now that we've gotten our mentions we're going to go through and
            # fulfill each user's request.
            for i in userRequests:
                lastRead = i['timestamp']
                maxLength = 140 - len(i['user'])
                if ('fortune' in i['request']):
                    process = subprocess.run(['fortune', '-s', '-n ' + 
                                             str(maxLength)], 
                                             stdout=subprocess.PIPE)
                    # Convert our subprocess object's output to a string
                    fortune = ''
                    for j in process.stdout:
                        fortune += chr(j)
                    fortune = fortune.strip('\n')
                    twitter.update_status(status=user + fortune)
                    del userRequests[userRequests.index(i)]
        
        #If it's been an hour since running a self-check, we'll do that here.
        if (time.time() - selfCheckTime >= 3600):
            twitter.update_status(status = 'Self-check at ' + 
                                  datetime.datetime.utcnow().isoformat())
            selfCheckTime = time.time()


main()
