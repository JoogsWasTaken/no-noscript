"""
Computes some general stats about the results.
"""
from util import parse_csv_line, append_to_filename, get_paths, as_bool
from util import results_columns as columns

import os

def pct_format(x, y):
    """
    Returns x/y in percent as a formatted string with two
    decimal places.
    """
    return "{:.2f} %".format((x / y) * 100)

bm_file_path, _, _, _ = get_paths()
bm_results_path = append_to_filename(bm_file_path, "_results")

# Collect all CSV rows into this list.
rows = []

with open(bm_results_path) as f:
    # Skip CSV header.
    next(f)

    for line in f:
        line = parse_csv_line(line)
        line[1] = as_bool(line[1])
        line[2] = as_bool(line[2])

        for i in range(3, len(line)):
            line[i] = float(line[i])
        
        rows.append(line)

# Total amount of rows.
count = len(rows)

# Counters for several values.
noscript_count = 0
noscript_without_scripts_count = 0

script_count = 0
script_without_noscript_count = 0

for row in rows:
    if row[columns["noscript"]]:
        noscript_count += 1

        if not row[columns["scripts"]]:
            noscript_without_scripts_count += 1
    
    if row[columns["scripts"]]:
        script_count += 1

        if not row[columns["noscript"]]:
            script_without_noscript_count += 1

# Beautiful output.
print("Number of websites: {}".format(count))
print("Sites with scripts: {} ({})".format(script_count, pct_format(script_count, count)))
print("Sites with scripts without noscript: {} ({})".format(script_without_noscript_count, pct_format(script_without_noscript_count, count)))
print("Sites with noscript: {} ({})".format(noscript_count, pct_format(noscript_count, count)))
print("Sites with noscript without scripts: {} ({})".format(noscript_without_scripts_count, pct_format(noscript_without_scripts_count, noscript_count)))
