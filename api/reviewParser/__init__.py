import logging

import azure.functions as func

import csv
import openai
import requests
from requests.auth import HTTPBasicAuth
import sys
import pathlib
import json


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
			ind = sentiment_str.find(choices[i], start)
			if ind >= start and ind < choice_ind:
				choice = i
				choice_ind = ind
		if choice_ind < len(sentiment_str):
			result.append(choices[choice])
		start = choice_ind + len(choices[choice])
	return result


def validate_reviews(reviews, choices):
	for review, sentiment in reviews:
		if sentiment not in choices:
			return False
	return True


def predict_sentiments(choices, new_reviews):
	openai.organization = "org-8NXhOCMcghGLJOumnG62SWh1"
	openai.api_key = "sk-hkLYOFvStc3NgQKLWmXlCnrF858whicNIIgPTZP3"

	reviews = [("I loved the new Batman movie!",
				"Positive"),
    		   ("I hate it when my phone battery dies",
    		   	"Negative"),
    		   ("My day has been 👍",
    		   	"Positive"),
    		   ("This is the link to the article",
    		   	"Neutral"),
    		   ("My wife and I have only been here a month, but we can say without doubt that it's proven to be one of the best decisions we've made! From the quality of our living space, to the cityscape views and the friendliness and professionalism of the staff, lilli Midtown is excellent!",
    		   	"Positive"),
    		   ("Takes multiple work orders to have things done. Long response time. On site renovations allow low skilled labor crew to run wild with no supervision. Poor work being done and very disruptive to residents. Continued issues even after reporting them to management and corporate.",
    		   	"Negative")
    		   ]

	if not validate_reviews(reviews, choices):
		print("Invalid reference review sentiments")

	stop = "###"
	prompt = create_prompt(reviews, new_reviews, stop)
	response = openai.Completion.create(
    	engine="davinci",
    	prompt=prompt,
    	temperature=0.2,
    	max_tokens=60,
    	top_p=1.0,
    	frequency_penalty=0.0,
    	presence_penalty=0.0,
		stop=stop
    )

	sentiments = extract_sentiments(response["choices"][0]["text"], choices)
	return sentiments[:min(len(new_reviews), len(sentiments))]


def main(req: func.HttpRequest) -> func.HttpResponse:
    minPeople = int(req.params.get('minPeople'))
    maxPeople = int(req.params.get('maxPeople'))
    minPrice = float(req.params.get('minPrice'))
    maxPrice = float(req.params.get('maxPrice'))
    minScore = float(req.params.get('minScore'))

    idToRev = {}
    with open(pathlib.Path(__file__).parent / "reviews1.csv", 'r') as f:
        for line in csv.reader(f):
            if line[0].isnumeric():
                if int(line[0]) in idToRev:
                    idToRev[int(line[0])].append(line[5])
                else:
                    idToRev[int(line[0])] = [line[5]]

    idToLatLong = {}
    idToURL = {}
    idToNumPeople = {}
    idToPrice = {}
    ids = []
    numDone = 0
    MAX_PLACES = 2
    with open(pathlib.Path(__file__).parent / "listings.csv", 'r') as f:
        for line in csv.reader(f):
            if numDone > MAX_PLACES:
                break
            if line[0].isnumeric():
                price = float(line[60][1:].replace(',', ''))
                numPeople = int(line[53])
                if (numPeople <= maxPeople and numPeople >= minPeople and price >= minPrice and price <= maxPrice):
                    idToLatLong[int(line[0])] = [float(line[48]), float(line[49])]
                    idToURL[int(line[0])] = str(line[1])
                    idToNumPeople[int(line[0])] = numPeople
                    idToPrice[int(line[0])] = price
                    ids.append(int(line[0]))
                    numDone+=1
    idToData = {}
    choices = ["Positive", "Neutral", "Negative"]
    for i in ids:
        if (i not in idToRev):
            continue
        reviews = idToRev[i]
        if (len(reviews) > 5):
            reviews = reviews[:5]
        # sentiments = predict_sentiments(choices, reviews)
        # score = round(100*sentiments.count(choices[0]) / len(sentiments))
        # if (score >= minScore):
        idToData[i] = (reviews, idToLatLong[i], idToURL[i], idToNumPeople[i], idToPrice[i])
    return func.HttpResponse(
        json.dumps(idToData),
        mimetype="application/json",
        status_code=200
    )
