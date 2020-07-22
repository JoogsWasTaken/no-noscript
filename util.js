const puppeteer = require("puppeteer-core");

/**
 * Returns a high resolution time in milliseconds.
 */
const hr = () => {
    let t = process.hrtime();
    return t[0] * 1e3 + t[1] / 1e6;
}

/**
 * Deletes all cookies on a browser page.
 * 
 * @param {puppeteer.Page} page 
 */
module.exports.deleteAllCookies = async (page) => {
    let cookies = await page.cookies();

    await Promise.all(cookies.map((cookie) => page.deleteCookie(cookie)));
}

/**
 * Simple timer utility that allows to measure time since
 * the call to the start function.
 */
module.exports.Timer = class {

    constructor() {
        this.startTime = -1;
    }

    /**
     * Starts the timer.
     */
    start() {
        this.startTime = -hr();
    }

    /**
     * Returns the milliseconds passed since the timer was started.
     */
    query() {
        return this.startTime + hr();
    }

}

/**
 * Writes an array of values to a writable stream.
 * 
 * @param {WritableStream} out Stream to write to.
 * @param {object[]} vals Array with values.
 */
module.exports.writeCSVRow = (out, vals) => {
    vals = vals.map((val) => {
        if (typeof val === "string") {
            return `"${val}"`;
        }

        return val;
    });

    out.write(vals.join(",") + "\n");
}