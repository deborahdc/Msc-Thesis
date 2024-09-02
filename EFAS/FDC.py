#%% Developed by Deborah Dotta, July 2024
# Flow duration curve for Shakriani, whole year

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter

# Path to the .obs file
file_path = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'

# Read the file
data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=['date', 'discharge'])

# Convert the 'date' column to datetime format
data['date'] = pd.to_datetime(data['date'], format='%Y%m%d%H')

# Remove negative discharge values
data = data[data['discharge'] >= 0]

# Sort discharge values in descending order
sorted_discharge = data['discharge'].sort_values(ascending=False)

# Calculate exceedance probability
rank = np.arange(1, len(sorted_discharge) + 1)
exceedance_probability = rank / (len(sorted_discharge) + 1) * 100  # Convert to percentage

# Determine the highest 10^something value for y-axis limit
y_max = 10 ** np.ceil(np.log10(sorted_discharge.max()))

# Plot the flow duration curve
plt.figure(figsize=(15, 10))  # Increased size for better readability
plt.plot(exceedance_probability, sorted_discharge, marker='o', linestyle='-', markersize=2, color='black')
plt.xscale('linear')
plt.yscale('log')
plt.xlabel('Percent of Time Indicated Discharge Was Equaled or Exceeded', fontsize=12)
plt.ylabel('Discharge (m³/s)', fontsize=10)
plt.ylim(1, y_max)  # Set y-axis limit
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

# Customize the x-axis and y-axis ticks
plt.xticks([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 100], fontsize=10)
plt.yticks(
    [1,2,3,4,5,6,7,8,9,10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    fontsize=10
)

# Set the y-axis formatter to scalar format
plt.gca().yaxis.set_major_formatter(ScalarFormatter())

plt.tight_layout()
plt.savefig(r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\flow_duration_yearly.png')
plt.show()




#%% Developed by Deborah Dotta, July 2024, ALL MONTHS
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter

# Path to the .obs file
file_path = r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\Q-Alazani-Shaqriani.obs'

# Read the file
data = pd.read_csv(file_path, delim_whitespace=True, header=None, names=['date', 'discharge'])

# Convert the 'date' column to datetime format
data['date'] = pd.to_datetime(data['date'], format='%Y%m%d%H')

# Remove negative discharge values
data = data[data['discharge'] >= 0]

# Extract month from date
data['month'] = data['date'].dt.month

# Month names for titles
month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Highlight colors for June, July, and August
highlight_color = 'red'
default_color = 'black'

# Create a figure for the subplots
fig, axs = plt.subplots(4, 3, figsize=(20, 20))
axs = axs.flatten()

# Prepare a dictionary to store discharge values at specific exceedance probabilities
discharge_at_probabilities = {'month': [], '67%': [], '90%': []}

# Plot flow duration curve for each month
for month in range(1, 13):
    monthly_data = data[data['month'] == month]
    sorted_discharge = monthly_data['discharge'].sort_values(ascending=False)
    
    # Calculate exceedance probability
    rank = np.arange(1, len(sorted_discharge) + 1)
    exceedance_probability = rank / (len(sorted_discharge) + 1) * 100  # Convert to percentage
    
    # Determine the highest 10^something value for y-axis limit
    y_max = 10 ** np.ceil(np.log10(sorted_discharge.max()))
    
    # Choose color based on the month
    color = highlight_color if month in [6, 7, 8] else default_color
    
    # Plot the flow duration curve
    axs[month-1].plot(exceedance_probability, sorted_discharge, marker='o', linestyle='-', markersize=2, color=color)
    axs[month-1].set_xscale('linear')
    axs[month-1].set_yscale('log')
    axs[month-1].set_xlabel('Percent of Time Indicated Discharge Was Equaled or Exceeded', fontsize=10)
    axs[month-1].set_ylabel('Discharge (m³/s)', fontsize=10)
    axs[month-1].set_ylim(1, y_max)  # Set y-axis limit
    axs[month-1].grid(True, which='both', linestyle='--', linewidth=0.5)
    axs[month-1].set_title(month_names[month-1], fontsize=12)

    # Customize the x-axis and y-axis ticks
    axs[month-1].set_xticks([0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100])
    axs[month-1].set_yticks(
        [1,2,3,4,5,6,7,8,9,10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600]
    )
    
    # Set the y-axis formatter to scalar format
    axs[month-1].yaxis.set_major_formatter(ScalarFormatter())
    axs[month-1].tick_params(axis='both', which='major', labelsize=6)
    
    # Calculate discharge values at specific exceedance probabilities
    discharge_67 = np.interp(67, exceedance_probability, sorted_discharge)
    discharge_90 = np.interp(90, exceedance_probability, sorted_discharge)
    
    # Debugging statements to verify the calculations
    print(f'Month: {month_names[month-1]}')
    print(f'Exceedance Probabilities: {exceedance_probability.tolist()}')
    print(f'Sorted Discharge: {sorted_discharge.tolist()}')
    print(f'Discharge at 67%: {discharge_67}')
    print(f'Discharge at 90%: {discharge_90}')
    
    # Store the values in the dictionary
    discharge_at_probabilities['month'].append(month_names[month-1])
    discharge_at_probabilities['67%'].append(discharge_67)
    discharge_at_probabilities['90%'].append(discharge_90)

plt.tight_layout()
plt.savefig(r'C:\Users\dottacor\Documents2\GitFiles\Georgia_obs\flow_duration_curves_all_months.png')
plt.show()

# Print discharge values at 67% and 90% exceedance probabilities for each month
discharge_df = pd.DataFrame(discharge_at_probabilities)
print(discharge_df)


#%%


import cdsapi
import os
import zipfile

def retrieve_efas_seasonal_reforecast(year, month, output_folder):
    c = cdsapi.Client()

    leadtimes = list(range(24, 5161, 24))  # Generate lead times from 24 to 5160 hours in steps of 24 hours

    output_zip_path = os.path.join(output_folder, f'{year}{month}_EFAS_seasonal_reforecast.zip')
    output_nc_path = os.path.join(output_folder, f'{year}{month}_EFAS_seasonal_reforecast.nc')

    c.retrieve(
        'efas-seasonal-reforecast',
        {
            'system_version': 'version_4_0',
            'variable': 'river_discharge_in_the_last_24_hours',
            'model_levels': 'surface_level',
            'hyear': year,
            'hmonth': month,
            'leadtime_hour': leadtimes,
            'format': 'netcdf4.zip',
            'area': [
                43.5, 40, 40,
                47.5,
            ],
        },
        output_zip_path)  # Save file in specified directory

    # Unzip the downloaded file
    with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    # Get list of files extracted from the zip
    extracted_files = zip_ref.namelist()

    # Find the NetCDF file and rename it
    for file in extracted_files:
        if file.endswith('.nc'):
            os.rename(os.path.join(output_folder, file), output_nc_path)
            break

def main():
    start_year = 1991
    end_year = 2009
    start_month = 1
    end_month = 12
    output_folder = r"C:\Users\dottacor\Documents2\GitFiles\EFAS_Georgia"  # Specify output folder here

    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month + 1):
            month_str = f'{month:02d}'  # Format month as two digits
            print(f"Processing year {year}, month {month_str}...")
            retrieve_efas_seasonal_reforecast(year, month_str, output_folder)

if __name__ == "__main__":
    main()














#%%


