import pandas as pd
import requests
import json
import datetime
import csv
import time

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_8_7 rv:5.0; en-US) AppleWebKit/533.31.5 (KHTML, like Gecko) Version/4.0 Safari/533.31.5',
}

def get_pushshift_data(after, before, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?&after=' + str(after) + '&before=' + str(before) + '&subreddit=' + str(sub)
    r = requests.get(url, headers = headers)
    r.raise_for_status()
    print(url)
    print(r.status_code)
    if r.status_code != 204:
        data = json.loads(r.text)

        return data['data']
    


def collect_subData(subm):
    subData = list() #list to store data points
    title = subm['title']
    url = subm['url']

    try:
        body = subm['selftext']
    except KeyError:
        body = ''
    
    author = subm['author']
    subId = subm['id']
    score = subm['score']
    created = datetime.datetime.fromtimestamp(subm['created_utc'])
    numComms = subm['num_comments']
    permalink = subm['permalink']


    if body not in {'', '[removed]'}:
        subData.append((subId, title, body, url, author, score, created, numComms, permalink))
        subStats[subId] = subData


def update_subFile():
    upload_count = 0
    location = "./"
    print("input filename of submission file, please add .csv")
    filename = input()
    file = location + filename
    with open(file, 'w', newline= '', encoding = 'utf-8') as file:
        a = csv.writer(file, delimiter=',')
        headers = ["Post ID", "Title", "Body", "URL", "Author", "Score", "Created", "Total No. of Comments", "Permalink"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub][0])
            upload_count += 1
        print(str(upload_count) + " submissions have been uploaded into a csv file")

subStats = {}

subCount = 0

sub = 'columbia'

after = '1648843278'
before = '1666379989'

data = get_pushshift_data(after, before, sub)

while len(data) > 0:
    for submission in data:
        collect_subData(submission)
        subCount += 1
    
    print(len(data))
    print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
    after = data[-1]['created_utc']
    data = get_pushshift_data(after, before, sub)
    #
    time.sleep(0.8)

update_subFile()