"""
Classify default reviews:
python sentiment.py -d 
Classify input reviews:
python sentiment.py [review1] [review2] ...
"""

import openai
import requests
from requests.auth import HTTPBasicAuth
import sys
import re

# reviews: list of (review, sentiment) tuples
# new_reviews: list of reviews to evaluate
def create_prompt(reviews, new_reviews, stop="###"):
    prompt = "This is a review sentiment classifier:\n"
    for review, sentiment in reviews:
        prompt += "Review:\n\"" + review + "\nSentiment: \"" + sentiment + "\"\n"
        prompt += stop + "\n"

    prompt += "Review text\n\n\n"
    count = 0
    for review, sentiment in reviews:
        count += 1
        prompt += str(count) + ". \"" + review + "\"\n"

    prompt += "\n\nReview sentiment ratings:\n"
    count = 0
    for review, sentiment in reviews:
        count += 1
        prompt += str(count) + ": " + sentiment + "\n"
    prompt += "\n\n" + stop + "\n"

    prompt += "Review text\n\n\n"
    count = 0
    for review in new_reviews:
        count += 1
        prompt += str(count) + ". \"" + review + "\"\n"

    prompt += "\n\nReview sentiment ratings:\n"
    prompt += "1."
    return prompt

def extract_sentiments(sentiment_str, choices):
    result = []
    start = 0
    while (start < len(sentiment_str)):
        choice = 0
        choice_ind = len(sentiment_str)
        for i in range(len(choices)):
            ind = sentiment_str.find(choices[i],start)
            if ind >= start and ind < choice_ind:
                choice = i
                choice_ind = ind
        if choice_ind < len(sentiment_str):
            result.append(choices[choice])
        start = choice_ind + len(choices[choice])
    return result

def validate_reviews(reviews,choices):
    for review, sentiment in reviews:
        if sentiment not in choices:
            return False
    return True

def create_single_prompt(reviews, new_review, stop="###"):
    prompt = "This is a review sentiment score classifier:\n"
    for review, sentiment in reviews:
        prompt += "Review:\n\"" + review + "\"\nSentiment: " + sentiment + "\n"
        prompt += stop + "\n"
    prompt += "Review:\n\"" + new_review + "\"\nSentiment score:"
    return prompt

def predict_single_sentiment(choices, new_review):
    #openai.organization = "org-RXpPxgGjA0O57LrS2a82hECn"
    openai.api_key = "sk-72WiFUFdlMZt5lPetkCYkqhPE18dnOKW2pXqX77C"
    #openai.api_key = "sk-bdqIulkQ3ddHuBtc6Sx7lyRbqOJ2SmAK23WtxGNW"

    reviews = [("I loved the new Batman movie!",
                "Positive"),
               ("I hate it when my phone battery dies",
                "Negative"),
               ("My day has been good",
                "Positive"),
               ("This is the link to the article",
                "Neutral")]
               #("My wife and I have only been here a month, but we can say without doubt that it's proven to be one of the best decisions we've made! From the quality of our living space, to the cityscape views and the friendliness and professionalism of the staff, lilli Midtown is excellent!",
               # "Positive"),
               #("Takes multiple work orders to have things done. Long response time. On site renovations allow low skilled labor crew to run wild with no supervision. Poor work being done and very disruptive to residents. Continued issues even after reporting them to management and corporate.",
               # "Negative")
               #]

    stop = "###"
    prompt = create_single_prompt(reviews, new_review, stop)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.3,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=stop
    )

    sentiments = re.findall('\d*\.?\d+',response["choices"][0]["text"])
    #extract_sentiments(response["choices"][0]["text"], choices)
    if len(sentiments) == 0:
        return None
    return sentiments[0]


def predict_sentiments(choices, new_reviews):
    #openai.organization = "org-RXpPxgGjA0O57LrS2a82hECn"
    #openai.api_key = "sk-bdqIulkQ3ddHuBtc6Sx7lyRbqOJ2SmAK23WtxGNW"
    openai.api_key = "sk-72WiFUFdlMZt5lPetkCYkqhPE18dnOKW2pXqX77C"

    reviews = [("I loved the new Batman movie!",
                "Positive"),
               ("I hate it when my phone battery dies",
                "Negative"),
               ("My day has been good",
                "Positive"),
               ("This is the link to the article",
                "Neutral"),
               ("My wife and I have only been here a month, but we can say without doubt that it's proven to be one of the best decisions we've made! From the quality of our living space, to the cityscape views and the friendliness and professionalism of the staff, lilli Midtown is excellent!",
                "Positive"),
               ("Takes multiple work orders to have things done. Long response time. On site renovations allow low skilled labor crew to run wild with no supervision. Poor work being done and very disruptive to residents. Continued issues even after reporting them to management and corporate.",
                "Negative")
               ]

    if not validate_reviews(reviews,choices):
        print("Invalid reference review sentiments")

    stop = "###"
    prompt = create_prompt(reviews,new_reviews,stop)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.3,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=stop
    )
    
    sentiments = extract_sentiments(response["choices"][0]["text"], choices)
    return sentiments[:min(len(new_reviews),len(sentiments))]

if __name__ == '__main__':
    choices = ["Positive", "Neutral", "Negative"]
    new_reviews = []
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        new_reviews = ["I like how this apartment is very spacious",
                       "Very dark, not enough sunlight",
                       "This house is very clean and organized",
                       "Definitely on the expensive side, but neat. Currently unsure",
                       "Not a fan of the service",
                       "This apartment is overpriced.",
                       "Community is great. People with dogs dont always clean up after them but staff has been on them about that. Some neighbors dont have their dogs on leashes when they take them out and others have loud dogs that we can hear from our apartment.",
                       "The apartment is not bad, though I am a little leery of the price."]

    else:
        new_reviews = sys.argv[1:]

    if len(new_reviews) == 0:
        print("No reviews found.")
    sentiments = []
    for rev in new_reviews:
        sent = predict_single_sentiment(choices, rev)
        if sent is not None:
            sentiments.append(float(sent))
    avg_score = sum(sentiments) / len(sentiments)
    print(round(avg_score, 2))

    #sentiments = predict_sentiments(choices,new_reviews)
    '''
    if len(sentiments) == 0:
        print("Error: Reviews found but no sentiments predicted")
    for choice in choices:
        percent = round(100*sentiments.count(choice)/len(sentiments))
        print(f"{choice} reviews: {percent}%")
    '''




