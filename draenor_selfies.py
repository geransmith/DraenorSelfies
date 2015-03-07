#!/usr/bin/env python
# -*- coding: utf-8 -*-

# imports the tweepy stuff, time for scheduling, and sys for reading a file
import tweepy, time, sys, json
from pprint import pprint

#enter the corresponding information from your Twitter application:
consumer_key = '123456' #keep the quotes, replace this with your consumer key
consumer_secret = '123456' #keep the quotes, replace this with your consumer secret key
access_token = '123456' #keep the quotes, replace this with your access token
access_token_secret = '123456' #keep the quotes, replace this with your access token secret

# retweet function
def doRetweet(id_string):
    print 'WE MADE IT INTO doRetweet'
    print id_string
    # authenticate against the Twitter API
    api = tweepy.API(auth)
    # actually do the retweet
    api.retweet(id_string)
    print 'I did the retweet'
    print ''
    return

# This is the listener, responsible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        is_data_good = 0
        
        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
        print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        # looks at the json and see if we have pic.twitter.com there somewhere
        if 'pic.twitter.com' in data and "selfie" in decoded['text']:
            print 'pic.twitter.com was found in the data stream'
            is_data_good = 1
        
        # looks at the decoded text to see if they are talking about achievements
        if "Achievement" in decoded['text']:
            print 'Achievement found in the tweet'
            is_data_good = 0
            
        # We don't retweet retweets
        if "retweeted_status" in data:
            print 'retweeted_status was found in the data stream'
            is_data_good = 0
        
        # Check to see if the data was decided to be good
        if is_data_good == 1:
            print 'Data was deemed good'
            tweet_id = decoded['id_str']
            doRetweet(tweet_id)
        else:
            print 'Data was determined to be bad'
            print ''

        return True

    def on_error(self, status):
        print status
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False
	    
try:
    if __name__ == '__main__':
        l = StdOutListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        print "Showing all new tweets for #warcraft:"

        # There are different kinds of streams: public stream, user stream, multi-user streams
        # In this example follow #warcraft tag
        # For more details refer to https://dev.twitter.com/docs/streaming-apis
        stream = tweepy.Stream(auth, l)
        stream.filter(track=['#warcraft'], languages=['en'])
except KeyboardInterrupt:
    sys.exit()
