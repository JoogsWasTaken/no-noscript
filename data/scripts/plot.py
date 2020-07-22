from util import get_paths, parse_csv_line, as_bool, append_to_filename
from util import results_columns as columns

import sys, os

# Determine amount of command line arguments.
argc = len(sys.argv) - 1

if argc < 2:
    print("usage: {} outputdir plot".format(sys.argv[0]))
    exit()

action = sys.argv[2]
plot_types = [ "hist_load", "hist_domload", "hist_idle" ]

if action not in plot_types:
    print("plot argument must be one of: {}".format(", ".join(plot_types)))
    exit()

# matplotlib is quite massive so we're only importing it now.
import matplotlib
import matplotlib.pyplot as plt

bm_file_path, _, _, _ = get_paths()
bm_results_file_path = append_to_filename(bm_file_path, "_results")

# Read results file into rows field.
rows = []

with open(bm_results_file_path) as f:
    # Skip CSV header.
    next(f)

    for line in f:
        line = parse_csv_line(line)
        line[1] = as_bool(line[1])
        line[2] = as_bool(line[2])

        for i in range(3, len(line)):
            line[i] = float(line[i])
        
        rows.append(line)

# Create basic figure.
fig, axes = plt.subplots(figsize=(6, 3))

if action.startswith("hist_"):
    hist_data = action[5:] # Strip hist_ at beginning.
    hist_title = ""
    # Contains indices of column containing measurements for
    # when JS is on (index 0) and JS is off (index 1).
    data_columns = ()

    if hist_data == "load":
        hist_title = "Median time until load event fired"
        data_columns = (columns["js_on_median_load"], columns["js_off_median_load"])
    elif hist_data == "domload":
        hist_title = "Median time until DOMContentLoaded event fired"
        data_columns = (columns["js_on_median_domload"], columns["js_off_median_domload"])
    elif hist_data == "idle":
        hist_title = "Median time until no more network connections"
        data_columns = (columns["js_on_median_idle"], columns["js_off_median_idle"])
    
    # Prepre lists for x values.
    x_js = []
    x_nojs = []

    for row in rows:
        # Divide by 1000 so we get time in seconds.
        x_js.append(row[data_columns[0]] / 1000)
        x_nojs.append(row[data_columns[1]] / 1000)
    
    # Draw grid.
    axes.grid(True)

    # 30 seconds, 120 bins = 1 bin is 250 milliseconds.
    axes.hist(x_js, histtype="step", bins=120, range=(0, 30), label="JS enabled", fill=True, facecolor="#17becf40")
    axes.hist(x_nojs, histtype="step", bins=120, range=(0, 30), label="JS disabled", fill=True, facecolor="#bcbd2240")

    axes.legend()
    axes.set_xlabel("Time in seconds")
    axes.set_ylabel("Number of websites")
    axes.set_title(hist_title)

    fig.tight_layout()
    plt.show()