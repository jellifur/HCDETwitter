#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
#   FILE: collect_tweets.py
#   DATE: January, 2014
#   Author: David W. McDonald
#
#   A simple tweet collector for HCDE 530
#
#   Copyright by Author. All rights reserved. Not for reuse without
#   express permissions.
#
import sys, json, time, re
from datetime import datetime
from sqlalchemy.exc import *
from hcde.data.db.base.dbConfig import DBConfiguration
from hcde.data.db.example.ExampleTweetObj import ExampleTweetObj
from hcde.data.db.example.ExampleTweetsDB import ExampleTweetsDB
from hcde.data.db.example.settings_db import *
from hcde.twitter.Login import Login
from hcde.twitter.Search import Search
from hcde.twitter.auth_settings import *

import sqlite3
#nasty_unicode = u'Some example text with a sleepy face \U0001f62a and fist \U0001f44a bah!'

# This is a regular expression that matches all 
# characters which are NOT 1, 2, or 3 bytes long
# Actually, this should probably be called "MySQL_utf8_acceptable"
#
utf8_acceptable = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)

# A global flag that automatically sets whether or not we rewrite the text and usernames of
# tweets to make sure they are without specific utf8 characters. The need to do this is a
# function of a problem in the pymysql library that links the DB and SQLAlchemy to our code
REWRITE_TWEET_FLAG = True
#REWRITE_TWEET_FLAG = False


def dump_tweet(rec=None, mesg_count=None, tweet_count=None):
    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count),
    print rec['user']['screen_name'].encode('utf-8'),rec['user']['name'].encode('utf-8'),
    print ":",rec['text'].encode('utf-8')
    print

def dump_json(rec=None, mesg_count=None, tweet_count=None):
    print "[m:%3d,t:%3d]"%(mesg_count,tweet_count)
    print json.dumps(rec, sort_keys=True, indent=4)
    print


# We use a regular expression to clean the tweet of any characters
# that would generate a 4 byte utf-8 encoding. To fix this one must
# ensure that MySQL version higher than 5.5 is installed and that all
# strings be utf8mb4 (minimally). The second requirement is that the
# DB connector package must be able to handle utf8 and multi-byte
# encoding. Right now pymysql package does not handle this
def rewrite_tweet_utf8_problems(tweet=None):
    # strip invalid characters from names and if they are different
    # replace the name
    strict_utf8_uname = utf8_acceptable.sub(u'',tweet['user']['name'])        
    if( not strict_utf8_uname==tweet['user']['name'] ):
        tweet['user']['name'] = strict_utf8_uname
            
    # strip invalid characters from screen names and if they are different
    # replace the screen name
    strict_utf8_sname = utf8_acceptable.sub(u'',tweet['user']['screen_name'])        
    if( not strict_utf8_sname==tweet['user']['screen_name'] ):
        tweet['user']['screen_name'] = strict_utf8_sname

    # strip invalid characters from tweet text and if it is different
    # replace the tweet text
    try:
        strict_utf8_text = utf8_acceptable.sub(u'',tweet['text'])        
        if( not strict_utf8_text==tweet['text'] ):
            tweet['text'] = strict_utf8_text
        #if( len(tweet['text'])>300 ):
        #    tweet['text'] = tweet['text'][:300]
    except KeyError, ke1:
        strict_utf8_text = utf8_acceptable.sub(u'',tweet['full_text'])        
        if( not strict_utf8_text==tweet['full_text'] ):
            tweet['full_text'] = strict_utf8_text
        #if( len(tweet['full_text'])>300 ):
        #    tweet['full_text'] = tweet['full_text'][:300]        
    return tweet
        
        
def collection_loop(db=None, twit=None, term=None, airline_handle=None):
    tweet_count = 0
    mesg_count = 0
    total_tweets = 0
    while( twit.messages()>0 or twit.query_in_process() ):
        message_list = twit.get_message()
        mesg_count += 1
        if( message_list ):
            total_tweets = total_tweets + len(message_list)
            #print json.dumps(message_list, sort_keys=True, indent=4)
            for tweet in message_list:
                tweet_count += 1
                #dump_json(rec=tweet,mesg_count=mesg_count,tweet_count=tweet_count)
                #dump_tweet(rec=tweet,mesg_count=mesg_count,tweet_count=tweet_count)
                source = "command_line:%s"%(str(term))
                if( REWRITE_TWEET_FLAG ):
                    tweet = rewrite_tweet_utf8_problems(tweet=tweet)
                save_tweet(db=db, tweet=tweet, source=source, airline_handle=airline_handle)
        while( twit.messages()<1 and twit.query_in_process() ):
            time.sleep(2.0)
    db.commit()
    return

