import os
from glob import glob
import pandas as pd
import re
from collections import OrderedDict

annotation_input_dir = "/data-net/datasets/HMDB51/splits/testTrainMulti_7030_splits"
annotation_output_dir = "data/hmdb51/testTrainMulti_601030_splits"

# Function to extract video prefix
def extract_prefix(video_name):
    pattern = r'_(?:u|f|h)_'
    cleaned_data = re.sub(pattern, '_SEPARATOR_', video_name)
    return cleaned_data.split('_SEPARATOR_')[0]

# Swap 10 instances of 1 with 3 for a given video prefix
def swap_ones_with_threes(video_prefix, data, count):
    subcount = 0
    for i in range(len(data)):
        if extract_prefix(data[i][0]) == video_prefix and data[i][1] == 1:
            data[i][1] = 3
            subcount += 1
            if count + subcount == 10:
                return subcount
    
    return subcount

for filepath in sorted(glob(os.path.join(annotation_input_dir, "*.txt"))):
    fi = open(filepath, "r")
    basename, file_number_and_format = os.path.basename(filepath).split("_test_split")
    file_number, format = file_number_and_format.split(".")

    # Parsing data into a list of tuples
    parsed_data = [line.strip().split() for line in fi.readlines()]

    # Dictionary to store data by video prefix
    data_by_prefix = {}

    # Grouping data by video prefix
    for video_name, number in parsed_data:
        prefix = extract_prefix(video_name)
        if prefix not in data_by_prefix:
            data_by_prefix[prefix] = []
        data_by_prefix[prefix].append([video_name, int(number)])

    # List to store modified data
    modified_data = []

    # Swapping 10 instances of 1 with 3 for each video prefix
    count = 0
    for prefix, data in data_by_prefix.items():
        ids = sum([id == 1 for _, id in data])
        if count < 10 and count + ids <= 10:
            count += swap_ones_with_threes(prefix, data, count)
        modified_data.extend(data)

    # Printing the updated data
    os.makedirs(annotation_output_dir, exist_ok=True)
    fo = open(filepath.replace(annotation_input_dir, annotation_output_dir), "w")
    for video_name, number in modified_data:
        fo.write(video_name + " " + str(number) + " \n")
    fo.close()

    print(filepath, count)

    fi.close()

