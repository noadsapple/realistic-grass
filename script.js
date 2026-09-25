(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const PHONE = "+17863299117";
  const ES = document.documentElement.lang === "es";
  // Asset URLs are resolved from this script's location so pages in
  // sub-folders (es/) load the same files.
  const BASE = (document.currentScript && document.currentScript.src) || location.href;
  const asset = (p) => new URL(p, BASE).href;

  // "Pause animations" button (WCAG 2.2.2): stops the wind, the van and the tiles
  let paused = false;
  try { paused = localStorage.getItem("rg-paused") === "1"; } catch (e) { /* storage blocked */ }
  const motionBtn = document.querySelector(".motion-toggle");
  const applyPause = () => {
    document.body.classList.toggle("paused", paused);
    if (!motionBtn) return;
    motionBtn.setAttribute("aria-pressed", String(paused));
    motionBtn.textContent = paused ? motionBtn.dataset.play : motionBtn.dataset.pause;
  };
  if (motionBtn) {
    if (reduceMotion) motionBtn.hidden = true;
    motionBtn.addEventListener("click", () => {
      paused = !paused;
      try { localStorage.setItem("rg-paused", paused ? "1" : "0"); } catch (e) { /* ignore */ }
      applyPause();
    });
  }
  applyPause();

  /* ------------------------------------------------------------------
   * 1. Turf background swaying in the wind (WebGL).
   *    The photo is tiled (mirrored) and displaced by a travelling "gust"
   *    noise field plus a fine per-blade flutter; gusts also brighten the
   *    turf a little, like light catching bent blades.
   *    If WebGL is unavailable the static CSS background stays visible.
   * ------------------------------------------------------------------ */
  const canvas = document.getElementById("turf");
  const gl = canvas.getContext("webgl", { antialias: false, alpha: false, powerPreference: "low-power" });

  if (gl) {
    const vs = `
      attribute vec2 a;
      void main() { gl_Position = vec4(a, 0.0, 1.0); }`;
    const fs = `
      precision mediump float;
      uniform sampler2D tex;
      uniform vec2 res;
      uniform float t;
      uniform float tile;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float noise(vec2 p) {
        vec2 i = floor(p), f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
                   mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
      }
      void main() {
        vec2 px = vec2(gl_FragCoord.x, res.y - gl_FragCoord.y);
        vec2 p = px / res.y;
        // Large gusts drifting left -> right (and slightly downwards)
        vec2 w = p * 2.2 - vec2(t * 0.32, t * 0.07);
        float g = noise(w) * 0.65 + noise(w * 2.3 + 3.1) * 0.35;
        g = smoothstep(0.2, 0.85, g);
        // Fine flutter of individual tufts
        float n = noise(px * 0.015 / (tile / 520.0));
        float flutter = sin(px.x * 0.05 + px.y * 0.03 + t * 5.0 + n * 6.2831);
        float scale = tile / 520.0;
        vec2 disp = vec2(1.0, 0.3) * (g * 7.0 + flutter * (0.6 + g * 1.2)) * scale;
        vec2 uv = (px - disp) / vec2(tile, tile * 2.0);
        vec3 c = texture2D(tex, uv).rgb;
        c *= 0.9 + g * 0.24;
        c = mix(c, c * vec3(1.04, 1.1, 0.92), g * 0.35);
        gl_FragColor = vec4(c, 1.0);
      }`;

    const compile = (type, src) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      return s;
    };

    try {
      const prog = gl.createProgram();
      gl.attachShader(prog, compile(gl.VERTEX_SHADER, vs));
      gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fs));
      gl.linkProgram(prog);
      gl.useProgram(prog);

      const buf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
      const loc = gl.getAttribLocation(prog, "a");
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

      const uRes = gl.getUniformLocation(prog, "res");
      const uT = gl.getUniformLocation(prog, "t");
      const uTile = gl.getUniformLocation(prog, "tile");

      let dpr = 1;
      const resize = () => {
        dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        canvas.width = Math.round(innerWidth * dpr);
        canvas.height = Math.round(innerHeight * dpr);
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.uniform2f(uRes, canvas.width, canvas.height);
        gl.uniform1f(uTile, (innerWidth < 600 ? 420 : 640) * dpr);
      };

      const img = new Image();
      img.onload = () => {
        const tex = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        resize();
        window.addEventListener("resize", resize);

        let clock = 0, prev = performance.now(), drawn = false;
        const frame = (now) => {
          if (!paused) clock += Math.min(0.1, (now - prev) / 1000);
          prev = now;
          if (!paused || !drawn) {
            gl.uniform1f(uT, clock);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            drawn = true;
          }
          if (!reduceMotion) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      };
      img.src = asset("assets/turf.jpg");
    } catch (e) {
      console.warn("Turf animation disabled:", e);
      canvas.style.display = "none";
    }
  } else {
    canvas.style.display = "none";
  }

  /* ------------------------------------------------------------------
   * 2. The Realistic Grass van drives clockwise around the window and
   *    lays a border of artificial-turf tiles behind it.
   *
   *    Van: its centre follows a rounded rectangle whose corner radius lets
   *    it turn in place while staying tight against every edge. It is
   *    rotated to its heading, so the front points down on the right-hand
   *    side and up on the left-hand side. Heading right/down uses the
   *    right-facing photo, heading left/up the left-facing one (so it is
   *    never upside-down), cross-fading in the two corners where they swap.
   *
   *    Turf border: a strip of square sod tiles along the window edges
   *    (the page is padded by the same width). Each tile drops out of the
   *    back of the van, tumbles and lands in its slot. Old tiles are rolled
   *    up just ahead of the van, so the border is always being re-laid.
   * ------------------------------------------------------------------ */
  const van = document.getElementById("van");
  const imgR = van.querySelector("img");
  const imgL = document.createElement("img");
  imgL.src = asset("assets/van-left.png");
  imgL.alt = "";
  van.appendChild(imgL);
  [imgR, imgL].forEach((im) => Object.assign(im.style, {
    position: "absolute", left: 0, top: "50%", transformOrigin: "50% 50%",
  }));

  const sod = document.createElement("canvas");
  sod.id = "sod";
  sod.setAttribute("aria-hidden", "true");
  document.body.appendChild(sod);
  const ctx = sod.getContext("2d");

  const RATIO = 0.5; // van photos are ~640 x 320
  let W, H, T, vw, vh, dpr, geo, border;

  const layout = () => {
    vw = document.documentElement.clientWidth;
    vh = innerHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = vw < 600 ? 104 : vw < 1000 ? 140 : 176;
    H = W * RATIO;
    T = vw < 600 ? 16 : 24; // turf border width
    document.documentElement.style.setProperty("--sod", T + "px");
    van.style.width = W + "px";
    van.style.height = H + "px";

    const M = 2;
    const r = (W - H) / 2;
    const x0 = M + W / 2, x1 = vw - M - W / 2;
    const y0 = M + W / 2, y1 = vh - M - W / 2;
    const lx = Math.max(0, x1 - x0), ly = Math.max(0, y1 - y0);
    const arc = (Math.PI / 2) * r;
    geo = { r, x0, x1, y0, y1, lx, ly, arc, total: 2 * lx + 2 * ly + 4 * arc };

    // Border slots run clockwise from the top-left corner, one tile each
    const bw = vw - T, bh = vh - T;
    const per = 2 * bw + 2 * bh;
    const n = Math.max(8, Math.round(per / T));
    border = { bw, bh, per, n, step: per / n, tiles: new Map(), last: null };

    sod.width = Math.round(vw * dpr);
    sod.height = Math.round(vh * dpr);
    sod.style.width = vw + "px";
    sod.style.height = vh + "px";
    buildSprites();
  };

  // Returns centre (x, y) and heading in degrees (0 = right, 90 = down)
  const pointAt = (s) => {
    const { r, x0, x1, y0, y1, lx, ly, arc } = geo;
    const segs = [
      [lx, (d) => [x0 + d, y0 - r, 0]],
      [arc, (d) => corner(x1, y0, -90, d / r)],
      [ly, (d) => [x1 + r, y0 + d, 90]],
      [arc, (d) => corner(x1, y1, 0, d / r)],
      [lx, (d) => [x1 - d, y1 + r, 180]],
      [arc, (d) => corner(x0, y1, 90, d / r)],
      [ly, (d) => [x0 - r, y1 - d, 270]],
      [arc, (d) => corner(x0, y0, 180, d / r)],
    ];
    for (const [len, fn] of segs) {
      if (s <= len) return fn(s);
      s -= len;
    }
    return segs[0][1](0);
  };
  // Point on a corner arc: centre (cx, cy), starting at polar angle a0 (deg), swept by rad
  const corner = (cx, cy, a0, rad) => {
    const a = (a0 * Math.PI) / 180 + rad;
    return [cx + geo.r * Math.cos(a), cy + geo.r * Math.sin(a), a0 + 90 + (rad * 180) / Math.PI];
  };

  // Clockwise distance along the border strip of the edge point nearest (x, y)
  const borderParam = (x, y) => {
    const { bw, bh } = border;
    const h = T / 2;
    const cx = Math.min(Math.max(x, h), vw - h), cy = Math.min(Math.max(y, h), vh - h);
    const d = [cy, vw - cx, vh - cy, cx];
    const e = d.indexOf(Math.min(...d));
    if (e === 0) return cx - h;
    if (e === 1) return bw + (cy - h);
    if (e === 2) return bw + bh + (vw - h - cx);
    return 2 * bw + bh + (vh - h - cy);
  };
  // Centre of border slot i
  const slotCenter = (i) => {
    const { bw, bh, step } = border;
    const h = T / 2;
    let d = (i + 0.5) * step;
    if (d < bw) return [h + d, h];
    d -= bw;
    if (d < bh) return [vw - h, h + d];
    d -= bh;
    if (d < bw) return [vw - h - d, vh - h];
    d -= bw;
    return [h, vh - h - d];
  };

  // A few sod-tile sprites cut from the turf photo. Laid tiles only show a
  // hairline seam; while a tile falls its brown latex backing shows as a
  // thickness under it, like a real sod square.
  const turfImg = new Image();
  turfImg.src = asset("assets/turf.jpg");
  let sprites = [];
  const buildSprites = () => {
    sprites = [];
    if (!turfImg.complete || !turfImg.naturalWidth) return;
    const px = Math.ceil(T * dpr);
    for (let k = 0; k < 6; k++) {
      const c = document.createElement("canvas");
      c.width = c.height = px;
      const g = c.getContext("2d");
      const src = 300; // source crop: keeps blades roughly the size of the page background
      const sx = Math.random() * (turfImg.naturalWidth - src);
      const sy = Math.random() * (turfImg.naturalHeight - src);
      g.drawImage(turfImg, sx, sy, src, src, 0, 0, px, px);
      const grad = g.createLinearGradient(0, 0, px, px);
      grad.addColorStop(0, "rgba(255,255,200,0.10)");
      grad.addColorStop(1, "rgba(0,0,0,0.12)");
      g.fillStyle = grad;
      g.fillRect(0, 0, px, px);
      g.strokeStyle = "rgba(0,0,0,0.22)";
      g.lineWidth = Math.max(1, dpr * 0.75);
      g.strokeRect(0, 0, px, px);
      sprites.push(c);
    }
  };
  turfImg.onload = buildSprites;

  const FALL = 560; // ms for a tile to drop from the van to its slot
  const smooth = (e0, e1, x) => {
    const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
    return t * t * (3 - 2 * t);
  };
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);

  const dropTile = (i, x, y, h, now) => {
    border.tiles.set(i, {
      born: now, fx: x, fy: y,
      spin: (Math.random() - 0.5) * 140 + h,
      sprite: (Math.random() * 6) | 0,
      gone: 0,
    });
  };

  const drawSod = (now, rearSlot) => {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, vw, vh);
    if (!sprites.length) return;
    const { n, tiles } = border;
    const clear = Math.ceil((W * 1.15) / border.step); // tiles rolled up ahead of the van
    for (const [i, t] of tiles) {
      const ahead = rearSlot === null ? n : (i - rearSlot + n) % n;
      if (!t.gone && ahead > 0 && ahead <= clear && now - t.born > FALL) t.gone = now;
      let k = 1, alpha = 1;
      if (t.gone) {
        k = 1 - Math.min(1, (now - t.gone) / 260);
        if (k <= 0) { tiles.delete(i); continue; }
        alpha = k;
      }
      const [sx, sy] = slotCenter(i);
      const p = Math.min(1, (now - t.born) / FALL);
      const e = easeOut(p);
      const x = t.fx + (sx - t.fx) * e;
      const y = t.fy + (sy - t.fy) * e;
      const lift = Math.sin(Math.PI * p) * 0.45;        // "height" while falling
      const squash = p >= 1 ? 1 : 1 + lift;
      const bounce = p < 1 ? 0 : Math.max(0, 1 - (now - t.born - FALL) / 140) * 0.08;
      const size = T * (squash - bounce) * k;
      const rot = (t.spin * (1 - e) * Math.PI) / 180;
      ctx.globalAlpha = alpha * Math.min(1, p * 4);
      if (lift > 0.02) {                                   // shadow under a falling tile
        ctx.fillStyle = "rgba(0,0,0,0.28)";
        ctx.fillRect(x - size / 2 + lift * 14, y - size / 2 + lift * 18, size, size);
      }
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(rot);
      if (lift > 0.02) {                                   // backing thickness while airborne
        ctx.fillStyle = "#4a3620";
        ctx.fillRect(-size / 2 + 1, -size / 2 + size * 0.14, size, size);
      }
      ctx.drawImage(sprites[t.sprite], -size / 2, -size / 2, size, size);
      ctx.restore();
    }
    ctx.globalAlpha = 1;
  };

  layout();
  window.addEventListener("resize", layout);

  if (reduceMotion) {
    // No animation: show the finished border straight away
    const fill = () => {
      buildSprites();
      for (let i = 0; i < border.n; i++) {
        const [x, y] = slotCenter(i);
        dropTile(i, x, y, 0, -1e6);
      }
      drawSod(0, null);
    };
    turfImg.complete ? fill() : turfImg.addEventListener("load", fill);
    window.addEventListener("resize", fill);
  }

  const SPEED = () => (innerWidth < 600 ? 90 : 150); // px per second
  let dist = geo.lx * 0.15, last = performance.now(), drivenOnce = false;
  const drive = (now) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    if (paused && !reduceMotion && drivenOnce) { requestAnimationFrame(drive); return; }
    drivenOnce = true;
    dist = (dist + SPEED() * dt) % geo.total;
    const [x, y, hRaw] = pointAt(dist);
    const h = ((hRaw % 360) + 360) % 360;
    // Weight of the left-facing photo: 0 when heading right/down, 1 when left/up
    let wL;
    if (h <= 90) wL = 0;
    else if (h <= 180) wL = smooth(100, 170, h);
    else if (h <= 270) wL = 1;
    else wL = 1 - smooth(280, 350, h);
    van.style.transform = `translate3d(${x - W / 2}px, ${y - H / 2}px, 0)`;
    imgR.style.transform = `translateY(-50%) rotate(${h}deg)`;
    imgL.style.transform = `translateY(-50%) rotate(${h - 180}deg)`;
    imgR.style.opacity = 1 - wL;
    imgL.style.opacity = wL;

    if (reduceMotion) return; // static border already drawn

    // Tiles drop from the back of the van into every slot it has passed
    const rad = (h * Math.PI) / 180;
    const rx = x - Math.cos(rad) * W * 0.42, ry = y - Math.sin(rad) * W * 0.42;
    const { n, step } = border;
    const rearSlot = Math.floor(borderParam(rx, ry) / step) % n;
    if (border.last === null) border.last = (rearSlot - 1 + n) % n;
    const gap = (rearSlot - border.last + n) % n;
    if (gap > 0 && gap < n / 4) {
      for (let k = 1; k <= gap; k++) dropTile((border.last + k) % n, rx, ry, h, now);
      border.last = rearSlot;
    } else if (gap >= n / 4) {
      border.last = rearSlot; // jumped (resize / tab switch): resync without a burst
    }
    drawSod(now, rearSlot);
    requestAnimationFrame(drive);
  };
  requestAnimationFrame(drive);
  if (!reduceMotion) van.classList.add("bump");

  /* ------------------------------------------------------------------
   * 3. Mobile menu, footer year, quote form (opens an SMS to the office)
   * ------------------------------------------------------------------ */
  const burger = document.querySelector(".burger");
  const links = document.querySelector(".nav-links");
  burger.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    burger.setAttribute("aria-expanded", open);
  });
  links.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      links.classList.remove("open");
      burger.setAttribute("aria-expanded", "false");
    }
  });

  document.getElementById("year").textContent = new Date().getFullYear();

  const form = document.getElementById("quote-form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const d = new FormData(form);
    const body = ES
      ? `Solicitud de estimado gratis – Realistic Grass\n` +
        `Nombre: ${d.get("name")}\nTeléfono: ${d.get("phone")}\n` +
        `Ciudad/Código postal: ${d.get("city") || "-"}\nProyecto: ${d.get("project")}\n` +
        `Área: ${d.get("area") || "-"} pies²\n${d.get("msg") || ""}`
      : `Free estimate request – Realistic Grass\n` +
        `Name: ${d.get("name")}\nPhone: ${d.get("phone")}\n` +
        `City/Zip: ${d.get("city") || "-"}\nProject: ${d.get("project")}\n` +
        `Area: ${d.get("area") || "-"} sq ft\n${d.get("msg") || ""}`;
    window.location.href = `sms:${PHONE}?&body=${encodeURIComponent(body)}`;
    let note = form.querySelector(".form-sent");
    if (!note) {
      note = document.createElement("p");
      note.className = "form-note form-sent";
      form.appendChild(note);
    }
    const call = '<a href="tel:' + PHONE + '" style="color:#ffd60a;font-weight:800">(786) 329-9117</a>';
    note.innerHTML = ES
      ? "Su aplicación de mensajes debería abrirse con su solicitud. Si no, llámenos al " + call + "."
      : "Your messaging app should open with your request. If not, call us at " + call + ".";
  });
})();
