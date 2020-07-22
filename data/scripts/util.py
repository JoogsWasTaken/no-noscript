"""
Collection of utilities.
"""
import os
import sys

results_columns = {
    "url":                      0,
    "noscript":                 1,
    "scripts":                  2,
    "js_on_median_load":        3,
    "js_on_median_domload":     4,
    "js_on_median_idle":        5,
    "js_off_median_load":       6,
    "js_off_median_domload":    7,
    "js_off_median_idle":       8
}

benchmark_columns = {
    "url":          0,
    "timestamp":    1,
    "jsEnabled":    2,
    "scriptCount":  3,
    "noscript":     4,
    "dataFileName": 5
}

def try_remove(lst, item):
    """
    Tries to remove the specified item from a list and 
    silently fails if the item doesn't exist.
    """
    try:
        lst.remove(item)
    except Exception:
        pass

def get_paths():
    """
    Gets the output path from the command line and formats
    the paths to the respective subdirectories.
    """
    if len(sys.argv) < 2:
        print("usage: {} outputdir [args...]".format(sys.argv[0]))
        exit()
    
    base_dir_path = sys.argv[1]

    return (os.path.join(base_dir_path, "benchmark.csv"), 
        os.path.join(base_dir_path, "metrics"), 
        os.path.join(base_dir_path, "noscript"), 
        os.path.join(base_dir_path, "screenshots"))

def as_bool(x):
    """
    Returns True if the given string in lowercase equals "true",
    False otherwise.
    """
    return True if x.lower() == "true" else False

def append_to_filename(path, suffix):
    """
    Appends a suffix to a filename, e.g. append_to_filename("test.csv", "_2")
    will return "test_2.csv".
    """
    name, ext = os.path.splitext(path)
    return name + suffix + ext

def parse_csv_line(line):
    """
    Splits a line of comma seperated values into a list of
    values. Removes leading and trailing quotes if there are
    any.
    """
    parsed_line = []

    for x in line.split(","):
        if x[0] == "\"" and x[-1] == "\"":
            x = x[1:-1]
        
        parsed_line.append(x.strip())
    
    return parsed_line