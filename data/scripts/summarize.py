"""
Creates a table containing the sanitized results of the benchmark.
This assumes that the main table has been split up.

This file is probably the jankiest out of all.
"""
from util import parse_csv_line, get_paths, as_bool, append_to_filename
from util import benchmark_columns as columns

import os
from math import floor, ceil

def median(lst):
    """
    Computes the median value in a list of 
    numeric values.
    """
    lst.sort()
    l = len(lst)

    if l % 2 == 0:
        return (lst[floor(l / 2)] + lst[ceil(l / 2)]) / 2
    else:
        return lst[floor(l / 2)]

bm_file_path, _, _, _ = get_paths()

# File handles.
js_file = None
no_js_file = None
out_file = None

try:
    # Prepare header for output file.
    out_file = open(append_to_filename(bm_file_path, "_results"), "w")

    csv_header = [ "url", "noscript", "scripts" ]
    
    # Append headers for the median values.
    for x in [ "js", "no_js" ]:
        csv_header.append("median_load_" + x)
        csv_header.append("median_domload_" + x)
        csv_header.append("median_idle_" + x)
    
    out_file.write(",".join(csv_header) + "\n")

    js_file = open(append_to_filename(bm_file_path, "_js"), "r")
    nojs_file = open(append_to_filename(bm_file_path, "_no_js"), "r")

    # Skip CSV headers.
    next(js_file)
    next(nojs_file)

    while True:
        # Both are None if EOF is reached.
        js_line = next(js_file, None)
        nojs_line = next(nojs_file, None)

        if js_line is None or nojs_line is None:
            break
        
        js_row = parse_csv_line(js_line)
        nojs_row = parse_csv_line(nojs_line)

        # 6 = index first median col.
        for i in range(6, len(js_row)):
            # Parse values into floats.
            js_row[i] = float(js_row[i])
            nojs_row[i] = float(nojs_row[i])
        
        out_row = [
            # col 1: url
            js_row[columns["url"]],
            # col 2: noscript exists?
            as_bool(js_row[columns["noscript"]]) or as_bool(nojs_row[columns["noscript"]]),
            # col 3: script exists?
            (int(js_row[columns["scriptCount"]]) > 0) or (int(nojs_row[columns["scriptCount"]]) > 0),
            # col 4: median load (js on)
            median(js_row[6:11]),
            # col 5: median domload (js on)
            median(js_row[11:16]),
            # col 6: median idle (js on)
            median(js_row[16:21]),
            # col 7: median load (js off)
            median(nojs_row[6:11]),
            # col 8: median domload (js off)
            median(nojs_row[11:16]),
            # col 9: median idle (js off)
            median(nojs_row[16:21])
        ]

        out_file.write(",".join([ str(x) for x in out_row ]) + "\n")
except IOError as e:
    print("File IO error: {}".format(e))
finally:
    # The error handling may be the cleanest out of
    # all scripts though.
    if js_file is not None:
        js_file.close()
    
    if nojs_file is not None:
        nojs_file.close()
    
    if out_file is not None:
        out_file.close()