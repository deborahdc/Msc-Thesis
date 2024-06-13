#NOT WORKING #%%# Developed by Deborah Dotta, June 2024
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging
from glob import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_closest_lat_lon(latitudes, longitudes, point_lat, point_lon):
    """
    Find the index of the closest spatial point to the given latitude and longitude,
    and ensure it has the highest value in the neighborhood.
    """
    lat_diff = np.abs(latitudes - point_lat)
    lon_diff = np.abs(longitudes - point_lon)
    min_lat_idx, min_lon_idx = np.unravel_index((lat_diff + lon_diff).argmin(), latitudes.shape)
    
    # Consider a 3x3 grid around the closest point
    lat_indices = np.clip([min_lat_idx-1, min_lat_idx, min_lat_idx+1], 0, latitudes.shape[0]-1)
    lon_indices = np.clip([min_lon_idx-1, min_lon_idx, min_lon_idx+1], 0, latitudes.shape[1]-1)
    
    max_value = -np.inf
    best_lat_idx = min_lat_idx
    best_lon_idx = min_lon_idx
    
    for lat_idx in lat_indices:
        for lon_idx in lon_indices:
            value = latitudes[lat_idx, lon_idx]  # Assuming the variable of interest is in latitudes
            if value > max_value:
                max_value = value
                best_lat_idx = lat_idx
                best_lon_idx = lon_idx
    
    return best_lat_idx, best_lon_idx

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

def extract_historical_data(file_path, point_lat, point_lon):
    """
    Extract historical data from the NetCDF file.
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
        actual_lat = latitudes[lat_idx]
        actual_lon = longitudes[lon_idx]
        logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")
        
        # Calculate the distance difference in meters
        distance_diff = haversine(point_lat, point_lon, actual_lat, actual_lon)
        if isinstance(distance_diff, np.ma.MaskedArray):
            distance_diff = distance_diff.item()
        logger.info(f"Distance from original point: {distance_diff:.2f} meters")
        
        dis6 = ds.variables['dis06'][:, lat_idx, lon_idx]
        time = ds.variables['time'][:]
        time_units = ds.variables['time'].units
        
        # Convert time to datetime
        times = nc.num2date(time, units=time_units, calendar='standard')
        # Convert cftime to datetime
        times = [datetime(t.year, t.month, t.day, t.hour, t.minute) for t in times]
        # Average the discharge values for 00:00, 06:00, 12:00, 18:00
        daily_discharge = np.mean(dis6.reshape(-1, 4), axis=1)
        daily_times = times[::4]
        
        return daily_discharge, daily_times, actual_lat, actual_lon

def plot_historical_data(time, discharge, month, output_filename, basin_name):
    """
    Plot the historical data for a specific month.
    """
    plt.figure(figsize=(10, 6))
    plt.rcParams["font.family"] = "Calibri"

    plt.plot(time, discharge, color='blue', linewidth=2)
    plt.title(f"Historical Data - EFAS for {basin_name} ({month})", fontsize=16)
    plt.xlabel("Time (days)")
    plt.ylabel("Discharge (m³/s)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight')
    plt.show()

def main():
    # Define file paths and parameters
    data_directory = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical"
    year = 2009
    point_lat = 42.05 
    point_lon = 44.97 
    basin_name = "Alazani Basin - Shakriani Hydrological Station"
    destination_path = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia_historical"
    
    # Process each month's file
    for month in range(1, 13):
        file_pattern = os.path.join(data_directory, f"{year}{month:02d}_EFAS_historical.nc")
        file_path = glob(file_pattern)[0]
        
        # Extract historical data
        discharge, time, actual_lat, actual_lon = extract_historical_data(file_path, point_lat, point_lon)
        logger.info(f"Discharge data dimensions for {month:02d}/{year}: {discharge.shape}")
        logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")
        
        # Plot historical data for the month
        month_name = datetime(year, month, 1).strftime('%B')
        plot_filename = os.path.join(destination_path, f"{basin_name}_historical_efas_{year}_{month_name}.png")
        plot_historical_data(time, discharge, month_name, plot_filename, basin_name)
        logger.info(f"Historical data plot saved as {plot_filename}")

if __name__ == "__main__":
    main()

#%%

#%%



#%%


#%%
