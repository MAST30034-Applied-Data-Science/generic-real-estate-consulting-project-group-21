import datetime
import time

import pandas as pd
import requests


def read_csv_file(p='../data/curated/realestate_school_coord.csv'):
    """
    reads csv
    :param p: directory
    :return:
    """
    df = pd.read_csv(p)
    return df


def read_keys(p='../data/raw/key.txt'):
    """
    reads API key
    :param p: directory
    :return:
    """
    with open(p, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
        return lines
    return None


def post_get(start_longitude, start_latitude, end_longitude, end_latitude):
    """
    request data
    :param start_longitude: starting point
    :param start_latitude: starting point
    :param end_longitude: end point
    :param end_latitude: end point
    :param key: API key
    :return: distance， duration
    """
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    # combine URL
    url = 'http://34.143.200.33:8080/ors/v2/directions/driving-car?start={},{}&end={},{}'.format(
            start_latitude, start_longitude, end_latitude, end_longitude)
    print(url)
    call = requests.get(url, headers=headers)
    print(call)
    # show responses
    if call.status_code == 200:
        data = call.json()
        data = data["features"][0]["properties"]["segments"][0]
        return data["distance"], data["duration"]
    else:
        print(call.status_code, call.reason)
        return None, None

    
def main():
    # file directory
    file_path = '../data/curated/realestate_school_coord.csv'
    # load to dataframe
    df = read_csv_file(file_path)
    # print(df)
    # columns to be added
    columns = ['min_pri_distance', 'min_pri_duration', 'min_sec_distance', 'min_sec_duration', 'min_other_distance',
               'min_other_duration']
    # add if doesn't exist
    for i in range(len(columns)):
        column = columns[i]
        if not column in df.columns:
            df.insert(loc=15 + i + i // 2 * 2, column=column, value=None)
    # save
    df.to_csv(file_path, index=False)
    # key，more keys can be added
    keys = read_keys()
    print(keys)
    print(df.iloc[0])
    for index in df.index:
        for i in range(3):
            if pd.isna(df.iloc[index, 15 + i * 4]):
                # request with key0
                distance, duration = post_get(df.iloc[index, 12], df.iloc[index, 13], df.iloc[index, 14 + i * 4],
                                              df.iloc[index, 13 + i * 4])
                if not distance is None and not duration is None:
                    print("success", i, index, len(df.index))
                    # unit conversion
                    # distance = distance/1000
                    # duration = duration/60
                    df.iloc[index, 15 + i * 4] = distance
                    df.iloc[index, 16 + i * 4] = duration
                    # save as requests go through, will start from where it stops if exit in the middle
                    df.to_csv(file_path, index=False)
                else:
                    print('None ', i, index, len(df.index))
                # to satisfy the 40/min limit
                time.sleep(1.5)


if __name__ == "__main__":
    main()
