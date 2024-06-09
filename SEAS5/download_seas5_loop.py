# Developed by Deborah Dotta, February 2024

import datetime as dt
from pathlib import Path
import os
import logging
import cdsapi

# Initialize CDS API client
c = cdsapi.Client()

def download_data_for_month(year, month, deltat, my_variables, var_name_suffix):
    """
    Downloads data for a given year, month, timestep, and variables list.
    """
    day0 = dt.datetime(year, month, 1)  # First day of the current month/year
    day0_str = '{}'.format(day0.strftime("%Y%m%d"))  # Date format to YYYYMMDD
    target_file_tmp = str(Path(import_folder) / (day0_str + '_seas5_' + var_name_suffix + '.grib'))
    final_file_name = target_file_tmp.replace(".tmp", ".grib")

    my_request = {
        'originating_centre': 'ecmwf',
        'system': '51',
        'variable': my_variables,
        'date': day0.strftime("%Y-%m-%d"),  # Use the day0 in YYYY-MM-DD format for the request
        'leadtime_hour': list(range(0, 4320 + deltat, deltat))
    }

    logging.info(f"Starting download for {var_name_suffix} data: {day0_str}")
    c.retrieve('seasonal-original-single-levels', my_request, target_file_tmp)

    # Check if the download was successful and the file exists before renaming
    if os.path.exists(target_file_tmp):
        try:
            os.rename(target_file_tmp, final_file_name)
            logging.info(f"File successfully renamed to {final_file_name}")
        except OSError as e:
            logging.error(f"Error renaming file from {target_file_tmp} to {final_file_name}: {e}")
    else:
        logging.error(f"Download failed or file does not exist: {target_file_tmp}")

if '__file__' in globals():
    my_path = Path(__file__).resolve().parent
else:
    my_path = Path('.').resolve()

# Setup logging
log_file = my_path / 'download_seas5.log'
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, filename=str(log_file))

# Input for year and month range
start_year = int(input("Enter the start year: "))
end_year = int(input("Enter the end year: "))
start_month = int(input("Enter the start month (1-12): "))
end_month = int(input("Enter the end month (1-12): "))

# Folder where files will be saved
import_folder = my_path

# Loop through each year and month
for year in range(start_year, end_year + 1):
    for month in range(start_month, end_month + 1):
        download_data_for_month(year, month, 24, ['surface_solar_radiation_downwards', 'total_precipitation'], '24h')
        download_data_for_month(year, month, 6, ['2m_temperature'], '6h')

logging.info("All downloads completed.")
