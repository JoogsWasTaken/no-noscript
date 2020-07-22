const { URL } = require("url");

class BenchmarkTimes {

    /**
     * Holds samples for the various events on a website.
     */
    constructor() {
        this.domLoadedEventFired = [];
        this.loadEventFired = [];
        this.networkIdleFired = [];
    }

}

module.exports.BenchmarkTimes = BenchmarkTimes;

module.exports.BenchmarkResult = class {

    /**
     * Holds information about a completed benchmark.
     * 
     * @param {URL} url URL to the website that was benchmarked.
     * @param {boolean} jsEnabled `true` if scripts were enabled for this benchmark, `false` otherwise.
     * @param {boolean} noscriptExists `true` if a `noscript` tag was found, `false` otherwise.
     * @param {number} scriptCount Amount of `script` tags on the page.
     * @param {string} dataFileName Name of the files containing additional data in one of the subdirectories of the output directory.
     * @param {BenchmarkTimes} times Times recorded during this benchmark.
     */
    constructor(url, jsEnabled, noscriptExists, scriptCount, dataFileName, times) {
        this.timestamp = Date.now();
        this.url = url;
        this.jsEnabled = jsEnabled;
        this.noscriptExists = noscriptExists;
        this.scriptCount = scriptCount;
        this.dataFileName = dataFileName;
        this.times = times;
    }

}