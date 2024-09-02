#%% Developed by Deborah Dotta, July 2024

import sys
import subprocess
import importlib

# Function to install a package
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Check and install cftime if not available
try:
    import cftime
except ModuleNotFoundError:
    install_package('cftime')
    import cftime

import netCDF4 as nc
import numpy as np
from datetime import datetime, timedelta
import os
import logging
from glob import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_closest_lat_lon(latitudes, longitudes, point_lat, point_lon):
    """
    Find the index of the closest spatial point to the given latitude and longitude.
    """
    lat_diff = np.abs(latitudes - point_lat)
    lon_diff = np.abs(longitudes - point_lon)
    
    combined_diff = np.sqrt(lat_diff**2 + lon_diff**2)
    min_idx = np.unravel_index(combined_diff.argmin(), combined_diff.shape)
    
    return min_idx

def extract_discharge_data(file_path, point_lat, point_lon):
    """
    Extract discharge data from the NetCDF file.
    """
    with nc.Dataset(file_path) as ds:
        latitudes = ds.variables['latitude'][:]
        longitudes = ds.variables['longitude'][:]
        
        try:
            lat_idx = np.where(latitudes == point_lat)[0][0]
            lon_idx = np.where(longitudes == point_lon)[0][0]
            exact_match = True
        except IndexError:
            exact_match = False
            lat_idx, lon_idx = find_closest_lat_lon(latitudes, longitudes, point_lat, point_lon)
        
        actual_lat = latitudes[lat_idx] if np.ndim(latitudes) == 1 else latitudes[lat_idx, lon_idx]
        actual_lon = longitudes[lon_idx] if np.ndim(longitudes) == 1 else longitudes[lat_idx, lon_idx]
        
        if exact_match:
            logger.info(f"Exact point found. Latitude: {actual_lat}, Longitude: {actual_lon}")
        else:
            logger.warning(f"Exact point not found. Closest point used. Latitude: {actual_lat}, Longitude: {actual_lon}")
        
        dis6 = ds.variables['dis06'][:, lat_idx, lon_idx]
        time = ds.variables['time'][:]
        time_units = ds.variables['time'].units
        
        # Convert time to datetetime
        times = nc.num2date(time, units=time_units, calendar='standard')
        times = [datetime(t.year, t.month, t.day, t.hour, t.minute) for t in times]
        
        return dis6, times, actual_lat, actual_lon

def write_discharge_data_to_txt(discharge, times, output_filename):
    """
    Write the discharge data to a text file.
    """
    with open(output_filename, 'a') as f:  # Append mode
        daily_discharge = []
        current_day = times[0].date()
        daily_values = []
        
        for t, dis in zip(times, discharge):
            if t.date() == current_day:
                daily_values.append(dis)
            else:
                # Calculate daily mean discharge
                mean_discharge = np.mean(daily_values)
                f.write(f"{current_day.strftime('%Y%m%d')} {mean_discharge:.3f}\n")
                
                # Reset for the next day
                current_day = t.date()
                daily_values = [dis]
        
        # Write the last day
        if daily_values:
            mean_discharge = np.mean(daily_values)
            f.write(f"{current_day.strftime('%Y%m%d')} {mean_discharge:.3f}\n")

def main():
    # Define file paths and parameters
    data_directory = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical"
    point_lat = 41.998
    point_lon = 45.582
    output_filename = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical\output\discharge_data_1991_2009.txt"
    
    # Clear the output file if it exists
    open(output_filename, 'w').close()
    
    # Variable to store the actual lat/lon used
    actual_lat_lon_used = None
    
    for year in range(1991, 2010):
        for month in range(1, 13):
            file_pattern = os.path.join(data_directory, f"{year}{month:02d}_EFAS_historical.nc")
            matching_files = glob(file_pattern)
            
            # Debugging: Check the file pattern and matching files
            logger.info(f"Searching for files with pattern: {file_pattern}")
            logger.info(f"Found files: {matching_files}")
            
            if not matching_files:
                logger.error(f"No files found for pattern: {file_pattern}")
                continue
            
            file_path = matching_files[0]
            
            # Extract discharge data
            discharge, times, actual_lat, actual_lon = extract_discharge_data(file_path, point_lat, point_lon)
            logger.info(f"Discharge data dimensions for {month:02d}/{year}: {discharge.shape}")
            
            # Store the actual lat/lon used
            if actual_lat_lon_used is None:
                actual_lat_lon_used = (actual_lat, actual_lon)
            
            # Write discharge data to text file
            write_discharge_data_to_txt(discharge, times, output_filename)
            logger.info(f"Discharge data saved to {output_filename}")
    
    # Log the actual lat/lon used
    if actual_lat_lon_used is not None:
        logger.info(f"Actual latitude and longitude used for extraction: {actual_lat_lon_used}")

if __name__ == "__main__":
    main()



#%%