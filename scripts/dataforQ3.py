import pandas as pd

df = pd.read_csv('data/curated/realestate_with_closest_distance_duration.csv')
df2 = pd.read_csv('data/curated/realestate_coor_school.csv')[['id', 'min_sec_icsea', 'min_pri_icsea']]

df = df.merge(df2, on='id')
df = df.merge(pd.read_csv('data/curated/Crime_Rate.csv'), left_on='postcode', right_on='Postcode')


df = df[['suburb', 'price', 
        'bedrooms', 
         'closest_primary_distance', 'closest_secondary_distance',
         'closest_train_distance', 'closest_tram_distance', 'Crime Rate',
         'closest_bus_distance', 'closest_park_distance', 'min_pri_icsea',
         'min_sec_icsea']]

df = df[(df['closest_park_distance'] > 0) & (df['closest_tram_distance'] > 0) & (df['closest_train_distance'] > 0) & (df['bedrooms'] >= 2) & (df['bedrooms'] <= 4)]

# Livability
df['park_walkability'] = df['closest_park_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_primary_school_walkable'] = df['closest_primary_distance'].apply(lambda dis: 'Yes' if dis < 1500 else 'No')
df['is_secondary_school_walkable'] = df['closest_secondary_distance'].apply(lambda dis: 'Yes' if dis < 1500 else 'No')
df['is_train_station_walkable'] = df['closest_train_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_tram_walkable'] = df['closest_tram_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_bus_walkable'] = df['closest_bus_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df = df[['suburb', 'price', 'bedrooms', 'park_walkability','is_primary_school_walkable','is_secondary_school_walkable','is_train_station_walkable','Crime Rate','min_pri_icsea','min_sec_icsea','is_tram_walkable','is_bus_walkable']]
         

df.to_csv('data/curated/Q3engineered-data.csv', index=False)
