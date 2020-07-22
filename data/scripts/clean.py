"""
Removes redundant files in the subdirectories of the output
file that don't belong to any row present in the main table.
"""
from util import get_paths, parse_csv_line, try_remove
from util import benchmark_columns as columns

import os

bm_file_path, metrics_dir_path, noscript_dir_path, screenshots_dir_path = get_paths()

# List all subdirectory contents.
metrics_dir_list = os.listdir(metrics_dir_path)
noscript_dir_list = os.listdir(noscript_dir_path)
screenshots_dir_list = os.listdir(screenshots_dir_path)

with open(bm_file_path, "r") as f:
    # Skip CSV header.
    next(f)

    # Remove the files from the directory listings that are
    # referenced in the main table. In the end, the lists will
    # only contain files that need to be deleted.
    for line in f:
        data_file_name = parse_csv_line(line)[columns["dataFileName"]]

        try_remove(metrics_dir_list, data_file_name + ".json")
        try_remove(noscript_dir_list, data_file_name + ".html")
        try_remove(screenshots_dir_list, data_file_name + ".png")

# Remove unnecessary metrics files.
for x in metrics_dir_list:
    os.remove(os.path.join(metrics_dir_path, x))

# Remove unnecessary noscript files.
for x in noscript_dir_list:
    os.remove(os.path.join(noscript_dir_path, x))

# Remove unnecessary screenshots.
for x in screenshots_dir_list:
    os.remove(os.path.join(screenshots_dir_path, x))
