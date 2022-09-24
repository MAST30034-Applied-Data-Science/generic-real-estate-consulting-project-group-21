import datetime
import time

import pandas as pd
import requests


def read_csv_file(p='../data/curated/realestate_coor.csv'):
    """
    reads csv
    :param p: directory
    :return:
    """
    df = pd.read_csv(p)
    return df


def post_get(start_longitude, start_latitude, end_longitude, end_latitude):
    """
    request data
    :param start_longitude: starting point
    :param start_latitude: starting point
    :param end_longitude: end point
    :param end_latitude: end point
    :return: distance， duration
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
    # file directory
    file_path = '../data/curated/realestate_coor.csv'
    # load to dataframe
    df = read_csv_file(file_path)

    # columns to be added
    columns = ['closest_primary_distance', 'closest_primary_duration',
               'closest_secondary_distance', 'closest_secondary_duration',
               'closest_train_distance', 'closest_train_duration',
               'closest_tram_distance', 'closest_tram_duration',
               'closest_bus_distance', 'closest_bus_duration',
               'closest_park_distance', 'closest_park_duration']
    position = ["closest_primary_lat", "closest_primary_long",
                "closest_secondary_lat", "closest_secondary_long",
                "closest_train_lat", "closest_train_long",
                "closest_tram_lat", "closest_tram_long",
                "closest_bus_lat", "closest_bus_long",
                "closest_park_lat", "closest_park_long"]
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
