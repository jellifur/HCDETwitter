import re
import nltk
import pandas as pd
import pickle
import os.path

###Preprocess tweets
def processTweet2(tweet):
    # process the tweets

    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet    

###get stopword list
def getStopWordList(stopWordListFileName):
    #read the stopwords file and build a list
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords

stopWords = []

# st = open('data/stopwords.txt', 'r')
stopWords = getStopWordList('data/stopwords.txt')

def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end

def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector

def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features

path_classifer = "training/naivebayes.pickle"
path_featureList = "training/featureList.pickle"
NBClassifier = None
featureList = []

if os.path.isfile(path_classifer) and os.path.isfile(path_featureList):
    classifier_f = open(path_classifer, "rb")
    NBClassifier = pickle.load(classifier_f)
    classifier_f.close()

    featureList_f = open(path_featureList, "rb")
    featureList = pickle.load(featureList_f)
    classifier_f.close()
else: 
    ###load airline sentiment training data 
        
    airlinetrain = pd.read_csv("data/Airline-Sentiment-2-w-AA.csv", encoding ="ISO-8859-1")
    tweets = []
    for i in range(len(airlinetrain)):
        sentiment = airlinetrain['airline_sentiment'][i]
        tweet = airlinetrain['text'][i]
        processedTweet = processTweet2(tweet)
        featureVector = getFeatureVector(processedTweet)
        featureList.extend(featureVector)
        tweets.append((featureVector, sentiment))

    ### Remove featureList duplicates
    featureList = list(set(featureList))

    training_set = nltk.classify.util.apply_features(extract_features, tweets)
    # # Train the classifier Naive Bayes Classifier
    NBClassifier = nltk.NaiveBayesClassifier.train(training_set)
    # #ua is a dataframe containing all the united airline tweets
    # ua['sentiment'] = ua['tweets'].apply(lambda tweet: NBClassifier.classify(extract_features(getFeatureVector(processTweet2(tweet)))))

    save_classifier = open(path_classifer,"wb")
    pickle.dump(NBClassifier, save_classifier)
    save_classifier.close()

    save_featureList = open(path_featureList,"wb")
    pickle.dump(featureList, save_featureList)
    save_featureList.close()

# # Test the classifier
# testTweet = '@AmericanAir She attempted to. But all of your employees kept passing her off to the next person and would conveniently be off duty'
# testTweet2 = 'so I went to @ChickfilA so a nice tea and lunch - where I stood next to an @AmericanAir flight attendant- Laura. https://t.co/blIYmXQkw3'
# processedTestTweet = processTweet2(testTweet)
# processedTestTweet2 = processTweet2(testTweet2)
# print NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet)))
# print NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet2)))

airlinereal = pd.read_csv("../data-csv/united.csv", encoding ="ISO-8859-1")
fakeCol = list(airlinereal['airline_handle'])
airlinereal.insert(0,'sentiment',fakeCol)

airlinereal = airlinereal.fillna("null")

# raw_data = {}
# raw_data['sentiment'] = []
num = 0
for i in range(len(airlinereal)):
    if airlinereal['airline_handle'][i].encode('utf-8').strip() == "united":
        tweet = airlinereal['tweet'][i]
        processedTestTweet = processTweet2(tweet)
        # raw_data['sentiment'].append(NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet))))
        airlinereal['sentiment'][i] = NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet)))
    else:
        # raw_data['sentiment'].append("null")
        airlinereal['sentiment'][i] = 'null'
    num += 1
    print num

# df = pd.DataFrame(raw_data, columns=['sentiment'])
# df.to_csv("result/united_result.csv")
airlinereal.to_csv("result/united_result.csv", header=True, index=False, encoding='utf-8')




