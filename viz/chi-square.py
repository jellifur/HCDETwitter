import csv
import codecs

def writeFile(airline, oFile):
    positive = 0
    negative = 0
    neutral = 0

    with codecs.open('../SentimentalAnalysis/result/'+airline+'_result.csv', 'r') as iFile:
        reader = csv.DictReader(iFile)
        for row in reader:
            if row['sentiment'] == 'positive':
                positive += 1
            elif row['sentiment'] == 'negative':
                negative += 1
            elif row['sentiment'] == 'neutral':
                neutral += 1
    
    oFile.writerow([airline, positive, negative, neutral])

def main():
    with open('chiSquared.csv', 'w') as oFile:
        chi = csv.writer(oFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        chi.writerow(['airline', 'positive', 'negative', 'neutral'])

        writeFile('AlaskaAir', chi)
        writeFile('AmericanAir', chi)
        writeFile('Delta', chi)
        writeFile('SouthwestAir', chi)
        writeFile('united', chi)

if __name__ == '__main__':
    main()
