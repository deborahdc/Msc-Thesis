#%% Developed by Deborah Dotta, June 2024
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os

# Function to parse XML and extract data
def parse_roc_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    thresholds = []
    false_alarms = []
    true_alarms = []

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        lead_hours.append(lead_hour)
        
        threshold_data = result.find('threshold_data/threshold')
        if threshold_data is not None:
            threshold_value = threshold_data.find('threshold_value').text
            thresholds.append(threshold_value)
            
            false_alarm_values = list(map(float, threshold_data.findall('data/values')[0].text.split(',')))
            true_alarm_values = list(map(float, threshold_data.findall('data/values')[1].text.split(',')))
            
            # Reduce the number of points
            step = max(1, len(false_alarm_values) // 10)
            false_alarms.append(false_alarm_values[::step])
            true_alarms.append(true_alarm_values[::step])
    
    return lead_hours, thresholds, false_alarms, true_alarms

# Parse the XML data
xml_file = r'C:\Users\dottacor\evs-SEASHYPE\evs-out\Lobith.Q.9503451.Relative_operating_characteristic.xml'
lead_hours, thresholds, false_alarms, true_alarms = parse_roc_data(xml_file)

# Set font to Calibri
plt.rcParams["font.family"] = "Calibri"

# Scientific color palette
colors = plt.cm.tab10(np.linspace(0, 1, len(lead_hours)))

# Plot the ROC curve
plt.figure(figsize=(10, 6))
for i, lead_hour in enumerate(lead_hours):
    plt.plot(false_alarms[i], true_alarms[i], marker='o', markersize=4, color=colors[i], label=f'Lead Hour: {lead_hour}')  # Decrease point size

# Plot the random guess line
plt.plot([0, 1], [0, 1], linestyle='--', color='black', label='Random Guess (No Skill)')

# Customize the plot
plt.title('Relative Operating Characteristic (ROC) Curve')
plt.xlabel('Probability of False Detection (False Alarms)')
plt.ylabel('Probability of Detection (True Alarms)')
plt.legend(loc='lower right')

# Save the plot
output_file = os.path.splitext(xml_file)[0] + '_python.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

#%%

# Function to parse XML and extract CRPS data
def parse_crps_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    lead_hours = []
    thresholds = []
    mean_crps_values = []

    for result in root.findall('result'):
        lead_hour = int(float(result.find('lead_hour').text))  # Read lead time as integer
        
        for threshold in result.findall('threshold_data/threshold'):
            threshold_value = threshold.find('threshold_value').text
            mean_crps_element = threshold.find('data/values')
            if mean_crps_element is not None:
                try:
                    mean_crps = float(mean_crps_element.text)
                    lead_hours.append(lead_hour)
                    # Replace "GT" with ">" or any other required replacements
                    threshold_value = threshold_value.replace("GT", ">")
                    thresholds.append(threshold_value)
                    mean_crps_values.append(mean_crps)
                except ValueError as e:
                    print(f"Error parsing mean_crps value: {mean_crps_element.text}, Error: {e}")
            else:
                print(f"mean_crps element not found for lead_hour: {lead_hour}")
    
    return lead_hours, thresholds, mean_crps_values

# Parse the XML data
xml_file = r'C:\Users\dottacor\evs-SEASHYPE\evs-out\Lobith.Q.9503451.Mean_continuous_ranked_probability_score.xml'
lead_hours, thresholds, mean_crps_values = parse_crps_data(xml_file)

# Check if data was parsed correctly
if not lead_hours or not mean_crps_values:
    print("No data parsed from the XML file. Please check the XML structure.")
else:
    # Set font to Calibri
    plt.rcParams["font.family"] = "Calibri"

    # Plot the CRPS
    plt.figure(figsize=(12, 8))
    
    # Get unique thresholds
    unique_thresholds = set(thresholds)
    
    for threshold in unique_thresholds:
        crps_values = [mean_crps_values[i] for i in range(len(mean_crps_values)) if thresholds[i] == threshold]
        corresponding_lead_hours = [lead_hours[i] for i in range(len(lead_hours)) if thresholds[i] == threshold]
        plt.plot(corresponding_lead_hours, crps_values, marker='o', markersize=4, label=f'{threshold}', linestyle='-')

    # Customize the plot
    plt.title('Mean Continuous Ranked Probability Score (CRPS)', fontsize=16)
    plt.xlabel('Forecast lead time (hours)', fontsize=14)
    plt.ylabel('CRPS (m³/s)', fontsize=14)
    plt.xticks(sorted(set(lead_hours)), fontsize=12)  # Only show unique lead times on x-axis
    plt.yticks(fontsize=12)
    plt.legend(loc='upper left', fontsize=12)
    
    # Save the plot
    output_file = os.path.splitext(xml_file)[0] + '_python.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()











#%%
