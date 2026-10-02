// Render social/reel.html to MP4 (30 fps, H.264 + AAC) with the voice-over/music track.
//   node social/render-reel.mjs <en|es> [vertical|square]
//   → social/realistic-grass-<format>-<lang>.mp4   (vertical 1080x1920, square 1080x1080)
// Prerequisites (from the repo root):
//   python3 social/make-audio.py en es      (writes audio-<lang>.wav + timing-<lang>.json)
//   npm i playwright && python3 -m http.server 8799 &
// Needs an ffmpeg with libx264 on PATH, or FFMPEG=/path/to/ffmpeg.
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const lang = process.argv[2] === "es" ? "es" : "en";
const format = process.argv[3] === "square" ? "square" : "vertical";
const FPS = 30;
const ffmpeg = process.env.FFMPEG || "ffmpeg";
const out = `social/realistic-grass-${format}-${lang}.mp4`;
const url = `${process.env.BASE || "http://localhost:8799"}/social/reel.html?lang=${lang}&format=${format}`;
const timingFile = `social/timing-${lang}.json`;
const audioFile = `social/audio-${lang}.wav`;

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
const size = format === "square" ? { width: 1080, height: 1080 } : { width: 1080, height: 1920 };
const page = await browser.newPage({ viewport: size, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.error("page error:", e.message));
await page.goto(url);
await page.evaluate(() => window.READY);
if (existsSync(timingFile)) await page.evaluate((t) => window.setTiming(t), JSON.parse(readFileSync(timingFile, "utf8")));
const duration = await page.evaluate(() => window.DURATION);

const audio = existsSync(audioFile)
  ? ["-i", audioFile]
  : ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"];
const enc = spawn(ffmpeg, [
  "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
  ...audio, "-map", "0:v", "-map", "1:a", "-t", String(duration),
  "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out,
], { stdio: ["pipe", "inherit", "inherit"] });

const frames = Math.round(duration * FPS);
for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.render(t), f / FPS);
  const jpg = await page.screenshot({ type: "jpeg", quality: 92 });
  if (!enc.stdin.write(jpg)) await new Promise((r) => enc.stdin.once("drain", r));
  if (f % 150 === 0) console.log(`${format}/${lang}: frame ${f}/${frames}`);
}
enc.stdin.end();
await new Promise((r) => enc.on("close", r));
await browser.close();
console.log("wrote", out);
