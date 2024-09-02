#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

# Function to parse XML and extract sample size data
def parse_sample_size_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    sample_sizes = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value != 'All data':
                threshold_value = '≤ ' + threshold_value.split(' ')[1]
            sample_size = float(threshold.find('data/values').text)
            
            if threshold_value not in sample_sizes:
                sample_sizes[threshold_value] = []
            
            sample_sizes[threshold_value].append(sample_size)
    
    return lead_hours, sample_sizes

# Parse the XML data
xml_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Lobith.Q.9503451.Sample_size.xml'
lead_hours, sample_sizes = parse_sample_size_data(xml_file)

# Convert lead hours to weeks for all except the first lead time
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Get a colormap
cmap = plt.get_cmap("viridis")
colors = cmap(np.linspace(0, 1, len(sample_sizes)))

# Plot the sample size
plt.figure(figsize=(12, 8))

for (threshold, color) in zip(sample_sizes.keys(), colors):
    plt.plot(lead_times, sample_sizes[threshold], marker='o', markersize=4, label=f'{threshold}', linestyle='-', color=color)

# Customize the plot
plt.title('Number of verification pairs available')
plt.xlabel('Lead Time')
plt.ylabel('Sample Size')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend to the upper left and ensure no overlap

# Set y-axis ticks to show increments of 5
plt.yticks(np.arange(0, max(map(max, sample_sizes.values())) + 5, 5))

# Save the plot
output_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Python\Lobith.Q.9503451.Sample_size_python_updated.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Sample size plot saved as {output_file}")

#%%
