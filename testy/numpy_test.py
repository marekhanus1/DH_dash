import numpy as np
from itertools import chain

data_names = np.array([["ekg", "ekgraw"],
        ["flex", "flexraw"], 
        ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD"],
        ["HR", "RESP"]], dtype=object)


print()

def find_row_col_with_shape(array, index):
    current_index = 0
    num_rows = array.shape[0]  # Total number of rows
    
    for row_idx in range(num_rows):
        row_length = len(array[row_idx])  # Length of the current row
        if current_index + row_length > index:
            col_idx = index - current_index  # Calculate the column index
            return row_idx, col_idx
        current_index += row_length
        
    return None  # If index is out of bounds

row, col = find_row_col_with_shape(data_names, 4)
print(row, col)
print(data_names[row][col])


import json

with open('components/DH_config.json', 'r') as file:
    config = json.load(file)
print(config)