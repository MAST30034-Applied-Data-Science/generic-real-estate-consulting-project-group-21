import pandas as pd
import time
import logging
from logging.handlers import WatchedFileHandler


info_logger = logging.getLogger()
info_logger.setLevel(logging.DEBUG)
log_file = 'erro.log'

formatter = logging.Formatter("%(asctime)s-{%(process)d}-%(name)s-%(levelname)s-%(message)s")
info_file_handler = WatchedFileHandler("{}".format(log_file), 'a')
info_file_handler.setLevel(logging.DEBUG)
info_file_handler.setFormatter(formatter)

info_logger.addHandler(info_file_handler)

# school_info_dict = {'school_name':{'latitude':0, 'longitude': 0, 'icsea': 0, 'type': 'pri' }}

def get_school_info(school_location_csv_file, school_profile_excel_file, excel_file_sheet_name):
    school_info_dict = {}

    df_school_loc = pd.read_csv(school_location_csv_file)
    print("====== get_school_info  file {}".format(school_location_csv_file))
    row_count, column_count = df_school_loc.shape
    print("====== csv_name {}, row_count {}, column_count {}".format(school_location_csv_file, row_count, column_count))
    info_logger.info("====== csv_name {}, row_count {}, column_count {}".format(df_school_loc, row_count, column_count))

    # Get school information: name, type, latitude and longitude
    for row in df_school_loc.itertuples():
        row_index = getattr(row, 'Index')
        row_school_no = getattr(row, 'SCHOOL_NO')
        row_school_name = getattr(row, 'School_Name')
        row_school_type = getattr(row, 'School_Type')
        row_school_address_town = getattr(row, 'Address_Town')
        row_school_latitude = getattr(row, 'Y')
        row_school_longitude = getattr(row, 'X')

        # Set the default ICSEA value to NA, If the school is not in the school_profile Excel file, the ICSEA value for the school is NA
        school_info_dict[row_school_name] = {'type': row_school_type, 'latitude': row_school_latitude, 'longitude':row_school_longitude,
                                             'school_no': row_school_no, 'school_address_town':row_school_address_town,
                                             'ICSEA': 'na'}

    # Get a school average
    info_logger.info("---- excel file {} ----".format(school_profile_excel_file))
    df_school_profile = pd.read_excel(school_profile_excel_file, sheet_name=excel_file_sheet_name)
    row_count, column_count = df_school_profile.shape
    print("====== excel_name {}, row_count {}, column_count {}".format(school_profile_excel_file, row_count, column_count))
    info_logger.info("====== excel_name {}, row_count {}, column_count {}".format(school_profile_excel_file, row_count, column_count))
    for row in df_school_profile.itertuples():
        # print (row)
        row_school_name = getattr(row, '_5')
        row_school_icsea = getattr(row, 'ICSEA')

        if row_school_name in school_info_dict:
            school_info_dict[row_school_name]['ICSEA'] = row_school_icsea

    return school_info_dict

