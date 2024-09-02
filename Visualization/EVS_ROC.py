#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

# Function to parse XML and extract ROC data
def parse_roc_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    roc_data = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value != 'All data':
                threshold_value = '≤ ' + threshold_value.split(' ')[1].split('.')[0]  # Show only one digit
            fpr_values = list(map(float, threshold.find('data/values[1]').text.split(',')))
            tpr_values = list(map(float, threshold.find('data/values[2]').text.split(',')))
            
            if threshold_value not in roc_data:
                roc_data[threshold_value] = {}
            
            roc_data[threshold_value][lead_hour] = (fpr_values, tpr_values)
    
    return lead_hours, roc_data

# Parse the XML data
xml_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Lobith.Q.9503451.Relative_operating_characteristic.xml'
lead_hours, roc_data = parse_roc_data(xml_file)

# Convert lead hours to weeks for all except the first lead time
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Create subplots
fig, axs = plt.subplots(3, 3, figsize=(18, 18))  # Adjusted to 3x3 for 7 subplots
axs = axs.flatten()

# Get a colormap
cmap = plt.get_cmap("viridis")
colors = cmap(np.linspace(0, 1, len(roc_data)))

# Plot the ROC curves for each lead time
for idx, lead_hour in enumerate(lead_hours):  # No limit on lead_hours to include all
    ax = axs[idx]
    for (threshold, color) in zip(roc_data.keys(), colors):
        if lead_hour in roc_data[threshold]:
            fpr_values, tpr_values = roc_data[threshold][lead_hour]
            ax.plot(fpr_values, tpr_values, marker='o', markersize=4, label=f'{threshold}', linestyle='-', color=color)

    # Customize the subplot
    ax.set_title(f'Lead Time: {lead_times[idx]}')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(loc='lower right')
    ax.grid(False)  # Remove grid

# Adjust layout and remove unused subplots
for ax in axs[len(lead_hours):]:
    ax.remove()

# Adjust layout
plt.tight_layout()

# Save the plot
output_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Python\Lobith.Q.9503451.Relative_operating_characteristic_multiplot.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"ROC curve multiplot saved as {output_file}")











#%%
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os

# Function to parse XML and extract ROC data
def parse_roc_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    roc_data = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value != 'All data':
                threshold_value = '≤ ' + threshold_value.split(' ')[1].split('.')[0]  # Show only one digit
            fpr_values = list(map(float, threshold.find('data/values').text.split(',')))
            tpr_values = list(map(float, threshold.findall('data/values')[1].text.split(',')))
            
            if lead_hour not in roc_data:
                roc_data[lead_hour] = {}
            if threshold_value not in roc_data[lead_hour]:
                roc_data[lead_hour][threshold_value] = []
            
            roc_data[lead_hour][threshold_value].append((fpr_values, tpr_values))
    
    return roc_data

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
combined_roc_data = {}

# Parse each XML file and combine the data
for month_dir in month_dirs:
    xml_file = os.path.join(base_dir, month_dir, 'Lobith.Q.9503451.Relative_operating_characteristic.xml')
    if os.path.exists(xml_file):
        roc_data = parse_roc_data(xml_file)

        # Get the specific threshold for the current month
        threshold_value = f'≤ {threshold_mapping[month_dir]}'
        legend_label = f'{month_name_mapping[month_dir]} (≤ {threshold_mapping[month_dir]})'
        
        if legend_label not in combined_roc_data:
            combined_roc_data[legend_label] = {}
        
        for lh, data in roc_data.items():
            if lh not in combined_roc_data[legend_label]:
                combined_roc_data[legend_label][lh] = data[threshold_value]
            else:
                combined_roc_data[legend_label][lh].extend(data[threshold_value])

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

# Create subplots
fig, axs = plt.subplots(3, 3, figsize=(18, 18))  # Adjusted to 3x3 for 7 subplots
axs = axs.flatten()

lead_hours = sorted({lh for data in combined_roc_data.values() for lh in data})
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Plot the ROC curves for each lead time
for idx, lead_hour in enumerate(lead_hours):
    ax = axs[idx]
    for legend_label, color in colors.items():
        if lead_hour in combined_roc_data[legend_label]:
            for fpr_values, tpr_values in combined_roc_data[legend_label][lead_hour]:
                ax.plot(fpr_values, tpr_values, marker='o', markersize=4, linestyle='-', color=color, label=legend_label)
    ax.set_title(f'Lead Time: {lead_times[idx]}')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(loc='lower right')

# Adjust layout and remove unused subplots
for ax in axs[len(lead_hours):]:
    ax.remove()

# Adjust layout
plt.tight_layout()

# Save the plot
output_dir = os.path.join(base_dir, 'python')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'Lobith.Q.9503451.Relative_operating_characteristic_multiplot.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"ROC curve multiplot saved as {output_file}")

#%%