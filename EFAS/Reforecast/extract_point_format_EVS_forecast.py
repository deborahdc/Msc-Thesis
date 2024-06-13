#%%# Developed by Deborah Dotta, June 2024
# This code extracts a point from nc data and formats it into an EVS verification file for ensemble forecasts .fcst

import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_closest_lat_lon(latitudes, longitudes, point_lat, point_lon):
    """
    Find the index of the closest spatial point to the given latitude and longitude.
    """
    lat_diff = np.abs(latitudes - point_lat)
    lon_diff = np.abs(longitudes - point_lon)
    min_lat_idx, min_lon_idx = np.unravel_index((lat_diff + lon_diff).argmin(), latitudes.shape)
    return min_lat_idx, min_lon_idx

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.
    """
    R = 6371e3  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

def extract_forecast_data(file_path, point_lat, point_lon):
    """
    Extract forecast data from the NetCDF file.
    """
    with nc.Dataset(file_path) as ds:
        latitudes = ds.variables['latitude'][:]
        longitudes = ds.variables['longitude'][:]
        
        # Log dataset resolution and grid details
        lat_resolution = np.abs(latitudes[1] - latitudes[0])
        lon_resolution = np.abs(longitudes[1] - longitudes[0])
        logger.info(f"Latitude resolution: {lat_resolution} degrees, Longitude resolution: {lon_resolution} degrees")
        logger.info(f"Latitude range: {latitudes.min()} to {latitudes.max()}")
        logger.info(f"Longitude range: {longitudes.min()} to {longitudes.max()}")
        
        lat_idx, lon_idx = find_closest_lat_lon(latitudes, longitudes, point_lat, point_lon)
        
        # Print the actual lat and lon used
        actual_lat = latitudes[lat_idx, lon_idx]
        actual_lon = longitudes[lat_idx, lon_idx]
        logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")
        
        # Calculate the distance difference in meters
        distance_diff = haversine(point_lat, point_lon, actual_lat, actual_lon)
        logger.info(f"Distance from original point: {distance_diff:.2f} meters")
        
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

def write_forecast_to_file(fcst_filename, forecast_data, forecast_steps, forecast_times):
    """
    Write forecast data to a .fcst file.
    """
    num_time_steps = forecast_steps.size
    num_ensemble_members = forecast_data.shape[0]

    with open(fcst_filename, 'w') as fcst_file:
        for time_step in range(num_time_steps):
            leadtime_hours = int(forecast_steps[time_step])
            forecast_date = forecast_times[time_step]
            date_str = forecast_date.strftime('%Y%m%d%H')

            logger.info(f"Processing time step: {time_step}, Lead time (hours): {leadtime_hours}, Forecast date: {forecast_date}")

            forecasts = ' '.join(f'{forecast_data[ensemble_member, time_step]:.1f}' for ensemble_member in range(num_ensemble_members))
            fcst_file.write(f"{date_str} {leadtime_hours} {forecasts}\n")

def plot_ensemble_members(time, forecast_data, output_filename):
    """
    Plot the 25 ensemble members.
    """
    plt.figure(figsize=(12, 6))
    plt.rcParams["font.family"] = "Calibri"

    colors = plt.cm.get_cmap('tab20', 25)

    for member in range(25):
        plt.plot(time, forecast_data[member, :], color=colors(member), linewidth=1)

    plt.xlabel('Time')
    plt.ylabel('Discharge (m³/s)')
    plt.title('Seasonal reforecast - EFAS')
    plt.grid(True)
    
    # Add legend indicating "25 Ensemble Members"
    plt.legend([f'Ensemble Member {i+1}' for i in range(25)], loc='upper right', fontsize='small', ncol=5)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_filename, bbox_inches='tight')
    plt.show()

def main():
    # Define file paths and parameters
    seasonal_forecast_file = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\EFAS\Reforecast\20016_EFAS_seasonal_reforecast.nc"
    point_lat = 42.05 
    point_lon = 44.97 
    basin_name = "Iori Basin"
    destination_path = r"C:\Users\dottacor\OneDrive - Stichting Deltares\Documents\Git\Msc-Thesis\EFAS\Reforecast"

    # Extract forecast data
    forecast_data, forecast_steps, ensemble_members, forecast_times, actual_lat, actual_lon = extract_forecast_data(seasonal_forecast_file, point_lat, point_lon)
    logger.info(f"Forecast data dimensions: {forecast_data.shape}")
    logger.info(f"Number of time steps: {forecast_steps.size}, Number of ensemble members: {ensemble_members.size}")
    logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")

    # Determine forecast start date from the first forecast time
    forecast_start_date = forecast_times[0]

    # Write forecast data to .fcst file
    file_basename = f"{basin_name}_reforecast_efas_{forecast_start_date.strftime('%Y%m')}"
    fcst_filename = os.path.join(destination_path, f"{file_basename}.fcst")
    write_forecast_to_file(fcst_filename, forecast_data, forecast_steps, forecast_times)
    logger.info(f"Forecast data written to {fcst_filename}")

    # Plot ensemble members
    plot_filename = os.path.join(destination_path, f"{file_basename}.png")
    plot_ensemble_members(forecast_times, forecast_data, plot_filename)
    logger.info(f"Ensemble members plot saved as {plot_filename}")

if __name__ == "__main__":
    main()


#%%