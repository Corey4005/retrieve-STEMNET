
import asyncio
import aiohttp
import pandas as pd
import requests
from io import BytesIO
from io import StringIO
import os
from tqdm import tqdm
import shutil
import logging


def remove_semicolon(value):
    if value.endswith(';'):
        value = int(value[:-1])
        return value
    else:
        return int(value)

# Read the data into a DataFrame
async def fetch_station_data(session, url, station, dir, date_start, pbar, errorlist):
    async with session.get(url, ssl=False) as response:
        try: 
            if response.status == 200:
                #need to read csv in as bytes
                buffer = BytesIO(await response.read())
                df = pd.read_csv(buffer, on_bad_lines='skip')

                #adding columns
                df.columns = ['index', 'T0', 'T1', 'T2', 'T3', 'T4', 'Solar Voltage', 
                            'Battery Voltage', 'Clock Voltage', 'M0', 'M1', 'M2', 
                            'M3', 'M4', 'Time Collected']
                
                #removing the semicolon and returning a integer to compare to
                lookup = df['Time Collected'].apply(remove_semicolon)
                
                #the index where the data should start
                df_start = lookup.loc[lookup>=date_start]

                #if the dataframe has data, this is where there are good values
                if not df_start.index.empty: 
                    value_start = df_start.index[0]
                    df_subset = df.loc[value_start:]
                    
                    #saving to path
                    path = dir + '/' + station + '.csv'
                    df_subset.to_csv(path)
                    pbar.update(1)

                else:
                    #saving to path
                    logging.error(f'{station} pull failed due to bad date start value.')
            else:
               logging.error(f'{station} server status bad request code: 404')
               

        except Exception as e:
            logging.error(f'{station} pull failed: {e}')


async def main(station_df, url, dir):
    taskurl = url
    logging.basicConfig(filename='logdir/example.log', encoding='utf-8', level=logging.ERROR)

    async with aiohttp.ClientSession() as session:
        errors = []
        tasks = []
        station_pbars = {}

        for index, row in station_df.iterrows():
            url = taskurl + row['id'] + ".csv"
            station = row['id']

            #start date, '0' means it is not 
            # reading soil moisture in the ground
            date_start = row['install_date']

            if date_start != 0:
                station_pbars[station] = tqdm(total=1, desc=f"Retrieving {station}")
        
        for index, row in station_df.iterrows():
            url = taskurl + row['id'] + ".csv"

            #the name of the station
            station = row['id']

            #the date the station was put in the ground.
            # we do not want any stations that are just sitting 
            # in the lab. Therefore, we will filter out 
            # stations that have a '0' for install_date column
            date_start = row['install_date']

            #test station that is not needed
            if date_start != 0:
                csv = fetch_station_data(session, url, station, dir, date_start, station_pbars[station], errors)
                tasks.append(csv)
        
        await asyncio.gather(*tasks)


if __name__ == "__main__":

    #url for the station metadata 
    url1 = 'https://data.alclimate.com/stemmnet/sn_meta.txt'
    response = requests.get(url1)

    if response.status_code == 200:
        text = response.text
        
    else:
        message = 'Unable to retrieve station text file from https://data.alclimate.com/stemmnet/sn_meta.txt'
        print(message)
        os._exit(1)

    url2 = 'https://data.alclimate.com/stemmnet/stations/'
    
    #loading in the data if response call was successful
    data = StringIO(text)
    stations_df = pd.read_csv(data)

    #make a data dir if it does not exist
    cwd = os.getcwd()
    datadir = os.path.join(cwd, 'datadir')
    logdir = os.path.join(cwd, 'logdir')

    #remove the datadir if it exists to clear all data
    if os.path.exists(datadir):
        shutil.rmtree(datadir)

    # if it does not exist, create it 
    if not os.path.exists(datadir):
        os.mkdir(datadir)

    #remove the datadir if it exists to clear all data
    if os.path.exists(logdir):
        shutil.rmtree(logdir)

    # if it does not exist, create it 
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(stations_df, url2, datadir))
    print('\n')
    print(f'All Data Stored at: {datadir}')

