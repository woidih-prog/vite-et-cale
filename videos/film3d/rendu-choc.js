// Rendu du film 3D : capture image par image (30 i/s) puis ffmpeg ajoute son4.wav.
const { chromium } = require("playwright"); const { spawn } = require("child_process"); const path = require("path");
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on("pageerror", e => { console.error(e.message); process.exit(1); });
  await p.goto("http://127.0.0.1:8777/pub3d-choc.html?rendu"); await p.waitForFunction(() => window.pret === true, { timeout: 60000 }); await p.waitForTimeout(2500);
  const { duree, nom } = await p.evaluate(() => ({ duree: window.DUREE, nom: window.NOM }));
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-", "-i", path.join(__dirname, "son4.wav"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", String(duree / 1000), "-movflags", "+faststart", path.join(__dirname, nom + ".mp4")], { stdio: ["pipe", "inherit", "inherit"] });
  const total = Math.round(duree / 1000 * 30);
  for (let i = 0; i < total; i++) {
    await p.evaluate(ms => window.seek(ms), i * 1000 / 30);
    const img = await p.screenshot({ type: "jpeg", quality: 94 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once("drain", r));
    if (i % 100 === 0) console.log(i, "/", total);
  }
  ff.stdin.end(); await new Promise((ok, ko) => ff.on("close", c => c ? ko(new Error("ffmpeg " + c)) : ok()));
  console.log("fini", nom); await b.close();
})();
