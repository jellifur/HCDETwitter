import pandas as pd
import re

###Preprocess tweets
def processTweet2(tweet):
    # process the tweets

    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
    #Convert @username, rt, retweet to ""
    tweet = re.sub('@[^\s]+','',tweet)
    tweet = re.sub('rt','',tweet)
    tweet = re.sub('retweet','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet    

def getStopWordSet(stopWordListFileName):
    stopwords = set()
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopwords.add(word)
        line = fp.readline()
    fp.close()
    return stopwords

stopWords = getStopWordSet('../SentimentalAnalysis/data/stopwords.txt')

airlinereal = pd.read_csv("../SentimentalAnalysis/result/AmericanAir_result.csv", encoding ="ISO-8859-1")
f_positive = open("data/AmericanAir_positive.txt", "w")
f_negative = open("data/AmericanAir_negative.txt", "w")

num = 0
airlinereal.dropna(how='all')
for i in range(len(airlinereal)):
    tweet = airlinereal['tweet'][i]
    sentiment = airlinereal['sentiment'][i]
    if sentiment == "positive" or sentiment == "negative":
        tweet = processTweet2(tweet.encode('utf-8').strip())
        tweet_texts = tweet.split(" ")
        newStr = ""
        for text in tweet_texts:
            if text not in stopWords:
                newStr += text + " "
        newStr.strip()
        if sentiment == "positive":
            f_positive.write(newStr)
            f_positive.write("\n")
        elif sentiment == "negative":
            f_negative.write(newStr)
            f_negative.write("\n")
    num += 1
    print num
    
f_positive.close()
f_negative.close()