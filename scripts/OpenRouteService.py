import datetime
import time

import pandas as pd
import grequests


def read_csv_file(p='../data/curated/realestate_with_coordinates.csv'):
    """
    reads csv
    :param p: directory
    :return:
    """
    df = pd.read_csv(p)
    return df


def generate_request_url(start_longitude, start_latitude, end_longitude, end_latitude):
    """
    request data
    :param start_longitude: starting point
    :param start_latitude: starting point
    :param end_longitude: end point
    :param end_latitude: end point
    :return: distance， duration
    """
    
    # combine URL
    url = 'http://34.143.200.33:8080/ors/v2/directions/driving-car?start={},{}&end={},{}'.format(
        start_longitude, start_latitude, end_longitude, end_latitude)
    
    return url

   # call = requests.get(url, headers=headers)
   # print(call)
    # show responses
   # if call.status_code == 200:
   #     data = call.json()
   #     data = data["features"][0]["properties"]["segments"][0]
   #     return data["distance"], data["duration"]
   # else:
   #     print(call.status_code, call.reason)
   #     return None, None

failed_requests = ()

def exception_handler(request, exception):
    global failed_requests
    failed_requests += (request,)

def main():
    # file directory
    file_path = '../data/curated/realestate_with_coordinates.csv'
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
    urls = []
    for index in df.index:
        for i in range(0, len(columns), 2):
            # check if empty
            if pd.isna(df.loc[index, columns[i]]):
                # request for empty values
                urls.append(generate_request_url(df.loc[index, "longitude"], df.loc[index, "latitude"],
                                              df.loc[index, position[i + 1]], df.loc[index, position[i]]))
    #library doesn't like 60,000 requests at a time, batch them into groups ourselves
    responses = []
    global failed_requests
    percent_complete = 0
    i = 0
    BATCH_SIZE = 9323
    print(f'batching {len(urls)} GET requests into groups of size {BATCH_SIZE}...\n')
    while (i+1)*BATCH_SIZE < len(urls):
        requests = (grequests.get(u) for u in urls[i*BATCH_SIZE:(i+1)*BATCH_SIZE])
        resp_batch = grequests.map(requests,exception_handler=exception_handler)
        retries = 0
        while len(failed_requests)>0 and retries < 10:
            retries += 1
            failed_requests = ()    
            resp_batch = grequests.map(requests,exception_handler=exception_handler)
        if len(failed_requests)>0:
            print("Requests failed, try again?")
        responses.append(resp_batch)
        if (i+1)*BATCH_SIZE/len(urls)*100 >= percent_complete:
            percent_complete = (i+1)*BATCH_SIZE/len(urls)*100
            print(f'\r {(i+1)*BATCH_SIZE} ({percent_complete:.1f}%) of GET requests complete...', end='', flush=True)
        i += 1
    resp_batch = (grequests.get(u) for u in urls[i*BATCH_SIZE:])
    retries = 0
    while len(failed_requests)>0 and retries < 10:
        retries += 1
        failed_requests = ()    
        resp_batch = grequests.map(requests,exception_handler=exception_handler)
    if len(failed_requests)>0:
        print("Requests failed, try again?")
    responses.append(resp_batch)
    
    print('\r 100% of GET requests complete... \n', end='', flush=True)
    


        #print(response)
        #add duration/distance to url
    
    #need to add these columsn to the CSV
    
    #            if not distance is None and not duration is None:
    #                print("success", i//2, index, len(df.index))
                    # unit conversion
                    # distance = distance/1000
                    # duration = duration/60
    #                df.loc[index, columns[i]] = distance
    #                df.loc[index, columns[i+1]] = duration
                    # save as requests go through, will start from where it stops if exit in the middle
    #                df.to_csv(file_path, index=False)
    #            else:
    #                print('None ', i//2, index, len(df.index))


if __name__ == "__main__":
    main()
