import datetime
import time

import pandas as pd
import requests


def read_csv_file(p= '../data/curated/realestate_with_closest_distance_duration.csv'):
    """
    reads csv
    :param p: directory
    :returns: dataframe
    """
    df = pd.read_csv(p)
    return df


def post_get(start_longitude, start_latitude, end_longitude, end_latitude):
    """
    requests data
    :param start_longitude: starting point
    :param start_latitude: starting point
    :param end_longitude: end point
    :param end_latitude: end point
    :returns: distance， duration
    """
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    # combine URL
    url = 'http://34.143.200.33:8080/ors/v2/directions/driving-car?start={},{}&end={},{}'.format(
        start_longitude, start_latitude, end_longitude, end_latitude)
    print(url)
    try:
        call = requests.get(url, headers=headers)
        print(call)
    except Exception as e:
        print(e)
        return None, None
    else:
        # show responses
        if call.status_code == 200:
            data = call.json()
            data = data["features"][0]["properties"]["segments"][0]
            return data["distance"], data["duration"]
        else:
            print(call.status_code, call.reason)
            return None, None


def main():
    """
    :returns: 0
    """
    # file directory
    file_path = '../data/curated/realestate_with_closest_distance_duration.csv'
    # load to dataframe
    df = read_csv_file(file_path)

    # columns to be added
    columns = ['cbd_distance', 'cbd_duration']
    position = ["cbd_lat", "cbd_long"]
    # add if doesn't exist
    for i in range(0, len(position), 2):
        column1 = columns[i]
        column2 = columns[i + 1]
        loc = list(df.columns).index(position[i+1])
        if column1 not in df.columns:
            df.insert(loc=loc + 1, column=column1, value=None)
        if column2 not in df.columns:
            df.insert(loc=loc + 2, column=column2, value=None)
    # save
    df.to_csv(file_path, index=False)

    write_time = datetime.datetime.now()
    for index in df.index:
        for i in range(0, len(columns), 2):
            # request if empty
            # change to while to make it pause if request isn't successful
            if pd.isna(df.loc[index, columns[i]]):
                # send request and get data
                distance, duration = post_get(df.loc[index, "longitude"], df.loc[index, "latitude"],
                                              df.loc[index, position[i + 1]], df.loc[index, position[i]])
                if not distance is None and not duration is None:
                    print("success", i//2, index, len(df.index))
                    # unit conversion
                    # distance = distance/1000
                    # duration = duration/60
                    df.loc[index, columns[i]] = distance
                    df.loc[index, columns[i+1]] = duration
                else:
                    print('None ', i//2, index, len(df.index), "Try requesting again after a second")

        if write_time + datetime.timedelta(seconds=90) < datetime.datetime.now():
            # write csv every 90 seconds
            df.to_csv(file_path, index=False)
            write_time = datetime.datetime.now()
        else:
            df.to_csv(file_path, index=False)



if __name__ == "__main__":
    main()
