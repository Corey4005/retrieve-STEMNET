# retrieve-STEMNET
# Data Retrieval Script

Are you a researcher in the field of environmental science, agriculture, or hydrology? Are you constantly on the lookout for efficient tools to retrieve and analyze soil moisture data?

This Python script retrieves high-temporal resolution (5 minute) soil moisture data from the Alabama Climotolgy Office located at the University of Alabama Huntsville. The data will be stored as CSV files in a local "data" directory created by the script in the same location it is ran. It uses asyncio, aiohttp, pandas, and tqdm to efficiently fetch the recorded history of each station, providing tons of useful data at a high download speed.

Here is the University of Alabama press [release](https://www.uah.edu/news/news/uah-builds-installs-low-cost-soil-moisture-sensors-to-examine-how-flash-droughts-impact-agriculture) describing the soil moisture program. 

## DEMO 

[This](https://youtu.be/1K_zSj3dEaA?si=vKd9rUkqPYH7o75S) is a youtube video demonstrating the use of the program, as well as important background on the project and data. 
## Prerequisites

Before running the script, ensure you have the following dependencies installed:

- Python 3.9.5
- aiohttp 3.8.5
- pandas 2.0.3
- requests 2.31.0
- tqdm 4.66.1

You can easily install python and all dependencies in a virtual environment using conda and pip:

```bash
conda create --name myenv python=3.9.5
```

```bash
conda activate myenv
```

```bash
pip install -r requirements.txt
```

## Usage

1. Clone this repository to your local machine.
2. Open a terminal and navigate to the directory containing the script and the `requirements.txt` file.
3. Install the dependencies as mentioned above.
4. Run the script:

```bash
python getstations.py
```

## Script Overview

This script performs the following tasks:

1. Reads station metadata from a remote server.
2. Fetches data for each station listed in the metadata.
3. Processes and saves the data as CSV files in a local "data" directory (Read Script Processing below).
4. Utilizes asyncio to efficiently handle multiple asynchronous requests.
5. Provides terminal progress bars to monitor download speeds. 

## Script Processing
This script will clean data on the Alabama Climatology Office server below 900.00 mV and above 2200.00 mV NaN values. This is because values below and above this range are not representative of real soil moisture values. Sensors were tested in the lab prior to being installed causing erroneous values that are not real. 

Values labled as -999.99 are also set to NaN. Sometimes clock errors in the sensors cause erroneous values to be reported to the Alabama State Climatology office data server. 

## Output

The script will display progress bars using tqdm for each station being retrieved. Once the script finishes execution, all retrieved data will be stored in the ./datadir/ directory. 

The script will also output a logfile in the ./logdir/stemneterror.log if there are bad server requests (404 error), or if station data could not be processed due to some exception that is thrown during processing. 

For questions or issues, please [open an issue](https://github.com/Corey4005/retrieve-STEMNET/issues) on the GitHub repository.
