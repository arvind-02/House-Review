import logging

import azure.functions as func

import openai
import requests
from requests.auth import HTTPBasicAuth
import sys
import pathlib

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

def predict_sentiments(choices, new_reviews):
	openai.organization = "org-RXpPxgGjA0O57LrS2a82hECn"
	openai.api_key = "sk-72WiFUFdlMZt5lPetkCYkqhPE18dnOKW2pXqX77C"

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

	if not validate_reviews(reviews,choices):
		print("Invalid reference review sentiments")

	stop = "###"
	prompt = create_prompt(reviews,new_reviews,stop)
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
	return sentiments[:min(len(new_reviews),len(sentiments))]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(func)
    logging.info('Python HTTP trigger function processed a request.')

    choices = ["Positive", "Neutral", "Negative"]
    new_reviews = ["I like how this apartment is very spacious",
                    "Very dark, not enough sunlight",
                    "This house is very clean and organized",
                    "Definitely on the expensive side, but neat. Currently unsure",
                    "Not a fan of the service",
                    "This apartment is overpriced.",
                    "Community is great. People with dogs dont always clean up after them but staff has been on them about that. Some neighbors dont have their dogs on leashes when they take them out and others have loud dogs that we can hear from our apartment.",
                    "The apartment is not bad, though I am a little leery of the price."]
    name = req.params.get('name')
    f = open(pathlib.Path(__file__).parent / 'test.txt', "r")
    # sentiments = predict_sentiments(choices, new_reviews)
    # logging.info(sentiments)
    # for choice in choices:
    #     percent = round(100*sentiments.count(choice) / len(sentiments))
    #     logging.info(f"{choice} reviews: {percent}%")

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             f"This HTTP triggered function executed successfully. {f.read()} Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )