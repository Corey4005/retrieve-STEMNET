
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
import numpy as np
import datetime 
import argparse
import warnings

warnings.filterwarnings("ignore")

def convert_timestamp(epoch):
    epoch = int(epoch)
    dt_object = datetime.datetime.utcfromtimestamp(epoch)
    formatted = dt_object.strftime("%m-%d-%Y %H:%M:%S")
    formatted_date_datetime = datetime.datetime.strptime(formatted, "%m-%d-%Y %H:%M:%S")
        
    return formatted_date_datetime

    

# Read the data into a DataFrame
async def fetch_station_data(session, url, station, dir, date_start, pbar):
    async with session.get(url, ssl=False) as response:
        try: 
            if response.status == 200:
                #update to show status 200
                pbar.update(1)

                #need to read csv in as bytes
                buffer = BytesIO(await response.read())
                df = pd.read_csv(buffer, on_bad_lines='skip', dtype={'time': int, 'm0': float, 
                                                                     'm1': float, 'm2': float, 
                                                                     'm3': float, 'm4': float})

                #getting rid of bad values 
                df = df.replace(-999.99, np.nan)

                #the index where the data should start
                df_start = df.loc[df['time']>=date_start]

                #converting timestamps
                df['time'] = df['time'].apply(convert_timestamp)
            
                #if the dataframe has data, this is where there are good values
                if not df_start.index.empty: 
                    value_start = df_start.index[0]
                    df_subset = df.loc[value_start:]

                    df_subset['m0'].values[df_subset['m0'].values>2200.0]=np.nan
                    df_subset['m0'].values[df_subset['m0'].values<900.0]=np.nan

                    #replace bad values 
                    df_subset['m1'].values[df_subset['m1'].values>2200.0]=np.nan
                    df_subset['m1'].values[df_subset['m1'].values<900.0]=np.nan

                    #replace bad values 
                    df_subset['m2'].values[df_subset['m2'].values>2200.0]=np.nan
                    df_subset['m2'].values[df_subset['m2'].values<900.0]=np.nan

                    #replace bad values 
                    df['m3'].values[df['m3'].values>2200.0]=np.nan
                    df['m3'].values[df['m3'].values<900.0]=np.nan

                    #replace bad values 
                    df['m4'].values[df['m4'].values>2200.0]=np.nan
                    df['m4'].values[df['m4'].values<900.0]=np.nan
                    
                    #saving to path
                    path = dir + '/' + station + '.csv'
                    df_subset.to_csv(path)
                    pbar.update(1)

                else:
                    #saving to path
                    logging.error(f'{station} pull failed with bad start value in sn_meta.txt.')
            
            else:
               logging.error(f'{station} server status bad request code: 404')
               

        except Exception as e:
            logging.error(f'{station} pull failed: {e}')


async def main(station_df, url, dir, model):
    taskurl = url
    logging.basicConfig(filename='logdir/stemneterror.log', encoding='utf-8', level=logging.ERROR)

    async with aiohttp.ClientSession() as session:
        tasks = []
        station_pbars = {}

        for index, row in station_df.iterrows():
            url = taskurl + row['id'] + ".csv"
            station = row['id']

            #start date, '0' means it is not 
            # reading soil moisture in the ground
            date_start = row['install_date']

            if date_start > 0:
                station_pbars[station] = tqdm(total=2, desc=f"Retrieving {station}")
        
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
            if date_start > 0:
                csv = fetch_station_data(session, url, station, dir, date_start, station_pbars[station])
                tasks.append(csv)
        
        await asyncio.gather(*tasks)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This program can pull data from AL STEMNET Stations.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--model", default=None, help=
    '''Choose a model to pull root zone soil moisture percentiles from 
    default choice: None 
    choices: gldas, None
    model descriptions: 
        Global Land Data Assimilation System - gldas 
        Purpose: Average 20th Percentile Root Zone Soil Moisture at 20 cm depth.
        Location: Data is in ./models/gldas/GLDAS_CLSM025_1980_2022_RZSM_20PCTL.nc
        Filetype: netcdf
        Author: Mohmoud Osman, John Hopkins University
        Email: mahmoud.osman@jhu.edu
        Temporal Resolution: daily (1-365)
        Spatial Resolution: 12.5 km
        Climatology: 1980-2022
    returns: 
        model textfiles for each STEMNET station on the server will be output to datadir 
        along with current STEMNET station data that can be read into aquatron''', choices=[None, 'gldas'])
    

    
    args = parser.parse_args()

    model = args.model
    #url for the station metadata 
    url1 = 'https://data.alclimate.com/stemmnet/sn_meta.txt'
    response = requests.get(url1)

    if response.status_code == 200:
        text = response.text
        
    else:
        message = 'Server status 404 at https://data.alclimate.com/stemmnet/sn_meta.txt, exiting.'
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
    loop.run_until_complete(main(stations_df, url2, datadir, model=model))
    print('\n')
    print(f'Station data stored at: {datadir}')
    print(f'If bar did not load, error log is stored at: {logdir}')

