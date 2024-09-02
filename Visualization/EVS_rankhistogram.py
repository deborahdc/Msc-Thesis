#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

# Function to parse XML and extract rank histogram data
def parse_rank_histogram_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    rank_values = []
    relative_frequencies = []

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value == 'All data':
                rank_values.append(list(map(float, threshold.find('data/values').text.split(','))))
                relative_frequencies.append(list(map(float, threshold.findall('data/values')[1].text.split(','))))
    
    return lead_hours, rank_values, relative_frequencies

# Parse the XML data
xml_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Lobith.Q.9503451.Rank_histogram.xml'
lead_hours, rank_values, relative_frequencies = parse_rank_histogram_data(xml_file)

# Convert lead hours to weeks for all except the first lead time
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Define a custom palette similar to the original
custom_colors = [
    '#1f77b4',  # blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2'   # pink
]

# Plot the rank histogram
plt.figure(figsize=(12, 8))

for i, (lead_time, color) in enumerate(zip(lead_times, custom_colors)):
    plt.plot(rank_values[i], relative_frequencies[i], marker='o', markersize=4, label=f'Lead Time: {lead_time}', linestyle='-', color=color)

# Customize the plot
plt.title('Rank Histogram')
plt.xlabel('Bin Separating Ranked Ensemble Members')
plt.ylabel('Relative Frequency')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend to the upper left and ensure no overlap

# Set x-axis ticks to show all ensemble members from 1 to 26
plt.xticks(range(1, 27))

# Set y-axis ticks to show increments of 0.05
plt.yticks(np.arange(0, 0.85, 0.05))

# Save the plot
output_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Python\Lobith.Q.9503451.Rank_histogram_python_updated.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Rank histogram plot saved as {output_file}")


#%%
