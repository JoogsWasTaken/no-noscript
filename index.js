const screenshotDir = "screenshots";
const noscriptDir = "noscript";
const scriptDir = "script";
const metricsDir = "metrics";
const benchmarkFile = "benchmark.csv";

const { BenchmarkTimes, BenchmarkResult } = require("./model");
const util = require("./util");

const fs = require("fs");
const path = require("path");
const debug = require("debug")("no-noscript");

const args = require("minimist")(process.argv.slice(2), {
    string: [ "output-dir", "revision", "url" ],
    alias: {
        "output-dir": [ "o" ],
        "revision": [ "r" ],
        "url": [ "u" ],
        "iterations": [ "i" ],
        "attempts": [ "a" ]
    },
    boolean: [ "nowarn" ],
    default: {
        "nowarn": false,
        "output-dir": ".",
        "iterations": 5,
        "attempts": 3
    }
});

// Command line arg validation.
if (!args["url"]) {
    debug("URL required.");
    process.exit(1);
}

// URL to benchmark.
let url;

try {
    url = new URL(args["url"].trim());
} catch (err) {
    debug("Invalid URL.");
    process.exit(1);
}

if (!args["output-dir"]) {
    debug("Output directory required.");
    process.exit(1);
}

// === OUTPUT DIRECTORY STRUCTURE ===

// Directory to write all data to.
const outputDir = args["output-dir"].trim();

// Create directory if it doesn't exist yet.
if (!fs.existsSync(outputDir)) {
    debug("Output directory doesn't exist yet. Creating it.");
    fs.mkdirSync(outputDir);
}

// Define output directory paths.
const screenshotPath = path.join(outputDir, screenshotDir);
const metricsPath = path.join(outputDir, metricsDir);
const noscriptPath = path.join(outputDir, noscriptDir);

for (let p of [ screenshotPath, metricsPath, noscriptPath ]) {
    if (!fs.existsSync(p)) {
        debug("Creating directory at %s.", p);
        fs.mkdirSync(p);
    }
}

// Optional benchmark arguments.
const benchmarkIterations = args["iterations"];
const maxAttempts = args["attempts"];

// Initialize puppeteer.
const browserRevision = args["revision"];
const puppeteer = require("puppeteer-core");

