import csv
import sys

csv.field_size_limit(sys.maxsize)
def constrain(minCost=0, maxCost=1000, minPeople=0, maxPeople=1000, minSent=0, maxSent=1):
	constrainIdToData = {}
	with open("id_to_data.tsv", "r") as f:
		for line in csv.reader(f, delimiter='\t'):
			line = line[1:]
			if line[0].isnumeric() and maxPeople >= int(line[5]) >=minPeople and maxCost >= float(line[6]) >= minCost and maxSent >= float(line[7]) >= minSent:
				revArr = line[1].split("[QWERTY123]")
				constrainIdToData[int(line[0])] = (revArr, [float(line[2]), float(line[3])], str(line[4]), int(line[5]), float(line[6]), float(line[7]))
	return constrainIdToData