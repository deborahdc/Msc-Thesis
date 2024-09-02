#%% Developed by Deborah Dotta, June 2024
import netCDF4 as nc
import numpy as np
import os
import logging
from datetime import datetime
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

def extract_forecast_data(file_path, point_lat, point_lon):
    """
    Extract forecast data from the NetCDF file.
    """
    try:
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
            
            dis24 = ds.variables['dis24'][:, :, lat_idx, lon_idx]
            step = ds.variables['step'][:]
            ensemble = ds.variables['number'][:]
            valid_time_units = ds.variables['valid_time'].units
            valid_time_values = ds.variables['valid_time'][:]
            # Convert valid_time to datetime
            time = nc.num2date(valid_time_values, units=valid_time_units, calendar='proleptic_gregorian')
            # Convert cftime to datetime using list comprehension
            time = [datetime(t.year, t.month, t.day, t.hour, t.minute, t.second) for t in time]
            
            return dis24, step, ensemble, time, actual_lat, actual_lon
    except OSError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None, None, None, None, None, None

def write_forecast_to_file(fcst_filename, forecast_data_list, forecast_steps_list, forecast_times_list):
    """
    Write forecast data to a .fcst file.
    """
    with open(fcst_filename, 'w') as fcst_file:
        for forecast_data, forecast_steps, forecast_times in zip(forecast_data_list, forecast_steps_list, forecast_times_list):
            if forecast_data is None:
                continue
            num_time_steps = forecast_steps.size
            num_ensemble_members = forecast_data.shape[0]

            for time_step in range(num_time_steps):
                leadtime_hours = int(forecast_steps[time_step])
                forecast_date = forecast_times[time_step]
                date_str = forecast_date.strftime('%Y%m%d%H')

                forecasts = ' '.join(f'{forecast_data[ensemble_member, time_step]:.1f}' for ensemble_member in range(num_ensemble_members))
                fcst_file.write(f"{date_str} {leadtime_hours} {forecasts}\n")

def main():
    # Define file paths and parameters
    data_directory = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia"
    start_year = 1991
    end_year = 2018
    point_lat = 41.998
    point_lon = 45.582
    basin_name = "Alazani Basin - Shakriani Hydrological Station"
    destination_path = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia\merged"
    
    all_forecast_data_list = []
    all_forecast_steps_list = []
    all_forecast_times_list = []
    
    # Process each year's files
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            file_pattern = os.path.join(data_directory, f"{year}{month:02d}_EFAS_seasonal_reforecast.nc")
            files_found = glob(file_pattern)
            if files_found:
                file_path = files_found[0]
                # Extract forecast data
                forecast_data, forecast_steps, ensemble_members, forecast_times, actual_lat, actual_lon = extract_forecast_data(file_path, point_lat, point_lon)
                if forecast_data is not None:
                    logger.info(f"Forecast data dimensions for {month:02d}/{year}: {forecast_data.shape}")
                    logger.info(f"Number of time steps: {forecast_steps.size}, Number of ensemble members: {ensemble_members.size}")
                    logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")
                    
                    all_forecast_data_list.append(forecast_data)
                    all_forecast_steps_list.append(forecast_steps)
                    all_forecast_times_list.append(forecast_times)
            else:
                logger.warning(f"No files found for pattern: {file_pattern}")
    
    # Write all forecast data to a single .fcst file
    fcst_filename = os.path.join(destination_path, f"{basin_name}_reforecast_efas_{start_year}_{end_year}.fcst")
    write_forecast_to_file(fcst_filename, all_forecast_data_list, all_forecast_steps_list, all_forecast_times_list)
    logger.info(f"All forecast data written to {fcst_filename}")

if __name__ == "__main__":
    main()

#%%