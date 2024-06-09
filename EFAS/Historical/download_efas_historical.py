#Developmed by Deborah Dotta, May 2024

import datetime as dt
from pathlib import Path
import os
import logging
import cdsapi

# Initialize CDS API client
c = cdsapi.Client()

def download_data_for_month(year, month):
    """
    Downloads data for all days of a given month.
    """
    target_file = f"{year}{month:02d}_efas_historical.nc"

    request = {
        'system_version': 'version_4_0',
        'variable': 'river_discharge_in_the_last_6_hours',
        'model_levels': 'surface_level',
        'hyear': str(year),
        'hmonth': str(month).zfill(2),
        'hday': [
            str(day).zfill(2) for day in range(1, (dt.datetime(year, month % 12 + 1, 1) - dt.timedelta(days=1)).day + 1)
        ],
        'time': [
            '00:00', '06:00', '12:00', '18:00'
        ],
        'format': 'netcdf4.zip',
        'area': [
            47.5, 43.5, 40,
            44,
        ],
    }

    logging.info(f"Starting download for {year}-{month}")
    c.retrieve('efas-historical', request, target_file)

    if os.path.exists(target_file):
        logging.info(f"Download successful: {target_file}")
    else:
        logging.error(f"Download failed for {year}-{month}")

if '__file__' in globals():
    my_path = Path(__file__).resolve().parent
else:
    my_path = Path('.').resolve()

# Setup logging
log_file = my_path / 'download_efas_historical.log'
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, filename=str(log_file))

# Input for year and month
year = int(input("Enter the year: "))
month = int(input("Enter the month (1-12): "))

download_data_for_month(year, month)

logging.info("Download completed.")
