# testAPI.py - just for testing printout of the API
# PREREQS: TomTom API Key, GPS coords, internet access

import math
import json
# GET requests to TomTom API are made using this package: https://2.python-requests.org/en/master/
import requests



def stupidRound(value, up):
	if up == 1:
		value = float(int(math.ceil(value * 1000))) / 1000
		return value
	else:
		value = float(int(math.floor(value * 1000))) / 1000
		return value


def main():
	print("Please enter your desired filename (file will be JSON, do not leave blank): ")
	fileName = str(input())
	fileName = fileName.strip()
	if len(fileName) == 0:
		fileName = str('blank')

	fileWriter = open(fileName + '.json', 'w')

	print("Please enter your API key (leave blank for default): ")
	apiKey = str(input())
	apiKey = apiKey.strip()

	# DO NOT RUN THIS KEY IN PRODUCTION. FOR TEST USE ONLY. TEST USING YOUR OWN KEY.
	if len(apiKey) == 0:
		apiKey = str('KOlZazpVGjznzL2TJzBoJcOqNmxpVuGz')

	# please don't enter garbage data into this part I don't have the mental effort to make this robust
	# shit gets autorounded to three decimals so fuck precision

	"""
	print("Please enter bounding box westmost long: ")
	farWest = float(input())
	farWest = stupidRound(farWest, False)

	print("Please enter bounding box eastmost long: ")
	farEast = float(input())
	farEast = stupidRound(farEast, True)

	print("Please enter bounding box northmost lat: ")
	farNorth = float(input())
	farNorth = stupidRound(farNorth, True)

	print("Please enter bounding box southmost lat: ")
	farSouth = float(input())
	farSouth = stupidRound(farSouth, False)
	"""
	farWest = -73.508
	farEast = -69.928
	farNorth = 42.886
	farSouth = 41.237

	# let's see how many fucking divisions we need.
	# the minimum box size will be goal of 10x10 miles for 'resolution'
	# minimum x (i.e. E/W) division size is 0.19 'longitude' units capped at a max of 50
	# minimum y (i.e. N/S) division size is 0.33 'latitude' units capped at a max of 15
	# really don't fucking care how this works or if it gets screwed near equator it's a good rule of thumb

	ewDivLength = 0.19
	nsDivLength = 0.33

	ewDivNum = int(math.ceil((farEast - farWest) / ewDivLength))
	nsDivNum = int(math.ceil((farNorth - farSouth) / nsDivLength))

	if ewDivNum > 50:
		ewDivNum = 50
		ewDivLength = stupidRound((farEast - farWest) / ewDivNum, True)

	if nsDivNum > 15:
		nsDivNum = 15
		nsDivLength = stupidRound((farNorth - farSouth) / nsDivNum, True)

	farEast = stupidRound((farWest + ewDivLength * ewDivNum), True)
	farNorth = stupidRound((farSouth + nsDivLength * nsDivNum), True)

	apiParameters = {
		'key': apiKey,
		'typeahead': True,
		'limit': 100,
		'ofs': 0,
		'countrySet': 'US',
		'topLeft': '',
		'btmRight': '',
		'categorySet': '9361023, 7332005, 9361066, 9361051, 9361009'
	}
	apiQuery = str('https://api.tomtom.com/search/2/categorySearch/.json');

	# tricky bits

	isExhausted = [[0 for EW in range(ewDivNum)] for NS in range(nsDivNum)]
	globalExhausted = False
	apiCallSafe = True

	totalCallCount = 0
	totalDataCount = 0
	totalGlobalCount = -1
	data = {}
	data['summary'] = []
	data['summary'].append({
		'numResults': totalDataCount
	})
	data['results'] = []

	# fileWriter = open(fileName + '.json', 'w+')
	fileWriter.write(json.dumps(data, sort_keys=True, indent=4))
	# print(json.dumps(data, sort_keys=True, indent=4))

	while (not globalExhausted) and apiCallSafe:
		fileWriter = open(fileName + '.json', 'w+')
		fileWriter.write(json.dumps(data, sort_keys=True, indent=4))
		globalExhausted = True
		totalGlobalCount += 1
		if totalGlobalCount == 19 :
			apiCallSafe = False
		for EW in range(ewDivNum):
			localWest = farWest + EW * ewDivLength
			localEast = farWest + (EW + 1) * ewDivLength
			for NS in range(nsDivNum):
				if isExhausted[NS][EW]:
					continue

				localSouth = farSouth + NS * nsDivLength
				localNorth = farSouth + (NS + 1) * nsDivLength

				topLeftStr = str(round(localNorth, 3)) + ", " + str(round(localWest, 3))
				btmRightStr = str(round(localSouth, 3)) + ", " + str(round(localEast, 3))

				apiParameters['topLeft'] = topLeftStr
				apiParameters['btmRight'] = btmRightStr
				apiParameters['ofs'] = totalGlobalCount * 100

				response = requests.get(apiQuery, params=apiParameters)
				while True:
					try:
						jsonResponse = response.json()
						break
					except:
						response = requests.get(apiQuery, params=apiParameters)

				# general info stuff/see if there's still stuff left
				if jsonResponse['summary']['totalResults'] > jsonResponse['summary']['numResults'] + \
						jsonResponse['summary'][
							'offset']:
					globalExhausted = False
				else:
					isExhausted[NS][EW] = True

				# parse results in
				for eachStore in jsonResponse['results']:
					"""
					uniqueID = eachStore['id']
					isUnique = True
					for existStore in data['results']:
						if uniqueID == existStore['id']:
							isUnique = False
							break

					if isUnique:
					"""
					data['results'].append(eachStore)
					totalDataCount += 1
					for sumData in data['summary']:
						sumData['numResults'] = totalDataCount
						# print('...')

				totalCallCount += 1

				print(totalDataCount)
				if totalCallCount > 1000:
					apiCallSafe = False

	print(ewDivNum)
	print(nsDivNum)
	print('\n\n')
	print(totalDataCount)
	print(totalCallCount)
	fileWriter.write(json.dumps(data, sort_keys=True, indent=4))

main()
