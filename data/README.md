# Data evaluation scripts

Use [this link](https://mega.nz/file/hkYkmCYB#vwAo8y5vSP_u4W_EtVIBBRDEdsCFMFhWyhMR5Nnt1Dg) to obtain a copy of the raw data (~428 MB) that I used in order to produce the results in my article with all of its imperfections. You'll also find scripts that I used to work with the data, a list of all websites that I tested and the list of websites that I had to remove during my manual review of the dataset.

To reproduce the results that I got, make sure you have Python 3 installed (I didn't test it with Python 2), check if you have the `lxml` and `matplotlib` packages installed extract the archive into this directory. You should have the application log from when the application was executed and a directory called `output` to work with. Switch into the `scripts` directory and execute them in the following order.

```
python3 trunc.py ../output ../blacklist.txt
python3 clean.py ../output
python3 split.py ../output
python3 summarize.py ../output
```

From top to bottom, these scripts:

* remove unwanted URLs from the dataset (copying the original)
* remove redundant data in the subdirectories of the output directory
* split the dataset into two: one containing samples when JavaScript was enabled and one when it was disabled
* summarize the final results into an extra file

With all intermediate files created, you can now execute the following scripts to crunch some numbers and values.

```
python3 stats.py ../output
python3 noscr.py ../output
python3 metr.py ../output
python3 plot.py ../output <hist_load|hist_domload|hist_idle>
```

Again, from top to bottom, these scripts:

* compute some general numbers (`noscript` uses etc.)
* categorize the HTML content within the `noscript` tags for every website
* compute the median script execution time for every website (this doesn't work reliably)
* generate the histograms of times for different loading states

**Important!** These scripts have been written for my own dataset. If you decide to create a dataset on your own and use the scripts on it, there is a chance that they will not function as intended. Especially `noscr.py` is prone to errors since a lot of tags will fly under the radar. All categorizations are based on what I observed in my own dataset. Also, it makes sense to send the output of the `noscr.py` script to a file because the amount of warnings about undetected tags can be a bit overwhelming.