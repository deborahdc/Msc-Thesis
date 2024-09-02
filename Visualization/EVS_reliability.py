#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

def parse_reliability_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    reliability_data = {}

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            if threshold_value == 'LTE 1400.0':  # Filter for only LTE 1400.0
                reliability_values = [list(map(float, values.text.split(','))) for values in threshold.findall('data/values')]
                
                # Filter out -999 values
                reliability_values = [[val for val in sublist if val != -999.0] for sublist in reliability_values]
                
                if threshold_value not in reliability_data:
                    reliability_data[threshold_value] = {}
                
                reliability_data[threshold_value][lead_hour] = reliability_values
    
    return lead_hours, reliability_data

# Set the file path
xml_file = r'C:\Users\dottacor\evs-SEASHYPE\evs-out\Lobith.Q.9503451.Reliability_diagram.xml'
output_file = r'C:\Users\dottacor\Documents2\GitFiles\Visualization_plots\Netherlands\EVS\drought_season\Python\Lobith.Q.9503451.Reliability_diagram_selected.png'

# Parse the XML data
lead_hours, reliability_data = parse_reliability_data(xml_file)

# Convert lead hours to weeks for the desired lead times
lead_times = ['24 hours'] + [f'{int(lh / 168)} weeks' for lh in lead_hours[1:]]

# Filter for the desired lead times: 2 weeks and 4 weeks
desired_lead_times = [2 * 168, 4 * 168]  # Convert weeks to hours

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Create subplots
fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # Two subplots for 2 weeks and 4 weeks
axs = axs.flatten()

# Get a colormap
cmap = plt.get_cmap("viridis")
colors = cmap(np.linspace(0, 1, len(desired_lead_times)))
markers = ['o', 's', 'D', '^', 'v', 'p', '*', 'h', 'x', '+']  # Different marker shapes

# Plot the reliability diagrams for the desired lead times
for idx, lead_hour in enumerate(desired_lead_times):
    if lead_hour in reliability_data['LTE 1400.0']:
        ax = axs[idx]
        reliability_values = reliability_data['LTE 1400.0'][lead_hour]
        if len(reliability_values) > 1:  # Ensure there are at least two lists (x and y values)
            forecast_prob = reliability_values[0]
            observed_freq = reliability_values[1]
            if len(forecast_prob) > 0 and len(observed_freq) > 0:
                # Use points instead of lines, vary point size by lead time, and add transparency
                point_size = 80  # Fixed point size for better visibility
                ax.scatter(forecast_prob, observed_freq, s=point_size, label='LTE 1400.0', color=colors[idx], marker=markers[idx], alpha=0.6)

        # Add the diagonal line for perfect reliability
        ax.plot([0, 1], [0, 1], linestyle='--', color='gray')

        # Customize the subplot
        ax.set_title(f'Lead Time: {int(lead_hour / 168)} weeks', fontsize=14)
        ax.set_xlabel('Forecast Probability', fontsize=12)
        ax.set_ylabel('Observed Frequency', fontsize=12)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)

# Adjust layout
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust rect to make space for legend

# Save the plot
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Reliability diagram for LTE 1400 with selected lead times saved as {output_file}")


#%%
