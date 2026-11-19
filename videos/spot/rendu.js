// Rendu du spot : une capture par image (30 i/s) de spot.html, puis ffmpeg ajoute son.wav.
const { chromium } = require("playwright"); const { spawn } = require("child_process"); const path = require("path");
const IPS = 30;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on("pageerror", e => { console.error(e.message); process.exit(1); });
  await p.goto("file://" + path.join(__dirname, "spot.html") + "?rendu"); await p.evaluate(() => document.fonts.ready); await p.waitForLoadState("networkidle");
  const { duree, nom } = await p.evaluate(() => ({ duree: window.DUREE, nom: window.NOM }));
  const sortie = path.join(__dirname, nom + ".mp4");
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(IPS), "-c:v", "mjpeg", "-i", "-", "-i", path.join(__dirname, "son.wav"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", String(duree / 1000), "-movflags", "+faststart", sortie], { stdio: ["pipe", "inherit", "inherit"] });
  const total = Math.round(duree / 1000 * IPS);
  for (let i = 0; i < total; i++) {
    await p.evaluate(ms => window.seek(ms), i * 1000 / IPS);
    const img = await p.screenshot({ type: "jpeg", quality: 94 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end(); await new Promise((ok, ko) => ff.on("close", c => c ? ko(new Error("ffmpeg " + c)) : ok()));
  console.log(sortie); await b.close();
})();
