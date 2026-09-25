// Render social/reel.html to MP4 (1080x1920, 30 fps, H.264) for TikTok / Instagram / Facebook Reels.
// Usage (from the repo root):  npm i playwright && python3 -m http.server 8799 &
//   node social/render-reel.mjs en   → social/realistic-grass-reel-en.mp4   (same with "es")
// Needs an ffmpeg with libx264 on PATH, or FFMPEG=/path/to/ffmpeg.
import { chromium } from "playwright";
import { spawn } from "node:child_process";

const lang = process.argv[2] === "es" ? "es" : "en";
const FPS = 30;
const ffmpeg = process.env.FFMPEG || "ffmpeg";
const out = `social/realistic-grass-reel-${lang}.mp4`;
const url = `${process.env.BASE || "http://localhost:8799"}/social/reel.html?lang=${lang}`;

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.error("page error:", e.message));
await page.goto(url);
await page.evaluate(() => window.READY);
const duration = await page.evaluate(() => window.DURATION);

const enc = spawn(ffmpeg, [
  "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
  // silent AAC track: some apps handle videos without audio badly; add music in the app
  "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
  "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p",
  "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out,
], { stdio: ["pipe", "inherit", "inherit"] });

const frames = Math.round(duration * FPS);
for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.render(t), f / FPS);
  const jpg = await page.screenshot({ type: "jpeg", quality: 92 });
  if (!enc.stdin.write(jpg)) await new Promise((r) => enc.stdin.once("drain", r));
  if (f % 90 === 0) console.log(`${lang}: frame ${f}/${frames}`);
}
enc.stdin.end();
await new Promise((r) => enc.on("close", r));
await browser.close();
console.log("wrote", out);
