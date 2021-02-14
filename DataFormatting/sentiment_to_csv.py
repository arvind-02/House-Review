import os
import pandas as pd 
import subprocess
from sentiment import *
from csv import writer

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

df = pd.read_csv("./reviews1.csv")
id_to_sentiment = {}
count = 0
min_count = 121
max_count = 200
'''
div by zero errors:
46 (18764)
'''
for listing_id in df['listing_id'].unique():
    if (count < min_count):
        count += 1
        continue
    if (count == max_count):
        break
    count += 1
    if (count % 1 == 0):
        print(count, ":", listing_id)
    relevant_rows = df[df['listing_id'] == listing_id]
    reviews = relevant_rows['comments'].to_list()
    if len(reviews) > 10:
        reviews = reviews[:10]
    
    for i in range(len(reviews)):
        reviews[i] = "\"" + str(reviews[i]) + "\""

    choices = ["Positive", "Neutral", "Negative"]
    sentiments = []
    for rev in reviews:
        sent = predict_single_sentiment(choices, rev)
        if sent is not None:
            sentiments.append(float(sent))
    avg_score = sum(sentiments) / len(sentiments)
    append_list_as_row("./sentiments.csv", [listing_id, avg_score])
    print(avg_score)

    '''
    command = "python sentiment.py " + " ".join(reviews)
    subproc = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
    sentiment = float(subproc.stdout.read())
    del subproc
    '''

'''
    id_to_sentiment[listing_id] = round(avg_score, 2)

id_to_sentiment_df = pd.DataFrame(columns=["listing_id","sentiment"])
for listing_id in reviews:
    id_to_sentiment_df.loc[len(id_to_sentiment_df)] = [listing_id, reviews[listing_id]]

id_to_sentiment_df.to_csv("./sentiments.csv")
'''