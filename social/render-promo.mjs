// Square promo: lawn footage + transparent marketing overlay (social/promo.html) + voice-over/music.
//   node social/render-promo.mjs <en|es> <background.mp4> [square|vertical|landscape] [name]
//   → social/<name>-<format>-<lang>.mp4 (default name realistic-grass-promo; 1080x1080, 1080x1920 or
//     1920x1080, 30 fps, H.264 + AAC)
// The background must already last timing-<lang>.json "duration" seconds (the lawn montage,
// cropped square and time-stretched to the voice-over). Needs playwright, ffmpeg (FFMPEG=…) and
// a static server on the repo root (BASE, default http://localhost:8799).
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";

const lang = process.argv[2] === "es" ? "es" : "en";
const bg = process.argv[3];
const format = ["vertical", "landscape"].includes(process.argv[4]) ? process.argv[4] : "square";
const name = process.argv[5] || "realistic-grass-promo";
const WIDTH = format === "landscape" ? 1920 : 1080, HEIGHT = format === "vertical" ? 1920 : 1080;
const FPS = 30;
const ffmpeg = process.env.FFMPEG || "ffmpeg";
const out = `social/${name}-${format}-${lang}.mp4`;
const T = JSON.parse(readFileSync(`social/timing-${lang}.json`, "utf8"));

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
page.on("pageerror", (e) => console.error("page error:", e.message));
await page.goto(`${process.env.BASE || "http://localhost:8799"}/social/promo.html?lang=${lang}&format=${format}`);
await page.evaluate(() => window.READY);
await page.evaluate((t) => window.setTiming(t), T);

const enc = spawn(ffmpeg, [
  "-y", "-loglevel", "error",
  "-i", bg,                                                        // 0: footage
  "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",   // 1: overlay frames (RGBA)
  "-i", `social/audio-${lang}.wav`,                                // 2: voice-over + music
  "-filter_complex", "[0:v]fps=30,format=yuv420p[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
  "-map", "[v]", "-map", "2:a", "-t", String(T.duration),
  "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high", "-level", "4.1",
  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out,
], { stdio: ["pipe", "inherit", "inherit"] });

const frames = Math.round(T.duration * FPS);
for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.render(t), f / FPS);
  const png = await page.screenshot({ type: "png", omitBackground: true });
  if (!enc.stdin.write(png)) await new Promise((r) => enc.stdin.once("drain", r));
  if (f % 150 === 0) console.log(`promo/${lang}: frame ${f}/${frames}`);
}
enc.stdin.end();
await new Promise((r) => enc.on("close", r));
await browser.close();
console.log("wrote", out);
