import sys
import sqlite3
import csv

#airline_handle: AmericanAir, Delta, *united, SouthwestAir, *AlaskaAir

def test_db():
    conn = sqlite3.connect('database/tweet.db')
    c = conn.cursor()

    #for row in c.execute('SELECT * FROM airlines'):
    #    print row
    #for row in c.execute('SELECT tweet FROM Tweets WHERE airline_handle="AlaskaAir" LIMIT 20'):
    #    print row
    #for row in c.execute('SELECT * FROM Tweets WHERE airline_handle="Delta" LIMIT 20'):
    #    print row
    for row in c.execute('SELECT COUNT(*) FROM Tweets WHERE airline_handle="united"'):
        print row
    #for row in c.execute('SELECT COUNT(*) FROM Tweets WHERE airline_handle="united" AND lang="en"'):
    #    print row

    conn.close()

def create_db():
    conn = sqlite3.connect('database/tweet.db')
    c = conn.cursor()

    # Create table
    c.execute('CREATE TABLE Airlines (name TEXT, handle TEXT PRIMARY KEY)')
    c.execute('''CREATE TABLE Users (user_id_str TEXT PRIMARY KEY, name TEXT, 
        screen_name TEXT, location TEXT, verified INTEGER, followers_count INTEGER, 
        utc_offset INTEGER, time_zone TEXT)''')

    # Date is TEXT ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS").
    # Attribute mapping deviation (API -> Database): text -> tweet
    # Comma separated values: entities_hashtags, entities_user_mentions, entities_urls
    c.execute('''CREATE TABLE Tweets (airline_handle TEXT, id_str TEXT PRIMARY KEY, created_at TEXT, tweet TEXT,
        retweet_count INTEGER, favorite_count INTEGER, lang TEXT, in_reply_to_status_id_str TEXT,
        user_id_str TEXT, place_country_code TEXT, place_full_name TEXT, place_type TEXT)''')

    # Insert our airlines into airlines
    c.execute("INSERT INTO Airlines VALUES ('American Airlines','AmericanAir')")
    c.execute("INSERT INTO Airlines VALUES ('Delta','Delta')")
    c.execute("INSERT INTO Airlines VALUES ('United Airlines','united')")
    c.execute("INSERT INTO Airlines VALUES ('Southwest Airlines','SouthwestAir')")
    c.execute("INSERT INTO Airlines VALUES ('Alaska Airlines','AlaskaAir')")

    #c.execute('''CREATE TABLE Analysis (tweet_id_str TEXT PRIMARY KEY, score INTEGER, description TEXT)''')
    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def main():
    #create_db()
    test_db()

if __name__ == '__main__':
    main()