def update_csv_with_school_info(realestate_csv_file, school_loc_csv_file, school_profile_excel_file, excel_file_sheet_name,
                                output_file_csv):

    school_info_dict = get_school_info(school_loc_csv_file, school_profile_excel_file, excel_file_sheet_name)

    df = pd.read_csv(realestate_csv_file)
    print("====== realestate_csv_file  header {}".format(df.columns))
    info_logger.info("====== realestate_csv_file  header {}".format(df.columns))

    row_count, column_count = df.shape

    print ("====== realestate_csv_file {}, row_count {}, column_count {}".format(realestate_csv_file, row_count, column_count))
    info_logger.info("====== realestate_csv_file {}, row_count {}, column_count {}".format(realestate_csv_file, row_count, column_count))

    columns = df.columns
    column_names = columns.tolist()

    print("=== column_names {}".format(column_names))
    info_logger.info("=== column_names {}".format(column_names))

    # Add a column MIN_PRI_ICSEA after MIN_PRI_LATITUDE
    index_min_pri_latitude = column_names.index('min_pri_latitude')
    column_names.insert(index_min_pri_latitude+1, 'min_pri_icsea')
    
    # If need to add a list of school_name
    # column_names.insert(index_min_pri_latitude+2, 'pri_school_name')
    # print("=== after insert min_pri_icsea, len {}\n column_names {}".format(len(column_names), column_names))

    # Add a column MIN_SEC_ICSEA after MIN_SEC_LATITUDE
    index_min_sec_latitude = column_names.index('min_sec_latitude')
    column_names.insert(index_min_sec_latitude+1, 'min_sec_icsea')
    
    # If need to add a list of school_name
    # column_names.insert(index_min_sec_latitude+2, 'sec_school_name')
    # print("=== after insert min_sec_icsea, len {}\n column_names {}".format(len(column_names), column_names))

    df = df.reindex(columns=column_names)

    column_names = df.columns.tolist()
    info_logger.info("=== after insert, column_names {}".format(column_names))
    print("=== after insert, len {}\n column_names {}".format(len(column_names), column_names))

    # Iterate over each row of the main table, updating MIN_PRI_ICSEA and MIN_SEC_ICSEA
    for row in df.itertuples():
        # print(row)
        row_index = getattr(row, 'Index')
        row_id = getattr(row, 'id')
        row_min_pri_latitude = getattr(row, 'min_pri_latitude')
        row_min_pri_longitude = getattr(row, 'min_pri_longitude')
        row_min_sec_latitude = getattr(row, 'min_sec_latitude')
        row_min_sec_longitude = getattr(row, 'min_sec_longitude')
        school_name = 'na'

        try:
            # Match the school information from school_info_dict based on the school coordinates in the main table. If this school information is found, update min_pri_icsea and min_sec_icsea
            for school_key, school in school_info_dict.items():
                if school['type'] in ['Primary', 'Pri/Sec']:
                    school_name = school_key
                    # print("school_name {} \n school_info {}".format(school_name, school))
                    if school['latitude'] == row_min_pri_latitude and school['longitude'] == row_min_pri_longitude:
                        # print("school_name {} \n school_info {}".format(school_name, school))
                        df.loc[row_index, 'min_pri_icsea'] = school['ICSEA']
                        # df.loc[row_index, 'pri_school_name'] = school_name
                elif school['type'] in ['Secondary', 'Pri/Sec']:
                    if school['latitude'] == row_min_sec_latitude and school['longitude'] == row_min_sec_longitude:
                        # print("school_name {} \n school_info {}".format(school_name, school))
                        df.loc[row_index, 'min_sec_icsea'] = school['ICSEA']
                        # df.loc[row_index, 'sec_school_name'] = school_name
        except Exception:
            info_logger.info("\t%s %s %s %s %s %s %s %s %s\n" % (row_index, row_id, row_min_pri_latitude,
                                                                    row_min_pri_longitude, df['min_pri_icsea'],
                                                                    row_min_sec_latitude, row_min_sec_longitude,
                                                                    df['min_sec_icsea'], school_name))
            with open(log_file, 'a') as tf:
                import traceback
                traceback.print_exc(file=tf)
                traceback.print_exc()

    # changing the object to integer
    df['min_pri_icsea'] = pd.to_numeric(df['min_pri_icsea'], errors='coerce')
    df['min_sec_icsea'] = pd.to_numeric(df['min_sec_icsea'], errors='coerce')
    print(df.dtypes)
    # output to csv
    df.to_csv(output_file_csv, index=False)

if __name__ == '__main__':
    print("\n====== begin ======\n")

    realestate_csv_file = '../data/curated/realestate_coor.csv'
    school_loc_csv_file = '../data/raw/SchoolLocations2022_remove_non_relevant.csv'
    school_profile_xlsx_file = '../data/raw/school-profile-2021d64e2f404c94637ead88ff00003e0139.xlsx'
    school_profile_xlsx_file_sheet = 'SchoolProfile 2021'
    output_csv_file = '../data/curated/realestate_coor_school.csv'


    start = time.time()
    try:
        update_csv_with_school_info(realestate_csv_file, school_loc_csv_file, school_profile_xlsx_file,
                                    school_profile_xlsx_file_sheet, output_csv_file)
    except:
        import traceback

        traceback.print_exc()
    end = time.time()
    print('\n!!!!!! running time : {}  secs'.format(end - start))

    print ("\n====== end ======\n")


