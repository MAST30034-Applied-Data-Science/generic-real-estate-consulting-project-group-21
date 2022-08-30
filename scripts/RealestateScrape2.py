import os
import re
import requests
import csv
import random
import time
import json

headers = {
    'Content-Type':
    'application/json',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'
}

requestMap = {
    "operationName": "searchByQuery",
    "variables": {
        "testListings": False,
        "nullifyOptionals": False,
        "testId": "RentResults",
        "recentHides": []
    },
    "extensions": {
        "persistedQuery": {
            "version":
            1,
            "sha256Hash":
            "18477afe2069ccd544b5413d468959d79ce1c0b8d3d85abbb5369c83ec3746bc"
        }
    }
}

query = {
    "channel": "rent",
    "page": 1,
    "pageSize": 25,
    "filters": {
        "surroundingSuburbs": True,
        "excludeNoSalePrice": False,
        "ex-under-contract": False,
        "ex-deposit-taken": False,
        "excludeAuctions": False,
        "furnished": False,
        "keywords": {
            "terms": ["victoria"]  # state
        },
        "petsAllowed": False,
        "hasScheduledAuction": False
    },
    "localities": []
}

url = 'https://lexa.realestate.com.au/graphql'  # api
"""
  scraping
  :number  required page number
"""


def reptile(number):
    for page in range(1, number + 1):
        query['page'] = page
        query_json = json.dumps(query)
        requestMap['variables']['query'] = query_json

        result = requests.post(url,
                               data=json.dumps(requestMap),
                               headers=headers)
        resultDict = json.loads(result.text)
        dataOut = format_json(resultDict)
        write_csv(dataOut)
        time.sleep(random.randint(3, 5))  # stop after each page, to prevent getting access denied


"""
  response message
"""


def format_json(result):
    dataOut = {
        "id": [],
        "address": [],
        "price": [],
        "propertyType": [],
        "bedrooms": [],
        "bathrooms": [],
        "parkingSpaces": [],
        "studies": [],
        "x": [],
        "y": [],
    }
    items = result['data']['rentSearch']['results']['exact']['items']
    for item in items:
        listing = item['listing']
        address = listing['address']['display']['fullAddress']  # address
        id = listing['id']  # id
        price = listing['price']['display']  # rent
        propertyType = listing['propertyType']['display']  # property type
        bedrooms = listing['generalFeatures']['bedrooms']['value']  # No of bedrooms
        bathrooms = listing['generalFeatures']['bathrooms']['value']  # No of bathrooms
        parkingSpaces = listing['generalFeatures']['parkingSpaces'][
            'value']  # parking spaces
        studies = listing['generalFeatures']['studies']['value']  # studies
        xy = getLocation(id)  # latitude x longitude y
        time.sleep(0.5)  # each address stop time in case access getting denied
        dataOut["id"].append(id)
        dataOut["address"].append(address)
        dataOut["price"].append(price)
        dataOut["propertyType"].append(propertyType)
        dataOut["bedrooms"].append(bedrooms)
        dataOut["bathrooms"].append(bathrooms)
        dataOut["parkingSpaces"].append(parkingSpaces)
        dataOut["studies"].append(studies)
        dataOut["x"].append(xy[0])
        dataOut["y"].append(xy[1])

    return dataOut


"""
 getting coordinates
 :id  property id
"""


def getLocation(id):
    reqM = {
        "query":
        "query getMapUrl($width: Int!, $height: Int!, $highDPI: Boolean!, $id: ListingId!) {\n  details: detailsV2(id: $id) {\n    listing {\n      ... on BuyResidentialListing {\n        __typename\n        parent {\n          staticMap(width: $width, height: $height, highDPI: $highDPI) {\n            url\n          }\n        }\n      }\n      ... on ResidentialListing {\n        id\n        staticMap(width: $width, height: $height, highDPI: $highDPI) {\n          url\n        }\n      }\n      ... on ProjectProfile {\n        id\n        staticMap(width: $width, height: $height, highDPI: $highDPI) {\n          url\n        }\n      }\n    }\n  }\n}\n",
        "variables": {
            "width": 640,
            "height": 230,
            "highDPI": False
        }
    }
    reqM['variables']['id'] = str(id)
    print(json.dumps(reqM))
    result = requests.post(url, data=json.dumps(reqM), headers=headers)
    resultDict = json.loads(result.text)
    urlL = resultDict['data']['details']['listing']['staticMap']['url']
    s = re.findall("%7C(.+)&signature", urlL)
    return s[0].split("%2C")


"""
  writing csv
"""


def write_csv(dataOut):
    with open('realestate.csv', mode='a', encoding='utf-8', newline='') as fd:
        csv_writer = csv.DictWriter(fd,
                                    fieldnames=[
                                        'id', 'address', 'price',
                                        'propertyType', 'bedrooms',
                                        'bathrooms', 'parkingSpaces',
                                        'studies', 'x', 'y'
                                    ])
        if os.stat('realestate.csv').st_size == 0:
            csv_writer.writeheader()
        for i in range(len(dataOut[list(dataOut.keys())[0]])):  # write each line into csv
            dic1 = {key: dataOut[key][i] for key in dataOut.keys()}
            csv_writer.writerow(dic1)
        print("successful")


if __name__ == "__main__":
    reptile(2)
