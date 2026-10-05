// expose.html mit Chromium zu PDF rendern (aufgerufen von build.py)
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }

(async () => {
  const launch = {};
  if (process.env.PLAYWRIGHT_BROWSERS_PATH === "/opt/pw-browsers") launch.executablePath = "/opt/pw-browsers/chromium";
  const browser = await chromium.launch(launch);
  const page = await browser.newPage();
  const [html = "expose.html", pdf = "Expose_Altenbaunaer_Strasse_26.pdf"] = process.argv.slice(2);
  await page.goto("file://" + path.join(__dirname, html), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(__dirname, pdf);
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  await browser.close();
  console.log(out);
})();
