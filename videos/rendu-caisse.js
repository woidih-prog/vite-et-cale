// Fabrique 29-deux-etudiantes-en-caisse.mp4 à partir de caisse.html (même principe que rendu.js). Usage : node rendu-caisse.js
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");
const IPS = 30;
(async () => {
  const nav = await chromium.launch();
  const page = await nav.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", e => { console.error(e.message); process.exit(1); });
  await page.goto("file://" + path.join(__dirname, "caisse.html") + "?rendu");
  await page.evaluate(() => document.fonts.ready); await page.waitForLoadState("networkidle");
  const { duree, nom, musique } = await page.evaluate(() => ({ duree: window.DUREE, nom: window.NOM, musique: window.MUSIQUE }));
  const sortie = path.join(__dirname, nom + ".mp4");
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(IPS), "-c:v", "mjpeg", "-i", "-",
    "-stream_loop", "-1", "-i", path.join(__dirname, "musique", musique + ".m4a"), "-af", `volume=3dB,afade=t=out:st=${duree / 1000 - 1.2}:d=1.2`,
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", String(duree / 1000),
    "-movflags", "+faststart", sortie], { stdio: ["pipe", "inherit", "inherit"] });
  const total = Math.round(duree / 1000 * IPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(ms => window.seek(ms), i * 1000 / IPS);
    const img = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise((ok, ko) => ff.on("close", c => c ? ko(new Error("ffmpeg " + c)) : ok()));
  console.log(sortie); await nav.close();
})();
