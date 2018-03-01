import json

def main():
    data = {}
    tweet_sentiment = ["positive", "negative", "netrual"]
	airlines = ["American", "Delta", "United", "Southwest", "Alaska"]

    tweet_count_positive = []
    tweet_count_negative = []
    tweet_count_neutral = []
    tweet_count = {"positive": tweet_count_positive, "negative": tweet_count_negative, "neutral": tweet_count_neutral}

    tweet_count_total = []

    tweet_percentage_positive = []
    tweet_percentage_negative = []
    tweet_percentage_neutral = []
    tweet_percentage = {
        "positive": tweet_percentage_positive,
        "negative": tweet_percentage_negative,
        "neutral": tweet_percentage_neutral
    }

    dates = []

    american = []
    delta = []
    united = []
    southwest = []
    alaska = []
    tweet_negative_count = {
        "American": american,
        "Delta": delta,
        "United": united,
        "Southwest": southwest,
        "Alaska": alaska
    }

    with open('graph.json', 'w') as outfile:  
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
