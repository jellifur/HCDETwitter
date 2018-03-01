import csv
import codecs

def main():
    with open('chiSquared.csv', 'w') as oFile:
        chi = csv.writer(oFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        chi.writerow(['airline', 'positive', 'negative', 'neutral'])

        positive = 0
        negative = 0
        neutral = 0

        with codecs.open('../SentimentalAnalysis/result/sentiment_result.csv', 'r') as iFile:
            reader = csv.DictReader(iFile)
            for row in reader:
                if row['sentiment'] == 'positive':
                    positive += 1
                elif row['sentiment'] == 'negative':
                    negative += 1
                elif row['sentiment'] == 'neutral':
                    neutral += 1
        
        chi.writerow(['airline', positive, negative, neutral])


if __name__ == '__main__':
    main()
