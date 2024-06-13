#%%# Developed by Deborah Dotta, June 2024
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

def find_closest_lat_lon(latitudes, longitudes, discharges, point_lat, point_lon):
    """
    Find the index of the closest spatial point to the given latitude and longitude,
    and ensure it has the highest discharge value in the neighborhood.
    """
    lat_diff = np.abs(latitudes - point_lat)
    lon_diff = np.abs(longitudes - point_lon)
    min_lat_idx, min_lon_idx = np.unravel_index((lat_diff + lon_diff).argmin(), latitudes.shape)
    
    # Consider a 3x3 grid around the closest point
    lat_indices = np.clip([min_lat_idx-1, min_lat_idx, min_lat_idx+1], 0, latitudes.shape[0]-1)
    lon_indices = np.clip([min_lon_idx-1, min_lon_idx, min_lon_idx+1], 0, longitudes.shape[1]-1)
    
    max_value = -np.inf
    best_lat_idx = min_lat_idx
    best_lon_idx = min_lon_idx
    
    for lat_idx in lat_indices:
        for lon_idx in lon_indices:
            value = discharges[lat_idx, lon_idx]
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

def extract_forecast_data(file_path, point_lat, point_lon):
    """
    Extract forecast data from the NetCDF file.
    """
    with nc.Dataset(file_path) as ds:
        latitudes = ds.variables['latitude'][:]
        longitudes = ds.variables['longitude'][:]
        dis24 = ds.variables['dis24'][:, :, :, :]
        
        # Log dataset resolution and grid details
        lat_resolution = np.abs(latitudes[1] - latitudes[0])
        lon_resolution = np.abs(longitudes[1] - longitudes[0])
        logger.info(f"Latitude resolution: {lat_resolution} degrees, Longitude resolution: {lon_resolution} degrees")
        logger.info(f"Latitude range: {latitudes.min()} to {latitudes.max()}")
        logger.info(f"Longitude range: {longitudes.min()} to {longitudes.max()}")
        
        # Find the nearest point with the highest discharge value
        lat_idx, lon_idx = find_closest_lat_lon(latitudes, longitudes, dis24[0, 0], point_lat, point_lon)
        
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

def plot_percentiles(times, forecast_data_list, output_filename, basin_name):
    """
    Plot the ensemble members for different months with percentiles and mean.
    """
    fig, axes = plt.subplots(4, 3, figsize=(18, 24), sharey=True)
    plt.rcParams["font.family"] = "Calibri"

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    for i, ax in enumerate(axes.flatten()):
        forecast_data = forecast_data_list[i]
        time = times[i]
        
        # Calculate percentiles
        p30 = np.percentile(forecast_data, 30, axis=0)
        p70 = np.percentile(forecast_data, 70, axis=0)
        p10 = np.percentile(forecast_data, 10, axis=0)
        p90 = np.percentile(forecast_data, 90, axis=0)
        mean = np.mean(forecast_data, axis=0)
        
        ax.fill_between(time, p30, p70, color='skyblue', alpha=0.6, label='30-70th Percentile')
        ax.fill_between(time, p10, p90, color='#66b3ff', alpha=0.3, label='10-90th Percentile')
        ax.plot(time, mean, color='#0059b3', label='Ensemble Mean', linewidth=2)
        
        ax.set_title(f"01 {months[i]} {time[0].year}")
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Discharge (m³/s)")
        ax.grid(True)
        
    fig.suptitle(f"Seasonal Reforecast - EFAS for {basin_name}", fontsize=16)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', fontsize='small', ncol=3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_filename, bbox_inches='tight')
    plt.show()

def plot_ensemble_members(times, forecast_data_list, output_filename, basin_name):
    """
    Plot the ensemble members for different months.
    """
    fig, axes = plt.subplots(4, 3, figsize=(18, 24), sharey=True)
    plt.rcParams["font.family"] = "Calibri"

    colors = plt.cm.get_cmap('tab20', 25)
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    for i, ax in enumerate(axes.flatten()):
        forecast_data = forecast_data_list[i]
        time = times[i]
        for member in range(forecast_data.shape[0]):
            ax.plot(time, forecast_data[member, :], color=colors(member), linewidth=1)
        ax.set_title(f"01 {months[i]} {time[0].year}")
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Discharge (m³/s)")
        ax.grid(True)
        
    fig.suptitle(f"Seasonal Reforecast - EFAS for {basin_name}", fontsize=16)
    handles = [plt.Line2D([0, 1], [0, 1], color=colors(i), lw=2) for i in range(forecast_data.shape[0])]
    labels = [f'Ensemble Member {i+1}' for i in range(forecast_data.shape[0])]
    fig.legend(handles, labels, loc='upper center', fontsize='small', ncol=5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_filename, bbox_inches='tight')
    plt.show()

def main():
    # Define file paths and parameters
    data_directory = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia"
    year = 2009
    point_lat = 42.05 
    point_lon = 44.97 
    basin_name = "Alazani Basin - Shakriani Hydrological Station"
    destination_path = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia"
    
    forecast_data_list = []
    times = []
    
    # Process each month's file
    for month in range(1, 13):
        file_pattern = os.path.join(data_directory, f"{year}{month:02d}_EFAS_seasonal_reforecast.nc")
        file_path = glob(file_pattern)[0]
        
        # Extract forecast data
        forecast_data, forecast_steps, ensemble_members, forecast_times, actual_lat, actual_lon = extract_forecast_data(file_path, point_lat, point_lon)
        logger.info(f"Forecast data dimensions for {month:02d}/{year}: {forecast_data.shape}")
        logger.info(f"Number of time steps: {forecast_steps.size}, Number of ensemble members: {ensemble_members.size}")
        logger.info(f"Actual latitude used: {actual_lat}, Actual longitude used: {actual_lon}")
        
        forecast_data_list.append(forecast_data)
        times.append(forecast_times)
        
        # Write forecast data to .fcst file
        file_basename = f"{basin_name}_reforecast_efas_{year}{month:02d}"
        fcst_filename = os.path.join(destination_path, f"{file_basename}.fcst")
        write_forecast_to_file(fcst_filename, forecast_data, forecast_steps, forecast_times)
        logger.info(f"Forecast data written to {fcst_filename}")
    
    # Plot ensemble members with percentiles and mean
    plot_filename_percentiles = os.path.join(destination_path, f"{basin_name}_reforecast_efas_{year}_percentiles.png")
    plot_percentiles(times, forecast_data_list, plot_filename_percentiles, basin_name)
    logger.info(f"Ensemble members plot saved as {plot_filename_percentiles}")
    
    # Plot ensemble members
    plot_filename_ensemble = os.path.join(destination_path, f"{basin_name}_reforecast_efas_{year}_ensemble.png")
    plot_ensemble_members(times, forecast_data_list, plot_filename_ensemble, basin_name)
    logger.info(f"Ensemble members plot saved as {plot_filename_ensemble}")

if __name__ == "__main__":
    main()



#%%