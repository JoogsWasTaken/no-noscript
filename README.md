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

## Step-by-step data collection guide

The following steps show the exact setup that I used when I ran the application for myself to collect the data showcased in my article. You can find the detailed specifications in the upcoming section. Lines starting with `#` are run as root.

```
~# apt install build-essential chromium curl git libgbm1
~# curl -sL https://deb.nodesource.com/setup_12.x | bash -
~# apt install nodejs
```

First, some necessary packages are installed. `chromium` is installed but not used by the benchmarking application. This is just to pull in all necessary dependencies. `libgbm1` is the only additional dependency required to be able to launch specific browser revisions using Puppeteer. In this example, Node 12 is installed as it is the stable release at the time of writing.

```
~# echo 1 > /proc/sys/kernel/unprivileged_userns_clone
~# useradd noscript-user
~# cd /opt
/opt# git clone https://github.com/JoogsWasTaken/no-noscript.git
/opt# chown -R noscript-user:noscript-user no-noscript
/opt# cd no-noscript && su noscript-user
```

User namespaces need to be enabled in order for Puppeteer to launch browser binaries. The first line accomplishes that but it doesn't persist until the next reboot. If you wish to permanently enable user namespaces (which you *might* not want to due to security reasons), use `sysctl -w kernel.unprivileged_userns_clone=1`. Next, a user account is created as well as the directory which will house the benchmark application. The account name can be chosen arbitrarily.

```
/opt/no-noscript$ DEBUG=no-noscript nohup ./run.sh pages.txt > noscript.log &
```

Finally, the application is started using `nohup` so terminal hangups won't interfere with the benchmark running in the background. Any modifications to the command line arguments to the benchmark application should be done in the `run.sh` file.

## Technical details

The application was run on July 2nd, 2020 on a VPS with Debian 10.3 running Linux 4.19.0 to create the dataset that you can find by checking the README in the [data](data) directory.

* **CPU:** Single Core Intel Xeon Processor (2.1 GHz, 16 GB Cache)
* **Network:** downlink approx. 1.1 Gbit/s, uplink approx. 4.17 Mbit/s
* **RAM:** 2 GB
* **Storage:** 20 GB SSD

As for the application itself, it ran with the following software/package versions.

* **Chromium:** v81.0.4044.138 (revision 737173)
* **Node (NPM):** v12.18.1 (v6.14.5)
* **Puppeteer:** v4.0.1