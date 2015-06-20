#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

### LICENSE ###
# WoW Selfie Bot
# Used to retweet selfies taken in World of Warcraft. The bot in production can be found here: https://twitter.com/WoWSelfieBot
# Copyright (C) 2015  - Geran Smith

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# If you have any issues, please post on the GitHub page for this project: <https://github.com/tehspaceg/DraenorSelfies>

# imports the tweepy stuff, datetime for rate limit, sys for reading a file, json for reading json, pushbullet for notifying me that something exploded, sleep so we can sleep when the 401 errors happen
import tweepy, sys, json
from datetime import datetime
from pushbullet import Pushbullet
from time import sleep

#enter the corresponding information from your Twitter application:
consumer_key = '123456' #keep the quotes, replace this with your consumer key
consumer_secret = '123456' #keep the quotes, replace this with your consumer secret key
access_token = '123456'#keep the quotes, replace this with your access token
access_token_secret = '123456'#keep the quotes, replace this with your access token secret

# PushBullet API code information. API key can be captured from https://www.pushbullet.com/account
pb = Pushbullet('123456')

# We assume the text files exist and are in the same location as this script
# Reads the "blocked_users" file and puts the data into the "blocked_users" variable, then closes the file (like a refrigerator)
filename=open('blocked_users.txt','r')
blocked_users=filename.readlines()
filename.close

# initialize the dictionary we will use for rate limit
rate_limit_dict = {}

# retweet function
def doRetweet(id_string):
    try:
        # actually do the retweet
        api.retweet(id_string)
        print('I did the retweet')
        print()
        return
    #since these various 401 errors occur in this method, we are going to check for them here
    except tweepy.TweepError as e:
        print('Below is the printed exception')
        print(e)
        if 'status code = 401' in str(e):
            # leaving this notification in place just in case this doesn't work
            push = pb.push_note("WowSelfieBot - TweepyError returned a 401", str(e))
            sleep(80)
            pass
        if 'status code = 404' in str(e):
            push = pb.push_note("WoWSelfieBot - TweepyError returned a 404", str(e))
            sleep(80)
            pass
        else:
            push = pb.push_note("WowSelfieBot - TweepyError has been found", str(e))
            raise e

# This is the listener, responsible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        
        # check to see if we are falling behind in the Twitter stream. This also stops processing of the current "tweet" since the other fields won't exist
        if 'warning' in decoded:
            print(decoded)
            return True
        
        # grab some data we use later
        tweet_id = decoded['id_str']
        tweet_text = decoded['text']
        tweet_user_id = decoded['user']['id_str']
        tweet_handle = decoded['user']['screen_name']
        tweet_source = decoded['source']

        # When this is 0, we will not retweet
        # Starting this out at one, since we are assuming the filter works coming in from Twitter
        is_data_good = 1

        # Print out the tweet we are inspecting
        print('@%s: %s' % (tweet_handle, tweet_text))

        # check the dictionary to see if the user has been retweeted in the past 10 minutes (600 seconds)
        if tweet_user_id in rate_limit_dict:
            print('User was found in the rate limit dictionary')
            print('Seconds between tweet time and now')
            print((datetime.now() - rate_limit_dict[tweet_user_id]).total_seconds())
            if (datetime.now() - rate_limit_dict[tweet_user_id]).total_seconds()  < 600:
                print('BAD - person has had a retweet recently')
                print()
                is_data_good = 0
                return True

        # Check the 'text' key in the decoded dictionary for the word 'Achievement'
        if 'Achievement' in tweet_text:
            print('BAD - Achievement found in the tweet')
            print()
            is_data_good = 0
            return True

        # Check the decoded dictionary for the 'retweeted_status' key
        if 'retweeted_status' in decoded:
            print('BAD - retweeted_status was found in the data stream')
            print()
            is_data_good = 0
            return True

        # Ignore tweets from users in the list
        for line in blocked_users:
            if tweet_user_id == line.rstrip():
                print('BAD - Tweet is from a person on the naughty list')
                print()
                is_data_good = 0
                return True

        # check to see if the tweet originated in World of Warcraft (NOTE: This will break if WoW changes their app name for some reason)
        if 'World of Warcraft' not in tweet_source:
            print('BAD - tweet came from {} app and not World of Warcraft'.format(tweet_source))
            print()
            is_data_good = 0
            return True

        # Check to see if the data was decided to be good
        if is_data_good == 1:
            print('Data was deemed good')
            print('Adding the user to the rate limit dictionary')
            # updates the rate_limit_dict with the time
            rate_limit_dict[tweet_user_id] = datetime.now()
            doRetweet(tweet_id)

        return True

    def on_error(self, status):
        print('The below status code was returned from Twitter')
        print(status)
        if status == 420:
            #returning False in on_error disconnects the stream
            return False
    def on_exception(self,exception):
        print(exception)
        if "'NoneType' object" in str(exception):
            push = pb.push_note("WoWSelfieBot had an AttributeError occur in on_exception", str(exception))
            print("'NoneType' object found in on_exception catch")
            return True
        else:
            print('I am in the on_exception else section')
            raise exception
try:
    if __name__ == '__main__':
        l = StdOutListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        # authenticate against the Twitter API
        # retry twice, wait five seconds between retries, only retry on 401 errors
        api = tweepy.API(auth,retry_count=2,retry_delay=5,retry_errors=[401])
        # Authenticate with the streaming API and filter what we initially receive
        # spaces are AND operators, while a comma indicates OR. More info here: https://dev.twitter.com/streaming/overview/request-parameters
        stream = tweepy.Stream(auth, l)
        try:
            stream.filter(track=['#warcraft selfie pic twitter com,#warcraft selfies pic twitter com, #wowselfie pic twitter com'], languages=['en'], stall_warnings='true')
        except AttributeError as e:
            if "'NoneType' object" in str(e):
                push = pb.push_note("WoWSelfieBot had an AttributeError occur", str(e))
                print("'NoneType' object found in try:except")
        else:
            raise e
# various exception handling blocks
except KeyboardInterrupt:
    sys.exit()
except Exception as e:
    push = pb.push_note("WoWSelfieBot had an unhandled exception in the final try/catch", str(e))
    raise e
