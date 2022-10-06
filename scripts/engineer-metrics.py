import pandas as pd
from numpy import log

df = pd.read_csv('data/curated/realestate_with_closest_distance_duration.csv')
df2 = pd.read_csv('data/curated/realestate_coor_school.csv')[['id', 'min_sec_icsea', 'min_pri_icsea']]

df = df.merge(df2, on='id')
df = df.merge(pd.read_csv('data/curated/Crime_Rate.csv'), left_on='postcode', right_on='Postcode')

df = df[['suburb', 'postcode', 'price', 'propertyType',
        'bedrooms', 'bathrooms', 'parkingSpaces', 'studies', 'furnished',
         'closest_primary_distance', 'closest_secondary_distance',
         'closest_train_distance', 'closest_tram_distance',
         'cbd_distance', 'cbd_duration', 'zlogCrimerate',
         'closest_bus_distance', 'closest_park_distance', 'min_pri_icsea',
         'min_sec_icsea']]

df = df[(df['closest_park_distance'] > 0) & (df['closest_tram_distance'] > 0) & (df['closest_train_distance'] > 0)]

# Livability
df['log_closest_park_distance'] = log(df['closest_park_distance'])
df['log_closest_tram_distance'] = log(df['closest_tram_distance'])
df['log_closest_train_distance'] = log(df['closest_train_distance'])

df['park_walkability'] = df['closest_park_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_primary_school_walkable'] = df['closest_primary_distance'].apply(lambda dis: r'$<$1.5km' if dis < 1500 else r'$>$1.5km')
df['is_secondary_school_walkable'] = df['closest_secondary_distance'].apply(lambda dis: r'$<$1.5km' if dis < 1500 else r'$>$1.5km')

df['is_tram_stop_walkable'] = df['closest_tram_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_train_station_walkable'] = df['closest_train_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')

df['city'] = df['cbd_distance'].apply(lambda dis: dis<3000)

df.to_csv('data/curated/engineered-data.csv', index=False)
