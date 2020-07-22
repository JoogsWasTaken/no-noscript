"""
Splits main table into two tables: one only containing rows
where JS was enabled and one where JS was disabled.
"""
from util import get_paths, parse_csv_line, append_to_filename, as_bool
from util import benchmark_columns as columns

import os

bm_file_path, _, _, _ = get_paths()
bm_js_file_path = append_to_filename(bm_file_path, "_js")
bm_no_js_file_path = append_to_filename(bm_file_path, "_no_js")

with open(bm_file_path, "r") as f:
    out_js = open(bm_js_file_path, "w")
    out_no_js = open(bm_no_js_file_path, "w")

    # Get CSV header and write them to both output files.
    csv_header = next(f)

    out_js.write(csv_header)
    out_no_js.write(csv_header)

    for line in f:
        # Write to respective file if the jsenabled column
        # is either true or false.
        if as_bool(parse_csv_line(line)[columns["jsEnabled"]]):
            out_js.write(line)
        else:
            out_no_js.write(line)
    
    out_js.close()
    out_no_js.close()