(async () => {

    // === PUPPETEER INITIALIZATION ===

    // Load the specified browser revision, or choose the most
    // recent one if none was specified.
    const fetcher = puppeteer.createBrowserFetcher();
    const localRevs = await fetcher.localRevisions();
    let revInfo = null;

    // Was a revision specified?
    if (browserRevision) {
        debug("Selected revision %s.", browserRevision);

        // Does this revision exist on disk?
        if (localRevs.includes(browserRevision)) {
            debug("Present on local disk.");
            revInfo = fetcher.revisionInfo(browserRevision);
        } else {
            debug("Not present on local disk.");

            // Can the revision be downloaded?
            if (await fetcher.canDownload(browserRevision)) {
                debug("Revision available, downloading.");
                debug("This might take a while.");

                // Download the revision.
                revInfo = await fetcher.download(browserRevision);
            } else {
                debug("Revision not available, cancelling.");
                process.exit(1);
            }
        }
    } else {
        debug("No revision specified.");

        // Are no revisions available on the disk?
        if (localRevs.length === 0) {
            debug("No revisions locally available, cancelling.");
            process.exit(1);
        } else {
            // Select the most recent revision with some janky syntax.
            const recentRev = localRevs.map(x => parseInt(x)).sort((a, b) => b - a)[0].toString();
            debug("Using most recent revision %s.", recentRev);

            revInfo = fetcher.revisionInfo(recentRev);
        }
    }
    
    debug("Launching browser from %s.", revInfo.executablePath);

    const browser = await puppeteer.launch({
        executablePath: revInfo.executablePath,
        defaultViewport: {
            width: 1920,
            height: 1080
        }
    });

    // Use incognito context so no user data persists.
    const ctx = await browser.createIncognitoBrowserContext();

    /**
     * Performs a benchmark against the specified URL.
     * 
     * @param {boolean} jsEnabled `true` if scripts should be allowed, `false` otherwise
     */
    const benchmarkUrl = async (jsEnabled) => {
        const urlStr = url.toString();
        const page = await ctx.newPage();
        page.setCacheEnabled(false);
        page.setJavaScriptEnabled(jsEnabled);

        // Construct file name for raw data.
        const urlFileName = `${url.host.replace(".", "_")}_${!jsEnabled ? "no" : ""}js_${Date.now()}`;
        const screenshotFilePath = path.join(screenshotPath, urlFileName + ".png");
        const metricsFilePath = path.join(metricsPath, urlFileName + ".json");
        const noscriptFilePath = path.join(noscriptPath, urlFileName + ".html");

        debug("Testing %s. (%d iterations, JS %s)", urlStr, benchmarkIterations, jsEnabled ? "enabled" : "disabled");

        // Do first navigation to take screenshot and check for noscript presence.
        await page.goto(urlStr, {
            waitUntil: [ "load", "domcontentloaded" ]
        });

        // Count script tags.
        const scriptCount = (await page.$$("script")).length;

        // Process noscript tags.
        let noscriptHTMLs = await page.$$eval("noscript", els => els.map(e => e.outerHTML));
        let noscriptFound = noscriptHTMLs.length > 0;
        
        debug("Noscript tag %s.", (noscriptFound ? "" : "not ") + "found");

        // Save noscript contents if they exist.
        if (noscriptFound) {
            debug("Saving noscript contents at %s.", noscriptFilePath);
            fs.writeFileSync(noscriptFilePath, noscriptHTMLs.join("\n"));
        }

        // Take screenshot.
        debug("Saving screenshot at %s.", screenshotFilePath);

        await page.screenshot({
            path: screenshotFilePath,
            fullPage: false
        });

        await util.deleteAllCookies(page);

        const times = new BenchmarkTimes();
        const timer = new util.Timer();
        let metrics = [ await page.metrics() ];

        // Handler for DomContentLoaded event.
        page.on("domcontentloaded", () => {
            let t = timer.query();

            times.domLoadedEventFired.push(t);
            debug("  DomContentLoaded: %d ms.", t);
        });

        // Handler for load event.
        page.on("load", () => {
            let t = timer.query();

            times.loadEventFired.push(t);
            debug("  Load: %d ms.", t);
        });

        // Additional response handler.
        if (!args["nowarn"]) {
            page.on("response", (e) => {
                if (e.fromCache()) {
                    debug("WARNING! Response from cache although caching is disabled.");
                    debug("URL of the response is %s.", e.url());
                }
            });
        }

        // Run timings.
        for (let i = 0; i < benchmarkIterations; i++) {
            debug("Iteration %d.", i + 1);
            timer.start();

            await page.goto(urlStr, {
                waitUntil: [ "load", "domcontentloaded", "networkidle0" ]
            });

            // Subtract 500 ms because networkidle fires 500 ms after
            // the last bit of network traffic was carried out.
            let t = timer.query() - 500;
            times.networkIdleFired.push(t);

            debug("  Network idle: %d ms.", t);

            // Append metrics.
            metrics.push(await page.metrics());
            await util.deleteAllCookies(page);
        }

        await page.close();

        // Save metrics for later evaluation.
        debug("Saving metrics to %s.", metricsFilePath);
        fs.writeFileSync(metricsFilePath, JSON.stringify(metrics));

        return new BenchmarkResult(url, jsEnabled, noscriptFound, scriptCount, urlFileName, times);
    }

    const benchmarkFilePath = path.join(outputDir, benchmarkFile);
    const writeHeader = !fs.existsSync(benchmarkFilePath);

    // Open CSV file in append mode.
    const outFile = fs.createWriteStream(benchmarkFilePath, { flags: "a" });

    if (writeHeader) {
        debug("Output file doesn't exist yet. Creating header.");

        let csvHeader = [ "url", "timestamp", "jsEnabled", "scriptCount", "noscript", "dataFileName" ];

        // Create a column for every sample.
        for (let h of [ "load", "domload", "idle" ]) {
            for (let i = 0; i < benchmarkIterations; i++) {
                csvHeader.push(`${h}${i + 1}`);
            }
        }

        util.writeCSVRow(outFile, csvHeader);
    }

    // Try until it works.
    for (let i = 0; i < maxAttempts; i++) {
        debug("Attempt %d.", i + 1);

        try {
            const resultJs = await benchmarkUrl(true);
            const resultNoJs = await benchmarkUrl(false);

            // Write the row to the benchmark file.
            for (let r of [ resultJs, resultNoJs ]) {
                let row = [ r.url.toString(), r.timestamp, r.jsEnabled, r.scriptCount, r.noscriptExists, r.dataFileName ];
                let b = r.times;

                for (let t of b.loadEventFired) { row.push(t); }
                for (let t of b.domLoadedEventFired) { row.push(t); }
                for (let t of b.networkIdleFired) { row.push(t); }

                util.writeCSVRow(outFile, row);
            }

            // Done with the benchmark for this page.
            break;
        } catch (err) {
            debug("Error during benchmark: %O.", err);
            debug("Trying to close pages.");

            try {
                // Attempt to close open pages.
                for (let page of await ctx.pages()) {
                    await page.close();
                }
            } catch (err) {
                // Something weird is going on and I don't like it.
                debug("Failed to close pages. %O", err);
                debug("Smells like something more severe is off. Aborting quietly.");

                break;
            }
        }
    }

    // Close the output stream.
    outFile.end();

    await browser.close();
})().catch((err) => {
    debug("Top-level promise rejection. %O", err);
});