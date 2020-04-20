# testAPI.py - just for testing printout of the API
# PREREQS: TomTom API Key, GPS coords, internet access


# GET requests to TomTom API are made using this package: https://2.python-requests.org/en/master/
import requests
import math
import json
import urllib.parse

def geo(address):
    apiKey = str('KOlZazpVGjznzL2TJzBoJcOqNmxpVuGz')
    encoded = urllib.parse.quote(address)
    query ='https://api.tomtom.com/search/2/geocode/' + str(encoded) + '.json?limit=1&countrySet=US&lat=42&lon=-72&topLeft=42.886%2C%20-73.508&btmRight=41.237%2C-69.928&key=' + apiKey

    response = requests.get(query)
    while True:
        try:
            jsonResponse = response.json()
            break
        except:
            response = requests.get(query)

    latit = 0
    longit = 0

    for address in jsonResponse['results']:
        latit = address['position']['lat']
        longit = address['position']['lon']
    return latit, longit

    return encoded


def reverseGeo(latit, longit):
    apiKey = str('KOlZazpVGjznzL2TJzBoJcOqNmxpVuGz')
    query = 'https://api.tomtom.com/search/2/reverseGeocode/'+str(latit)+'%2C%20' +str(longit)+'.json?returnSpeedLimit=false&heading=0&radius=50&number=0&returnRoadUse=false&key=' + apiKey
    response = requests.get(query)
    while True:
        try:
            jsonResponse = response.json()
            break
        except:
            response = requests.get(query)

    cur_address = ''

    for address in jsonResponse['addresses']:
        cur_address = address['address']['freeformAddress']
    return cur_address


def search(latit, longit):
    # DO NOT RUN THIS KEY IN PRODUCTION. FOR TEST USE ONLY. TEST USING YOUR OWN KEY.

    apiKey = str('KOlZazpVGjznzL2TJzBoJcOqNmxpVuGz')

    # please don't enter garbage data into this part I don't have the mental effort to make this robust

    apiParameters = {
        'key': apiKey,
        'typeahead': True,
        'limit': 20,
        'ofs': 0,
        'countrySet': 'US',
        'lat': latit,
        'lon': longit,
        'radius': 10000,  # 10KM

        # SWITCH BETWEEN THESE TWO DEPENDING ON WHAT CATEGORY YOU WANT
        # all
        # 'categorySet': '9361023, 7332005, 9361066, 9361051, 9361009'
        # just supermarkets
        'categorySet': '7332005'
    }
    apiQuery = str('https://api.tomtom.com/search/2/categorySearch/.json');

    response = requests.get(apiQuery, params=apiParameters)
    while True:
        try:
            jsonResponse = response.json()
            break
        except:
            response = requests.get(apiQuery, params=apiParameters)

    data = {}


    '''
    data['summary'] = []
    data['summary'].append({
        'numResults': jsonResponse['summary']['numResults']
    })
    '''
    latitude_lst = []
    longitude_lst = []
    for eachStore in jsonResponse['results']:
        latitude_lst.append(eachStore['position']['lat'])
        longitude_lst.append(eachStore['position']['lon'])
    final_lat = []
    final_lon = []
    for i in range(len(latitude_lst)):
        repeat = False
        for j in range(len(final_lat)):
            if final_lat[j] == latitude_lst[i] and final_lon[j] == longitude_lst[i]:
                repeat = True
                break
        if repeat == False:
            final_lat.append(latitude_lst[i])
            final_lon.append(longitude_lst[i])
    print(final_lat)
    print(final_lon)
    return final_lat, final_lon