def save_tweet(db=None, tweet=None, source="", airline_handle=None):
    c = db.cursor()
    if( tweet and (type(tweet) is dict) ):
        tweetText = ''
        try:
            tweetText = tweet['text']
        except KeyError, ke:
            tweetText = tweet['full_text']

        if (tweet['place']):
            c.execute("INSERT OR REPLACE INTO Tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                (airline_handle, tweet['id_str'], tweet['created_at'], tweetText, tweet['retweet_count'], \
                tweet['favorite_count'], tweet['lang'], tweet['in_reply_to_status_id_str'], \
                tweet['user']['id_str'], tweet['place']['country_code'], tweet['place']['full_name'], \
                tweet['place']['place_type']))
        else:
            c.execute("INSERT OR REPLACE INTO Tweets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                (airline_handle, tweet['id_str'], tweet['created_at'], tweetText, tweet['retweet_count'], \
                tweet['favorite_count'], tweet['lang'], tweet['in_reply_to_status_id_str'], \
                tweet['user']['id_str'], None, None, None))            

        c.execute("INSERT OR REPLACE INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", \
            (tweet['user']['id_str'], tweet['user']['name'], tweet['user']['screen_name'], \
            tweet['user']['location'], tweet['user']['verified'], tweet['user']['followers_count'], \
            tweet['user']['utc_offset'], tweet['user']['time_zone']))

def parse_params(argv):
    auth = None
    user = None
    query = None
    size = 100
    cycles = 1
    airline_handle = None
    
    continuation = False
    debug = False
    json = False
    pc = 1
    while( pc < len(argv) ):
        param = argv[pc]
        if( param == "-auth"):
            pc += 1
            auth = argv[pc]
        if( param == "-user"):
            pc += 1
            user = argv[pc]
        if( param == "-query"):
            pc += 1
            query = argv[pc]
        if( param == "-page_size"):
            pc += 1
            size = int(argv[pc])
        if ( param == "-airline"):
            pc += 1
            airline_handle = argv[pc]
        
        if( param == "-cycles"):
            pc += 1
            cycles = int(argv[pc])

        if( param == "-cont"):
            continuation = True
        if( param == "-debug"):
            debug = True
        if( param == "-json"):
            json = True
        pc += 1

    return {'auth':auth, 'user':user,
            'query':query, 'json':json, 'page_size':size, 'cycles':cycles,
            'use_continuations':continuation, 'debug':debug, 'airline_handle': airline_handle }

def usage(argv):
    print "USAGE: python %s -auth <appname> -user <auth_user> -query \"<query_terms>\" [-page_size <n>] [-airline <airline handle>] [-cycles <n>] [-cont] [-debug] [-json]"%(argv[0])
    sys.exit(0)


def main(argv):
    if len(argv) < 5:
        usage(argv)
    p = parse_params(argv)
    print p
    
    twit = Search()
    twit.set_user_agent(agent="random")
    twit.set_throttling(True)

    lg = None
    if( not p['auth'] and not p['user'] ):
        print "Must have authenticating User and Application!"
        usage(argv)
        return

    if( p['auth'] ):
        app = p['auth']
        app_keys = TWITTER_APP_OAUTH_PAIR(app=p['auth'])
        app_token_fname = TWITTER_APP_TOKEN_FNAME(app=p['auth'])
        lg = Login( name="SampleTweetCollectorLoginObj",
                    app_name=p['auth'],
                    app_user=p['user'],
                    token_fname=app_token_fname)
        if( p['debug'] ):
            lg.set_debug(True)
        ## Key and secret for specified application
        lg.set_consumer_key(consumer_key=app_keys['consumer_key'])
        lg.set_consumer_secret(consumer_secret=app_keys['consumer_secret'])
        lg.login()
        twit.set_auth_obj(obj=lg)

    if( not p['query'] ):
        print "Must provide some query terms!"
        usage(argv)
    
    if( not p['airline_handle'] ):
        print "Must provide airline handle!"
        usage(argv)

    if( p['use_continuations'] ):
        print "Using Continuations for requests"
        twit.set_continuation(True)

    print "Collecting tweets for term:", p['query'].encode('utf-8')
    twit.set_query_terms(p['query'].encode('utf-8'))
    twit.set_query_result_type(rt="recent")
    twit.set_page_size(sz=p['page_size'])
    #twit.set_extended_tweet_mode(True)
    #twit.set_page_size(sz=5)

    #db_config = DBConfiguration(db_settings=DATABASE_SETTINGS['main_db'])
    #db = ExampleTweetsDB(config=db_config)
    db = sqlite3.connect('../database/AmericanAir.db')
    
    twit.start_thread()
    cycle_count = 0
    while( cycle_count < p['cycles'] ):
        cycle_count += 1
        twit.start_request()
        twit.wait_request()
        collection_loop(db=db,twit=twit,term=p['query'].encode('utf-8'), airline_handle=p['airline_handle'])
        if( cycle_count < p['cycles'] ):
            print ">>>>"
            print ">>>> Waiting a few minutes before next query."
            print ">>>>"
            time.sleep(200.0)
        
    twit.terminate_thread()
    db.close()
    return


if __name__ == '__main__':
    main(sys.argv)
