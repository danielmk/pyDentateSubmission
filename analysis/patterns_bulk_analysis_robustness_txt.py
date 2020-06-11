# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import os
import numpy as np

parent = "C:\\Users\\Daniel\\pyDentateData\\robustness\\frequencies\\"
all_files = [x for x in os.listdir(parent) if "figure" not in x if '.npz' in x]
all_input_data = [np.load(parent + x)['input_corrs'] for x in all_files]
all_output_data = [np.load(parent + x)['output_corrs'] for x in all_files]

parsed_files = np.array([x.split('_')[3:14] for x in all_files], dtype = np.float)

subtracted_Rs = np.array([(all_input_data[x] - all_output_data[x]) for x in range(len(all_input_data))])
subtracted_Rs_mean = subtracted_Rs.mean(axis=1)

bins = np.arange(0,1.1,0.1)
digitized_inputs = np.digitize(all_input_data, bins) - 1  # minus 1 to convert to indices
binned_Rs = np.zeros((digitized_inputs.shape[0], bins.shape[0]-1))
binned_ns = np.zeros((digitized_inputs.shape[0], bins.shape[0]-1))

for row_idx, row in enumerate(digitized_inputs):
    for col_idx, col in enumerate(row):
        binned_Rs[row_idx, col] += subtracted_Rs[row_idx, col_idx]
        binned_ns[row_idx, col] += 1

binned_mean_Rs = binned_Rs / binned_ns
binned_mean_Rs = np.nanmean(binned_mean_Rs, axis=1)

full_data = np.append(parsed_files, binned_mean_Rs[:,np.newaxis], axis=1)
np.savetxt("C:\\Users\\Daniel\\pyDentateData\\robustness\\aggregate_data.txt", full_data, delimiter = '\t')

# Maps parameters to their index in parsed_files
idx_map = {'nw-seed': 0,
           'input-seed': 1,
           'input_freq': 2,
           'input_scale': 3,
           'bc_decay': 4,
           'hc_decay': 5,
           'bc_delay': 6,
           'hc_delay': 7,
           'gc_weight': 8,
           'bc_weight': 9,
           'hc_weight': 10}

# Maps parameters to their tuned value
idx_map = {'nw-seed': 10000,
           'input-seed': 10000,
           'input_freq': 10,
           'input_scale': 1000,
           'bc_decay': 20,
           'hc_decay': 20,
           'bc_delay': 0.85,
           'hc_delay': 3.8,
           'gc_weight': 0.025,
           'bc_weight': 0.0012,
           'hc_weight': 0.006}



# Split the files by frequency
freqs = np.array([5,10,15,20,25,30,35,40,45,50,55,60,70,80,90,100])
freqs_dict = {
    str(x): subtracted_Rs_mean[np.argwhere(parsed_files[:, 2] == x)]
    for x in freqs
}

"""
for root, dirs, files in os.walk(parent):
    for name in files:
        if os.path.isfile(root + '\\1_leutgeb-measure-tresolved_len-bin_1000.txt'):
            done += 1
            break
        elif name.endswith('spike_data.npz'):
            print(root)
            data_path = root + '\\'
            get_outputs.similarity_measure_leutgeb_output_tresolved_directory(data_path, 1000)
            break
        elif name.startswith('input_patterns') & name.endswith('npz'):
            print(root)
            data_path = root + '\\'
            get_inputs.similarity_measure_leutgeb_inputs_directory(data_path, 1000)
            break
print(str(done) + ' files already present')
"""