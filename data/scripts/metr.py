"""
Computes the median script execution time for every
website (doesn't work).
"""
from util import get_paths, parse_csv_line
from util import benchmark_columns as columns

import os, json

_, metrics_dir_path, _, _ = get_paths()
metrics_file_names = os.listdir(metrics_dir_path)

for file_name in metrics_file_names:
    # Skip metrics taken when JS was disabled.
    if "nojs" in file_name:
        continue

    file_path = os.path.join(metrics_dir_path, file_name)

    # List to load the JSON array with browser metrics into.
    metrics = []
    # List of script execution durations.
    script_timings = []

    with open(file_path, "r") as f:
        metrics = json.load(f)
    
    # Compute the difference in time between the current and
    # the previous sample taken.
    for i in range(1, len(metrics)):
        t = metrics[i]["ScriptDuration"] - metrics[i - 1]["ScriptDuration"]
        script_timings.append(t)
    
    script_timings.sort()
    median = script_timings[2] # len will always be 5 so hardcoding this (I know I shouldn't)

    # Beautifully pythonic
    print("{}:\t {} {}".format(file_name, "{:.2f}".format(median), [ "{:.2f}".format(x) for x in script_timings ]))