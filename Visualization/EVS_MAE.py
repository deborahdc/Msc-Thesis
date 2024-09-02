#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

# Function to parse XML and extract mean absolute error data
def parse_mae_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    mae_values = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value != 'All data':
                threshold_value = '≤ ' + threshold_value.split(' ')[1].split('.')[0]  # Show only one digit
            mae_value = float(threshold.find('data/values').text)
            
            if threshold_value not in mae_values:
                mae_values[threshold_value] = []
            
            mae_values[threshold_value].append(mae_value)
    
    return lead_hours, mae_values

# Parse the XML data
xml_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Lobith.Q.9503451.Mean_absolute_error.xml'
lead_hours, mae_values = parse_mae_data(xml_file)

# Convert lead hours to weeks for all except the first lead time
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Get a colormap
cmap = plt.get_cmap("viridis")
colors = cmap(np.linspace(0, 1, len(mae_values)))

# Plot the mean absolute error
plt.figure(figsize=(12, 8))

for (threshold, color) in zip(mae_values.keys(), colors):
    plt.plot(lead_times, mae_values[threshold], marker='o', markersize=4, label=f'{threshold}', linestyle='-', color=color)

# Customize the plot
plt.title('Mean Absolute Error (MAE) of the ensemble average')
plt.xlabel('Lead Time')
plt.ylabel('MAE (m³/s)')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend to the upper left and ensure no overlap

# Set y-axis ticks to show increments of 50
plt.yticks(np.arange(0, max(map(max, mae_values.values())) + 50, 50))

# Save the plot
output_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Python\Lobith.Q.9503451.Mean_absolute_error_python_updated.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Mean absolute error plot saved as {output_file}")














#%%
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os

# Function to parse XML and extract mean absolute error data
def parse_mae_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    mae_values = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value != 'All data':
                threshold_value = '≤ ' + threshold_value.split(' ')[1].split('.')[0]  # Show only one digit
            mae_value = float(threshold.find('data/values').text)
            
            if threshold_value not in mae_values:
                mae_values[threshold_value] = {}
            
            mae_values[threshold_value][lead_hour] = mae_value
    
    return lead_hours, mae_values

# Directory containing the XML files
base_dir = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS'

# List of directories (representing months)
month_dirs = ['4_9', '5', '6', '7', '8']

# Month-to-threshold mapping
threshold_mapping = {
    '4_9': '1000',
    '5': '1400',
    '6': '1300',
    '7': '1200',
    '8': '1100'
}

# Month-to-name mapping
month_name_mapping = {
    '4_9': 'April and September',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August'
}

# Initialize combined data
combined_lead_hours = set()
combined_mae_values = {}

# Parse each XML file and combine the data
for month_dir in month_dirs:
    xml_file = os.path.join(base_dir, month_dir, 'Lobith.Q.9503451.Mean_absolute_error.xml')
    if os.path.exists(xml_file):
        lead_hours, mae_values = parse_mae_data(xml_file)
        combined_lead_hours.update(lead_hours)

        # Get the specific threshold for the current month
        threshold_value = f'≤ {threshold_mapping[month_dir]}'
        if threshold_value in mae_values:
            legend_label = f'{month_name_mapping[month_dir]} (≤ {threshold_mapping[month_dir]})'
            if legend_label not in combined_mae_values:
                combined_mae_values[legend_label] = {}
            for lh, mae in zip(lead_hours, mae_values[threshold_value].values()):
                if lh not in combined_mae_values[legend_label]:
                    combined_mae_values[legend_label][lh] = []
                combined_mae_values[legend_label][lh].append(mae)

combined_lead_hours = sorted(combined_lead_hours)
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in combined_lead_hours[1:]]

# Averaging the MAE values for each threshold and lead time
averaged_mae_values = {}
for legend_label, values in combined_mae_values.items():
    averaged_mae_values[legend_label] = []
    for lh in combined_lead_hours:
        if lh in values:
            averaged_mae_values[legend_label].append(np.nanmean(values[lh]))
        else:
            averaged_mae_values[legend_label].append(np.nan)

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Manually map the viridis colors to the thresholds
cmap = plt.get_cmap("viridis")
viridis_colors = cmap(np.linspace(0, 1, 7))  # 7 colors from viridis

# Define specific colors for each threshold using the mapped colors
colors = {
    'April and September (≤ 1000)': viridis_colors[2],
    'August (≤ 1100)': viridis_colors[3],
    'July (≤ 1200)': viridis_colors[4],
    'June (≤ 1300)': viridis_colors[5],
    'May (≤ 1400)': viridis_colors[6]
}

# Plot the mean absolute error
plt.figure(figsize=(12, 8))

for legend_label, color in colors.items():
    if legend_label in averaged_mae_values:
        plt.plot(lead_times, averaged_mae_values[legend_label], marker='o', markersize=4, label=f'{legend_label}', linestyle='-', color=color)

# Customize the plot
plt.title('Mean Absolute Error (MAE) of the ensemble average')
plt.xlabel('Lead Time')
plt.ylabel('MAE (m³/s)')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend to the upper left and ensure no overlap

# Set y-axis ticks to show increments of 50
plt.yticks(np.arange(0, np.nanmax([np.nanmax(values) for values in averaged_mae_values.values()]) + 50, 50))

# Save the plot
output_dir = os.path.join(base_dir, 'python')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'Lobith.Q.9503451.Mean_absolute_error_combined.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Mean absolute error plot saved as {output_file}")

#%%