"""
Removes URLs from a file using a blacklist as an additional
command line parameter.
"""
from util import get_paths, parse_csv_line, append_to_filename
from util import benchmark_columns as columns

import os, sys, shutil

if len(sys.argv) < 3:
    print("usage: {} outputdir blacklist".format(sys.argv[0]))
    exit()

bm_file_path, _, _, _ = get_paths()
bm_trunc_file_path = append_to_filename(bm_file_path, "_trunc")
bl_file_path = sys.argv[2]

# Read all URLs from the blacklist file into list.
blacklisted_urls = []

with open(bl_file_path, "r") as f:
    for line in f:
        line = line.strip()

        # Ignore empty lines and comments.
        if line.startswith("#") or len(line) == 0:
            continue
        
        blacklisted_urls.append(line)

with open(bm_file_path, "r") as in_file:
    # Copy CSV header.
    out_file = open(bm_trunc_file_path, "w")
    out_file.write(next(in_file))

    # Write rows line by line except for the ones that
    # belong to a blacklisted URL.
    for line in in_file:
        if parse_csv_line(line)[columns["url"]] in blacklisted_urls:
            continue
        
        out_file.write(line)

    out_file.close()

# Copy original file.
shutil.copyfile(bm_file_path, append_to_filename(bm_file_path, "_orig"))
# Overwrite original benchmark file.
shutil.move(bm_trunc_file_path, bm_file_path)