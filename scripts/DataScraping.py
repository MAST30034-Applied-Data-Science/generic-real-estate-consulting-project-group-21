import os
import re
import requests
import csv
import random
import time
import json

pages = 80

headers = {
    'Content-Type':
        'application/json',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'
}

# query message
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
                "59978706853ca33a61836b839cd15ef4a1132f0111aa7b7c15831ca46bcaff51"  # changes every a few days
                                                                                    # public api used so the key is left here
                                                                                    # how to get it: browser's inspector element, network, locate graphql, under request payload
        }
    }
}
query = {
    "channel": "rent",
    "page": 1,
    "pageSize": 25,
    "filters": {
        "surroundingSuburbs": False,  # surrounding included or not
        "excludeNoSalePrice": False,
        "ex-under-contract": False,
        "ex-deposit-taken": False,
        "excludeAuctions": False,
        "furnished": False,  # furnished or not
        "petsAllowed": False,
        "hasScheduledAuction": False
    },
    "localities": [{
        "searchLocation": "3000"  # postcode
    }]
}

url = 'https://lexa.realestate.com.au/graphql'  # api


def reptile(number, postcode):
    """
    scrapes data
    :param number: number of pages required
    :returns: scraping result
    """
    query['page'] = number
    query['localities'][0]['searchLocation'] = str(postcode)
    query_json = json.dumps(query)
    requestMap['variables']['query'] = query_json
    # print(json.dumps(requestMap))
    result = requests.post(url, data=json.dumps(requestMap), headers=headers)
    resultDict = json.loads(result.text)
    dataOut = format_json(resultDict)
    write_csv(dataOut)
    time.sleep(random.randint(3, 5))  # stops after each page to prevent access getting denied


def format_json(result):
    """
    formats response 
    :param result: result from scraping
    :returns: data after formatting
    """
    dataOut = {
        "id": {},
        "address": {},
        "suburb": {},
        "postcode": {},
        "price": {},
        "propertyType": {},
        "bedrooms": {},
        "bathrooms": {},
        "parkingSpaces": {},
        "studies": {},
        "furnished": {},
        "latitude": {},
        "longitude": {}
    }
    global pages
    try:
        pages = result['data']['rentSearch']['results']['pagination'][
            'maxPageNumberAvailable']
        items = result['data']['rentSearch']['results']['exact']['items']
    except Exception as e:
        print('failed to get data')
        print(e)
        return dataOut
    # code for surrounding suburbs
    # if len(items) == 0:
    # items = result['data']['rentSearch']['results']['surrounding']['items']
    count = 0
    for item in items:
        listing = item['listing']
        address = listing['address']['display']['shortAddress']  # address
        suburb = listing['address']['suburb']  # suburb
        postcode = listing['address']['postcode']  # postcode
        id = listing['id']  # id
        price = listing['price']['display']  # price
        propertyType = listing['propertyType']['display']  # propertyType
        bedrooms = listing['generalFeatures']['bedrooms']['value']  # No of bedrooms
        bathrooms = listing['generalFeatures']['bathrooms']['value']  # No of bathrooms
        parkingSpaces = listing['generalFeatures']['parkingSpaces'][
            'value']  # parkingSpaces
        studies = listing['generalFeatures']['studies']['value']  # study
        xy = getLocation(id)  # latitude x longitude y
        time.sleep(0.5)  # stops after every property to prevent access getting denied
        furnished = getFurnished(id)  # furnished
        time.sleep(0.5)  # stops after every property to prevent access getting denied
        dataOut["id"][str(count)] = id
        dataOut["address"][str(count)] = address
        dataOut["suburb"][str(count)] = suburb
        dataOut["postcode"][str(count)] = postcode
        dataOut["price"][str(count)] = price
        dataOut["propertyType"][str(count)] = propertyType
        dataOut["bedrooms"][str(count)] = bedrooms
        dataOut["bathrooms"][str(count)] = bathrooms
        dataOut["parkingSpaces"][str(count)] = parkingSpaces
        dataOut["studies"][str(count)] = studies
        dataOut["furnished"][str(count)] = furnished
        dataOut["latitude"][str(count)] = xy[0]
        dataOut["longitude"][str(count)] = xy[1]
        count += 1

    return dataOut


# address
reqM = {
    "query":
        "query getMapUrl($width: Int!, $height: Int!, $highDPI: Boolean!, $id: ListingId!) {\n  details: detailsV2(id: $id) {\n    listing {\n      ... on BuyResidentialListing {\n        __typename\n        parent {\n          staticMap(width: $width, height: $height, highDPI: $highDPI) {\n            url\n          }\n        }\n      }\n      ... on ResidentialListing {\n        id\n        staticMap(width: $width, height: $height, highDPI: $highDPI) {\n          url\n        }\n      }\n      ... on ProjectProfile {\n        id\n        staticMap(width: $width, height: $height, highDPI: $highDPI) {\n          url\n        }\n      }\n    }\n  }\n}\n",
    "variables": {
        "width": 640,
        "height": 230,
        "highDPI": False
    }
}


