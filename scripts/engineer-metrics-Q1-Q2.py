import pandas as pd
from numpy import log

df = pd.read_csv('data/curated/realestate_with_closest_distance_duration.csv')
df2 = pd.read_csv('data/curated/realestate_coor_school.csv')[['id', 'min_sec_icsea', 'min_pri_icsea']]

df = df.merge(df2, on='id')
df = df.merge(pd.read_csv('data/curated/Crime_Rate.csv'), left_on='postcode', right_on='Postcode')

df = df.dropna(subset='zlogCrimerate')

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
df['is_bus_walkable'] = df['closest_bus_distance'].apply(lambda dis: r'$<$200 m' if dis < 200 else '200m-1km' if dis < 1000 else r'$>$1 km')

df['city'] = df['cbd_distance'].apply(lambda dis: dis < 3000)

selected_property_types = ['Townhouse', 'House', 'Apartment', 'Unit']
df.loc[:, 'propertyType'] = df['propertyType'].apply(lambda t: t if t in selected_property_types else 'Other')

df.loc[:, 'bedrooms'] = df['bedrooms'].apply(lambda p: 1 if p in {0, 1} else p if p < 4 else '4+')
df.loc[:, 'parkingSpaces'] = df['parkingSpaces'].apply(lambda p: p if p < 3 else '3+')
df.loc[:, 'bathrooms'] = df['bathrooms'].apply(lambda p: p if p < 3 else '3+')

previous_size = len(df)
df = df[df['propertyType'] != 'Other']
print(f'{previous_size-len(df)}/{previous_size} ({(previous_size-len(df))/previous_size*100:.0f}%) of properties of type not in {selected_property_types} removed.')

df.to_csv('data/curated/engineered-data.csv', index=False)
