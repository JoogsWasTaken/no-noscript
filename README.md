# no-noscript

Application that ran the test described in my [article about noscript usage and tracking](https://joogswastaken.github.io/posts/no-noscript). In order to run it yourself, clone this repository and install its dependencies with `npm i`.

If you want to be lazy and not bother with required and optional command line arguments, just execute `run.sh` and add the path to a file containing URLs to investigate on every line. `run.sh` contains the exact parameters used for the collected data in the original article. Additionally, it writes the application output to a log file called `noscript.log`.

If you want to fine-tune the application, take a look at the list of supported command line arguments if you decide to launch it directly using Node with `node index.js`.

```
Required:
    -u, --url           URL to test
    -o, --output-dir    Path to the output directory

Optional:
    -r, --revision      Chromium revision to use (defaults to latest)
    -a, --attempts      Amount of attempts to retry the specified URL if errors occur
    -i, --iterations    Amount of samples to collect for the specified URL
    --nowarn            Disables warnings if responses are loaded from cache
```

The application will create the output directory if it doesn't exist yet. It will then also create subdirectories for screenshots, browser metrics and the HTML content of `noscript` elements on visited pages. Load times, observations about `script` and `noscript` elements and page metadata are appended to a CSV file (and thus created if it doesn't exist yet) so subsequent application launches will write to the same file.

## Technical details

The application was run on July 2nd, 2020 on a VPS with Debian 4.19.0 to create the dataset that you can find by checking the README in the [data](data) directory.

* **CPU:** Single Core Intel Xeon Processor (2.1 GHz, 16 GB Cache)
* **Network:** downlink approx. 1.1 Gbit/s, uplink approx. 4.17 Mbit/s
* **RAM:** 2 GB
* **Storage:** 20 GB SSD

As for the application itself, it ran with the following software/package versions.

* **Chromium:** v81.0.4044.138 (revision 737173)
* **Node (NPM):** v12.18.1 (v6.14.5)
* **Puppeteer:** v4.0.1