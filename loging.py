import pandas as pd
import re

# Define the file path
log_file = "mylog.txt"

# Initialize lists to store extracted data
camtype_list = []
api_took_list = []

# Regular expressions to extract Camtype and API took
camtype_pattern = re.compile(r"Camtype\s*:\s*([\w_]+)")
api_took_pattern = re.compile(r"API took\s*:\s*([\d.]+)")

# Read log file line by line and extract data
with open(log_file, 'r') as file:
    for line in file:
        camtype_match = camtype_pattern.search(line)
        if camtype_match:
            camtype_list.append(camtype_match.group(1))

        api_took_match = api_took_pattern.search(line)
        if api_took_match:
            api_took_list.append(float(api_took_match.group(1)))

# Creating DataFrame
df = pd.DataFrame({'Camtype': camtype_list, 'API Took': api_took_list})
average_df = df.groupby('Camtype').mean().reset_index()
print(df)
print(average_df)
