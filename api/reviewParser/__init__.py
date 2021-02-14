import logging

import azure.functions as func

import csv
import openai
import requests
from requests.auth import HTTPBasicAuth
import sys
import pathlib
import json

csv.field_size_limit(sys.maxsize)

def constrain(minCost=0, maxCost=1000, minPeople=0, maxPeople=1000, minSent=0, maxSent=1):
   constrainIdToData = {}
   with open(pathlib.Path(__file__).parent / "id_to_data.tsv", "r") as f:
      for line in csv.reader(f, delimiter='\t'):
         line = line[1:]
         if line[0].isnumeric() and maxPeople >= int(line[5]) >=minPeople and maxCost >= float(line[6]) >= minCost and maxSent >= float(line[7]) >= minSent:
            revArr = line[1].split("[QWERTY123]")
            constrainIdToData[int(line[0])] = (revArr, [float(line[2]), float(line[3])], str(line[4]), int(line[5]), float(line[6]), float(line[7]))
   return constrainIdToData

def main(req: func.HttpRequest) -> func.HttpResponse:
    minPeople = int(req.params.get('minPeople'))
    maxPeople = int(req.params.get('maxPeople'))
    minPrice = float(req.params.get('minPrice'))
    maxPrice = float(req.params.get('maxPrice'))
    minScore = float(req.params.get('minScore'))
    maxScore = float(req.params.get('maxScore'))

    idToData = constrain(minPrice, maxPrice, minPeople, maxPeople, minScore, maxScore)

    return func.HttpResponse(
        json.dumps(idToData),
        mimetype="application/json",
        status_code=200
    )