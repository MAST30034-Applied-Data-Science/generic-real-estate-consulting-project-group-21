import pandas as pd


df = pd.read_csv('data/curated/realestate_with_closest_distance_duration.csv')
df2 = pd.read_csv('data/curated/realestate_coor_school.csv')[['id', 'min_sec_icsea', 'min_pri_icsea']]

df2['min_pri_icsea'] = pd.to_numeric(df2['min_pri_icsea'], errors='coerce')
df2['min_sec_icsea'] = pd.to_numeric(df2['min_sec_icsea'], errors='coerce')

df = df.join(df2, lsuffix='id', rsuffix='id')

df = df[['suburb', 'postcode', 'price', 'propertyType',
        'bedrooms', 'bathrooms', 'parkingSpaces', 'studies', 'furnished',
         'closest_primary_distance', 'closest_secondary_distance',
         'closest_train_distance', 'closest_tram_distance',
         'closest_bus_distance', 'closest_park_distance', 'min_pri_icsea',
         'min_sec_icsea']]


# Livability

df['park_walkability'] = df['closest_park_distance'].apply(lambda dis: r'$<$1.5 km' if dis < 1500 else '1.5-5km' if dis < 5000 else r'$>$5 km')
df['is_primary_school_walkable'] = df['closest_primary_distance'].apply(lambda dis: 'Yes' if dis < 1500 else 'No')
df['is_secondary_school_walkable'] = df['closest_secondary_distance'].apply(lambda dis: 'Yes' if dis < 1500 else 'No')

df['is_tram_stop_walkable'] = df['closest_tram_distance'].apply(lambda dis: 'Yes' if dis < 1500 else 'No')

df.to_csv('data/curated/engineered-data.csv', index=False)
