#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# imports the tweepy stuff, time for scheduling, and sys for reading a file
import tweepy, time, sys, json

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
        
        # When this is 0, we will not retweet
        is_data_good = 0
        
        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
        print('@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore')))
        
        # Since I can't figure out how to read the dictionary data, look at the straight json for pic.twitter.com
        # Check the 'text' key in the decoded dictionary for the word 'selfie'
        if 'pic.twitter.com' in data and 'selfie' in decoded['text']:
            print('GOOD - pic.twitter.com was found in the raw JSON and selfie was found in the tweet')
            is_data_good = 1
                  
        # Check the 'text' key in the decoded dictionary for the word 'Achievement'
        if 'Achievement' in decoded['text']:
            print('BAD - Achievement found in the tweet')
            is_data_good = 0
            
        # Check the decoded dictionary for the 'retweeted_status' key
        if 'retweeted_status' in decoded:
            print('BAD - retweeted_status was found in the data stream')
            is_data_good = 0
        
        # Ignore tweets from users in the list
        for line in blocked_users:
            if decoded['user']['id_str'] == line.rstrip():
                print('BAD - Tweet is from a person on the naughty list')
                print(line.rstrip())
                is_data_good = 0

        # Check to see if the data was decided to be good
        if is_data_good == 1:
            print('Data was deemed good')
            tweet_id = decoded['id_str']
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
