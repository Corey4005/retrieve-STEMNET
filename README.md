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
3. Processes and saves the data as CSV files in a local "data" directory.
4. Utilizes asyncio to efficiently handle multiple asynchronous requests.
5. Provides terminal progress bars to monitor download speeds. 

## Customization

You may need to customize the following parts of the script to suit your needs:

- **Output Directory**: By default, data is stored in a "data" directory in the current working directory. You can change the `datadir` variable to specify a different output directory by updating the script. 

## Output

The script will display progress bars using tqdm for each station being retrieved. Once the script finishes execution, all retrieved data will be stored in the specified output directory.

For questions or issues, please [open an issue](https://github.com/Corey4005/retrieve-STEMNET/issues) on the GitHub repository.
