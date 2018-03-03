import json
import csv
import codecs
import datetime

def getDateCount(dates, airlines):
    airlineDateCounts = {}
    for airline in airlines:
        dateCount = [0] * len(dates)

        with codecs.open('../SentimentalAnalysis/result/'+airline+'_result.csv', 'r') as iFile:
            reader = csv.DictReader(iFile)
            for row in reader:
                date = row['created_at']
                if len(date) > 10 and row['sentiment'] == 'negative':
                    dateStr = date[8] + date[9]
                    i = dates.index('2018-02-'+dateStr)
                    if i >= 0:
                        dateCount[i] += 1

        airlineDateCounts[airline] = dateCount
    
    return airlineDateCounts

def getUniqueDates(airlines):
    dates = {}
    for airline in airlines:
        with codecs.open('../SentimentalAnalysis/result/'+airline+'_result.csv', 'r') as iFile:
            reader = csv.DictReader(iFile)
            for row in reader:
                date = row['created_at']
                if len(date) > 10:
                    dateStr = date[8] + date[9]
                    dates['2018-02-'+dateStr] = 1

    dateList = []
    for date in dates:
        dateList.append(date)
    dateList.sort()
    return dateList

def tweetCount(airlines):
    count = {}
    for airline in airlines:
        positive = 0
        negative = 0
        neutral = 0
        total = 0
        with codecs.open('../SentimentalAnalysis/result/'+airline+'_result.csv', 'r') as iFile:
            reader = csv.DictReader(iFile)
            for row in reader:
                total += 1
                if row['sentiment'] == 'positive':
                    positive += 1
                elif row['sentiment'] == 'negative':
                    negative += 1
                elif row['sentiment'] == 'neutral':
                    neutral += 1

        count[airline] = [positive, negative, neutral, total]
        
    return count

def main():
    tweet_sentiment = ["positive", "negative", "netrual"]
    airlines = ["AlaskaAir", "AmericanAir", "Delta", "SouthwestAir", "united"]

    results = tweetCount(airlines)
    tweet_count_positive = []
    tweet_count_negative = []
    tweet_count_neutral = []
    tweet_count_total = []
    for result in results:
        airList = results[result]
        tweet_count_positive.append(airList[0])
        tweet_count_negative.append(airList[1])
        tweet_count_neutral.append(airList[2])
        tweet_count_total.append(airList[3])

    tweet_count = {"positive": tweet_count_positive, "negative": tweet_count_negative, "neutral": tweet_count_neutral}

    tweet_percentage_positive = []
    tweet_percentage_negative = []
    tweet_percentage_neutral = []
    for result in results:
        airList = results[result]
        total = airList[3]
        tweet_percentage_positive.append(airList[0]*100.0/total)
        tweet_percentage_negative.append(airList[1]*100.0/total)
        tweet_percentage_neutral.append(airList[2]*100.0/total)

    tweet_percentage = {
        "positive": tweet_percentage_positive,
        "negative": tweet_percentage_negative,
        "neutral": tweet_percentage_neutral
    }

    #============================================
    dates = getUniqueDates(airlines)

    dateCounts = getDateCount(dates, airlines)
    american = dateCounts['AmericanAir']
    delta = dateCounts['Delta']
    united = dateCounts['united']
    southwest = dateCounts['SouthwestAir']
    alaska = dateCounts['AlaskaAir']
    tweet_negative_count = {
        "AmericanAir": american,
        "Delta": delta,
        "united": united,
        "SouthwestAir": southwest,
        "AlaskaAir": alaska
    }

    data = {
        'tweet_sentiment': tweet_sentiment,
        'airlines': airlines,
        'tweet_count': tweet_count,
        'tweet_count_total': tweet_count_total,
        'tweet_percentage': tweet_percentage,
        'dates': dates,
        'tweet_negative_count': tweet_negative_count
    }
    with open('graph.json', 'w') as outfile:  
        json.dump(data, outfile, indent=2)

if __name__ == '__main__':
    main()
