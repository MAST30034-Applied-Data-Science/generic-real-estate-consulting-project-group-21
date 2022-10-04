import pandas as pd

df = pd.read_csv('data/curated/realestate_with_closest_distance_duration.csv')
df2 = pd.read_csv('data/curated/realestate_coor_school.csv')[['id', 'min_sec_icsea', 'min_pri_icsea']]

df2['min_pri_icsea'] = pd.to_numeric(df2['min_pri_icsea'], errors='coerce')
df2['min_sec_icsea'] = pd.to_numeric(df2['min_sec_icsea'], errors='coerce')

df = df.join(df2, lsuffix='id', rsuffix='id')

df = df[['suburb', 'postcode', 'price', 'propertyType',
       'bedrooms', 'bathrooms', 'parkingSpaces', 'studies', 'furnished',
       'closest_primary_duration', 'closest_secondary_duration',
       'closest_train_duration', 'closest_tram_duration', 'closest_bus_duration',
       'closest_park_duration', 'min_pri_icsea', 'min_sec_icsea']]

# Livability

df['park_walkability'] = df['closest_park_duration'].apply(lambda dur: 'High' if dur < 2*60 else 'Medium' if dur < 5*60 else 'Low')
df['is_primary_school_walkable'] = df['closest_primary_duration'].apply(lambda dur: dur < 2*60)
df['is_secondary_school_walkable'] = df['closest_secondary_duration'].apply(lambda dur: dur < 3*60)

df.to_csv('data/curated/engineered-data.csv', index=False)