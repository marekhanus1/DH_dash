import numpy as np

# Initial data
data_names = np.array([["ekg", "ekgraw"],
                                ["flex", "flexraw"], 
                                ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"],                            
                                ["HR", "RESP"]], dtype=object)

print(data_names)

# Remove ["epochy_HR", "epochy_RESP", "epochy_RR-min", "epochy_RR-max", "epochy_SDNN", "epochy_RMSSD", "epochy_FlexDer"] by numpy slicing
data_names = np.delete(data_names, 2, axis=0)
print(data_names)