def getLocation(id):
    """
    gets coordinates
    :param id: property id
    :returns: coordinates
    """
    reqM['variables']['id'] = str(id)
    print("obtain coordinates")
    try:
        result = requests.post(url, data=json.dumps(reqM), headers=headers)
        resultDict = json.loads(result.text)
        urlL = resultDict['data']['details']['listing']['staticMap']['url']
        s = re.findall("%7C(.+)&signature", urlL)
        print("coordinates obtained")
        return s[0].split("%2C")
    except Exception as e:
        print('failed to get coordinates')
        print(e)
        return ["None", "None"]


reqFurn = {
    "operationName": "getListingById",
    "variables": {
        "id": "425475326",
        "nullifyOptionals": False,
        "testId": "RentDetails"
    },
    "extensions": {
        "persistedQuery": {
            "version":
                1,
            "sha256Hash":
                "59978706853ca33a61836b839cd15ef4a1132f0111aa7b7c15831ca46bcaff51"  # changes every a few days
                                                                                    # public api used so the key is left here
                                                                                    # how to get it: browser's inspector element, network, locate graphql, under request payload
        }
    }
}


def getFurnished(id):
    """
    checks if furnished
    :param id: property id
    :returns: furnishing status
    """
    reqFurn['variables']['id'] = str(id)
    print("checking if furnished")
    furnished = 'N'
    try:
        result = requests.post(url, data=json.dumps(reqFurn), headers=headers)
        resultDict = json.loads(result.text)
        propertyFeatures = resultDict['data']['details']['listing'][
            'propertyFeatures']
        for propertyFeature in propertyFeatures:
            if propertyFeature['displayLabel'] == 'Furnished':
                furnished = 'Y'
        print("furnished checked")
    except Exception as e:
        print('failed to check furnished')
        print(e)
    return furnished


def write_csv(dataOut):
    """
    writes csv
    :param dataOut: formatted data from scraping
    :returns:
    """
    with open('realestate.csv', mode='a', encoding='utf-8', newline='') as fd:
        csv_writer = csv.DictWriter(fd,
                                    fieldnames=[
                                        'id', 'address', 'suburb', 'postcode',
                                        'price', 'propertyType', 'bedrooms',
                                        'bathrooms', 'parkingSpaces',
                                        'studies', 'furnished', 'latitude',
                                        'longitude'
                                    ])
        if os.stat('realestate.csv').st_size == 0:
            csv_writer.writeheader()
        for i in range(len(dataOut[list(dataOut.keys())[0]])):  # writes csv from dictionary line by line
            dic1 = {key: dataOut[key][str(i)] for key in dataOut.keys()}
            csv_writer.writerow(dic1)
        print("written csv successfully")


if __name__ == "__main__":
    # postcode
    postcodes = [
        3000, 3002, 3003, 3004, 3005, 3006, 3008, 3010, 3011, 3012, 3013, 3015,
        3016, 3018, 3019, 3020, 3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028,
        3029, 3030, 3031, 3032, 3033, 3034, 3036, 3037, 3038, 3039, 3040, 3041,
        3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 3052, 3053,
        3054, 3055, 3056, 3057, 3058, 3059, 3060, 3061, 3062, 3064, 3065, 3066,
        3067, 3068, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3078, 3079, 3081,
        3082, 3083, 3084, 3085, 3086, 3087, 3088, 3089, 3090, 3091, 3093, 3094,
        3095, 3096, 3099, 3101, 3102, 3103, 3104, 3105, 3106, 3107, 3108, 3109,
        3111, 3113, 3114, 3115, 3116, 3121, 3122, 3123, 3124, 3125, 3126, 3127,
        3128, 3129, 3130, 3131, 3132, 3133, 3134, 3135, 3136, 3137, 3138, 3139,
        3140, 3141, 3142, 3143, 3144, 3145, 3146, 3147, 3148, 3149, 3150, 3151,
        3152, 3153, 3154, 3155, 3156, 3158, 3159, 3160, 3161, 3162, 3163, 3165,
        3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3177, 3178,
        3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190,
        3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202,
        3204, 3205, 3206, 3207, 3335, 3752, 3754, 3765, 3766, 3767, 3781, 3782,
        3785, 3786, 3787, 3788, 3789, 3791
    ]
    for postcode in postcodes:
        print('page%s,%s' % (1, postcode))
        reptile(1, postcode)
        for i in range(2, pages):
            print('page%s,%s' % (i, postcode))
            reptile(i, postcode)
