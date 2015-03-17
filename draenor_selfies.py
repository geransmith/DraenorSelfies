#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# imports the tweepy stuff, datetime for rate limit, and sys for reading a file
import tweepy, sys, json
from datetime import datetime

#enter the corresponding information from your Twitter application:
consumer_key = '123456' #keep the quotes, replace this with your consumer key
consumer_secret = '123456' #keep the quotes, replace this with your consumer secret key
access_token = '123456' #keep the quotes, replace this with your access token
access_token_secret = '123456' #keep the quotes, replace this with your access token secret

# We assume the text files exist and are in the same location as this script
# Reads the "blocked_users" file and puts the data into the "blocked_users" variable, then closes the file (like a refrigerator)
filename=open('blocked_users.txt','r')
blocked_users=filename.readlines()
filename.close

# initialize the dictionary we will use for rate limit
rate_limit_dict = {}

# retweet function
def doRetweet(id_string):
    # authenticate against the Twitter API
    api = tweepy.API(auth)
    # actually do the retweet
    api.retweet(id_string)
    print('I did the retweet')
    print()
    return

# This is the listener, responsible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
            
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        
        # grab some data we use later
        tweet_id = decoded['id_str']
        tweet_text = decoded['text']
        tweet_user_id = decoded['user']['id_str']
        tweet_handle = decoded['user']['screen_name']
        
        # When this is 0, we will not retweet
        is_data_good = 0
        
        # Print out the tweet we are inspecting
        print('@%s: %s' % (tweet_handle, tweet_text))
              
        # Since I can't figure out how to read the dictionary data, look at the straight json for pic.twitter.com
        # Check the 'text' key in the decoded dictionary for the word 'selfie'
        if 'pic.twitter.com' in data and 'selfie' in tweet_text:
            print('GOOD - pic.twitter.com was found in the raw JSON and selfie was found in the tweet')
            is_data_good = 1

        # check the dictionary to see if the user has been retweeted in the past 10 minutes (600 seconds)
        if tweet_user_id in rate_limit_dict:
            print('User was found in the rate limit dictionary')
            print('Seconds between tweet time and now')
            print((datetime.now() - rate_limit_dict[tweet_user_id]).total_seconds())
            if (datetime.now() - rate_limit_dict[tweet_user_id]).total_seconds()  < 600:
                print('BAD - person has had a retweet recently')
                is_data_good = 0
            
        # Check the 'text' key in the decoded dictionary for the word 'Achievement'
        if 'Achievement' in tweet_text:
            print('BAD - Achievement found in the tweet')
            is_data_good = 0
            
        # Check the decoded dictionary for the 'retweeted_status' key
        if 'retweeted_status' in decoded:
            print('BAD - retweeted_status was found in the data stream')
            is_data_good = 0
        
        # Ignore tweets from users in the list
        for line in blocked_users:
            if tweet_user_id == line.rstrip():
                print('BAD - Tweet is from a person on the naughty list')
                is_data_good = 0

        # Check to see if the data was decided to be good
        if is_data_good == 1:
            print('Data was deemed good')
            print('Adding the user to the rate limit dictionary')
            # updates the rate_limit_dict with the time
            rate_limit_dict[tweet_user_id] = datetime.now()
            doRetweet(tweet_id)
        else:
            print('Data was determined to be bad')
            print()

        return True

    def on_error(self, status):
        print('The below status code was returned from Twitter')
        print(status)
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False
            
    def on_exception(self, exception):
        print('Oh crap, we hit an exception')
        # I am kind of assuming that we should return False here to disconnect, but I think it will just crap out
        raise exception
        return False
	    
try:
    if __name__ == '__main__':
        l = StdOutListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # There are different kinds of streams: public stream, user stream, multi-user streams
        # In this example follow #warcraft tag
        # For more details refer to https://dev.twitter.com/docs/streaming-apis
        stream = tweepy.Stream(auth, l)
        stream.filter(track=['#warcraft'], languages=['en'])
except KeyboardInterrupt:
    sys.exit()
