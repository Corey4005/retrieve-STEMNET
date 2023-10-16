
import asyncio
import aiohttp
import pandas as pd
import requests
from io import BytesIO
from io import StringIO
import os
from tqdm import tqdm
import shutil


# Read the data into a DataFrame
async def fetch_station_data(session, url, station, dir, date_start, pbar):
    async with session.get(url, ssl=False) as response:
        if response.status == 200:
            #need to read csv in as bytes
            buffer = BytesIO(await response.read())
            df = pd.read_csv(buffer, on_bad_lines='skip')
            #adding columns
            df.columns = ['index', 'T0', 'T1', 'T2', 'T3', 'T4', 'Solar Voltage', 
                          'Battery Voltage', 'Clock Voltage', 'M0', 'M1', 'M2', 
                          'M3', 'M4', 'Time Collected']
            
            start = str(date_start)
            value_to_lookup = start+';'
            #the index where the data should start
            df_start = df.loc[df['Time Collected']==value_to_lookup]
            if not df_start.index.empty: 
                value_start = df_start.index[0]
                df_subset = df.loc[value_start:]
                
                #saving to path
                path = dir + '/' + station + '.csv'
                df_subset.to_csv(path)
                pbar.update(1)

            else:
                #saving to path
                path = dir + '/' + station + '.csv'
                df.to_csv(path)
                pbar.update(1)
                
        else:
            print(f"Failed to fetch data from {url}, status code: {response.status}")

async def main(station_df, url, dir):
    taskurl = url
    length = len(station_df)
    async with aiohttp.ClientSession() as session:
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
                csv = fetch_station_data(session, url, station, dir, date_start, station_pbars[station])
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
    datadir = os.path.join(cwd, 'data')

    #remove the datadir if it exists to clear all data
    if os.path.exists(datadir):
        shutil.rmtree(datadir)

    # if it does not exist, create it 
    if not os.path.exists(datadir):
        os.mkdir(datadir)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(stations_df, url2, datadir))
    print('\n')
    print(f'All Data Stored at: {datadir}')

