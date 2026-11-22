/*
 * Realistic Grass — animated hero logo.
 * Progressive enhancement: the original <img> inside .hero-logo stays in the page (layout, SEO, alt text,
 * no-JS fallback). This script draws the animated version on a canvas laid over it, then hides the <img>.
 *
 * Effects: tuft swaying in a steady wind (silver ring stays fixed), a light sweep across the lettering,
 * a sun glint on the turf slab, and twinkling water drops.
 *
 * Respects: the site's "Pause animations" button (.motion-toggle, aria-pressed), prefers-reduced-motion,
 * tab visibility and scrolling off-screen (all stop the animation).
 */
(() => {
  'use strict';

  const host = document.querySelector('.hero-logo');
  const img = host && host.querySelector('img');
  if (!host || !img) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduce.matches) return;                       // keep the static image

  const script = document.currentScript;
  const BASE = script && script.src ? script.src.replace(/[^\/]*$/, '') : 'assets/';

  // artwork space is 960 x 960; the visible crop matches the original logo's proportions
  const S = 960, OX = 48, OY = 72, CW = 866, CH = 807;

  const load = (name) => new Promise((res, rej) => {
    const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = BASE + name;
  });
  Promise.all([
    load('logo-anim.webp'), load('logo-anim-text.png'), load('logo-anim-ring.png'), load('logo-anim-holes.png'),
  ]).then(start).catch(() => { /* any failure: the original image simply stays */ });

  function start([logo, textMask, ringMask, holes]) {
    const mk = (w = S, h = S) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

    // ---- visible canvas, laid over the original <img> ----
    const cv = mk(CW, CH), ctx = cv.getContext('2d');
    cv.setAttribute('aria-hidden', 'true');
    cv.style.cssText = 'position:absolute;pointer-events:none;opacity:0;transition:opacity .4s ease;';
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    const f = getComputedStyle(img).filter;
    if (f && f !== 'none') cv.style.filter = f;     // keep an existing drop-shadow
    host.appendChild(cv);

    function place() {
      const r = img.getBoundingClientRect(), h = host.getBoundingClientRect();
      cv.style.left = (r.left - h.left - host.clientLeft) + 'px';
      cv.style.top = (r.top - h.top - host.clientTop) + 'px';
      cv.style.width = r.width + 'px';
      cv.style.height = r.height + 'px';
    }

    // ---- working canvases (artwork space) ----
    const F = mk(), fx = F.getContext('2d');        // composed frame
    const acc = mk(), actx = acc.getContext('2d');  // swaying tuft accumulator
    const tmp = mk(), tctx = tmp.getContext('2d');  // one sway window
    const shn = mk(), sctx = shn.getContext('2d');  // light sweep

    // swaying source = logo with ring / halo cut out (the ring is redrawn fixed on top)
    const srcC = mk(), sc = srcC.getContext('2d');
    sc.drawImage(logo, 0, 0);
    sc.globalCompositeOperation = 'destination-out'; sc.drawImage(holes, 0, 0);
    const ringL = mk(), rc = ringL.getContext('2d');
    rc.drawImage(logo, 0, 0);
    rc.globalCompositeOperation = 'destination-in'; rc.drawImage(ringMask, 0, 0);

    // soft mask: only the foreground tuft may sway
    const M = mk(), mc = M.getContext('2d');
    let g = mc.createLinearGradient(0, 640, 0, 678);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, '#000');
    mc.fillStyle = g; mc.fillRect(0, 640, S, S - 640);
    const zone = (x0, y0, x1, y1, fadeRight) => {
      const t = mk(), k = t.getContext('2d');
      k.fillStyle = '#000'; k.fillRect(x0, y0, x1 - x0, y1 - y0);
      k.globalCompositeOperation = 'destination-out';
      const edge = (xa, ya, xb, yb, r) => {
        const gg = k.createLinearGradient(xa, ya, xb, yb);
        gg.addColorStop(0, 'rgba(0,0,0,0)'); gg.addColorStop(1, '#000');
        k.fillStyle = gg; k.fillRect(r[0], r[1], r[2], r[3]);
      };
      edge(0, y0 + 34, 0, y0, [x0, y0, x1 - x0, 34]);
      if (fadeRight) edge(x1 - 40, 0, x1, 0, [x1 - 40, y0, 40, y1 - y0]);
      else edge(x0 + 40, 0, x0, 0, [x0, y0, 40, y1 - y0]);
      mc.drawImage(t, 0, 0);
    };
    zone(0, 560, 262, 720, true);
    zone(698, 560, S, 720, false);

    // 21 overlapping vertical windows, each at its own wind phase (alphas sum to the mask: no tearing)
    const K = 21, SPAN = S / (K - 1), wins = [];
    for (let k = 0; k < K; k++) {
      const cx = k * SPAN, w = mk(), c = w.getContext('2d');
      c.drawImage(M, 0, 0);
      c.globalCompositeOperation = 'destination-in';
      const gg = c.createLinearGradient(cx - SPAN, 0, cx + SPAN, 0);
      gg.addColorStop(0, 'rgba(0,0,0,0)'); gg.addColorStop(.5, '#000'); gg.addColorStop(1, 'rgba(0,0,0,0)');
      c.fillStyle = gg; c.fillRect(0, 0, S, S);
      wins.push({ cx, w });
    }

    // ---- tuning ----
    const Y_TOP = 570, Y_BASE = 840, AMP = 24, LEAN = 0.75, STEP = 3;
    const KX = 2 * Math.PI / 820, WIND = 3.9;        // wavelength ~820 px, ~1.6 s per cycle, left to right

    const STAR = new Path2D('M0,-1 Q.09,-.09 1,0 Q.09,.09 0,1 Q-.09,.09 -1,0 Q-.09,-.09 0,-1Z');
    const DROPS = [ // x, y, size, delay, period
      [240, 720, 13, .3, 4.6], [308, 750, 12, 1.9, 5.1], [407, 723, 13, 3.1, 4.3], [426, 788, 15, .9, 5.4],
      [605, 786, 12, 2.4, 4.8], [682, 738, 12, 3.7, 4.4], [743, 632, 11, 1.3, 5.0],
    ];
    const ease = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };

    function sway(t) {
      actx.globalCompositeOperation = 'source-over'; actx.clearRect(0, 0, S, S);
      for (let k = 0; k < K; k++) {
        const { cx, w } = wins[k];
        const sx = Math.max(0, Math.floor(cx - SPAN - 4));
        const sw = Math.min(S, Math.ceil(cx + SPAN + 4)) - sx;
        const ph = -cx * KX;
        tctx.globalCompositeOperation = 'source-over'; tctx.clearRect(sx, 560, sw, 310);
        for (let y = 560; y < 860; y += STEP) {
          const u = Math.min(1, Math.max(0, (Y_BASE - y) / (Y_BASE - Y_TOP)));
          if (u <= 0) continue;
          const a = t * WIND + ph + y * 0.009;
          const dx = AMP * Math.pow(u, 1.35) * (LEAN + Math.sin(a) + 0.3 * Math.sin(2 * a + 0.8));
          tctx.drawImage(srcC, sx, y, sw, STEP, sx + dx, y, sw, STEP);
        }
        tctx.globalCompositeOperation = 'destination-in';
        tctx.drawImage(w, sx, 560, sw, 310, sx, 560, sw, 310);
        actx.globalCompositeOperation = 'lighter';
        actx.drawImage(tmp, sx, 560, sw, 310, sx, 560, sw, 310);
      }
      fx.drawImage(acc, 0, 0);
      fx.drawImage(ringL, 0, 0);                     // silver ring stays put, in front of the moving tuft
    }

    function shine(t) {                              // 1.5 s sweep every 7 s, first one at 1.6 s
      const u = (((t - 1.6) % 7) + 7) % 7 / 1.5;
      if (t < 1.6 || u > 1) return;
      const bx = -220 + 1400 * ease(u);
      sctx.setTransform(1, 0, 0, 1, 0, 0);
      sctx.globalCompositeOperation = 'source-over'; sctx.clearRect(0, 0, S, S);
      sctx.setTransform(1, 0, -0.27, 1, 0.27 * 480, 0);
      const gr = sctx.createLinearGradient(bx - 190, 0, bx + 190, 0);
      gr.addColorStop(0, 'rgba(96,176,24,0)'); gr.addColorStop(.30, 'rgba(96,176,24,.30)');
      gr.addColorStop(.50, 'rgba(255,255,226,.96)'); gr.addColorStop(.70, 'rgba(96,176,24,0)');
      gr.addColorStop(1, 'rgba(96,176,24,0)');
      sctx.fillStyle = gr; sctx.fillRect(bx - 190, 0, 380, S);
      sctx.setTransform(1, 0, 0, 1, 0, 0);
      sctx.globalCompositeOperation = 'destination-in'; sctx.drawImage(textMask, 0, 0);
      fx.drawImage(shn, 0, 0);
    }

    function sparkles(t) {
      // sun glint on the turf slab
      const s = 0.5 - 0.5 * Math.cos(2 * Math.PI * t / 3.8);
      fx.save(); fx.translate(238, 168);
      const rg = fx.createRadialGradient(0, 0, 0, 0, 0, 46 * (0.7 + 0.45 * s));
      rg.addColorStop(0, `rgba(255,251,208,${0.35 + 0.4 * s})`); rg.addColorStop(.45, `rgba(244,236,122,${0.12 + 0.2 * s})`);
      rg.addColorStop(1, 'rgba(244,236,122,0)');
      fx.fillStyle = rg; fx.beginPath(); fx.arc(0, 0, 46 * (0.7 + 0.45 * s), 0, 7); fx.fill();
      fx.rotate(18 * s * Math.PI / 180); fx.scale(40 * (0.55 + 0.57 * s), 40 * (0.55 + 0.57 * s));
      fx.globalAlpha = 0.55 + 0.45 * s; fx.fillStyle = '#fffef0'; fx.fill(STAR);
      fx.restore();
      // water drops
      for (const [x, y, r, d, p] of DROPS) {
        const ph = (((t - d) % p) + p) % p / p;
        let e = 0;
        if (ph >= .62 && ph < .76) e = (ph - .62) / .14; else if (ph >= .76 && ph < .90) e = 1 - (ph - .76) / .14;
        if (e <= 0) continue;
        fx.save(); fx.translate(x, y); fx.rotate(ph * Math.PI * 2 * .25 + .6);
        const k = r * (0.2 + 0.8 * e); fx.scale(k, k);
        fx.globalAlpha = e; fx.fillStyle = '#fff'; fx.fill(STAR);
        fx.restore();
      }
    }

    function draw(t, animated) {
      fx.clearRect(0, 0, S, S);
      fx.drawImage(logo, 0, 0);
      if (animated) { sway(t); shine(t); sparkles(t); }
      ctx.clearRect(0, 0, CW, CH);
      ctx.drawImage(F, OX, OY, CW, CH, 0, 0, CW, CH);
    }

    // ---- run control ----
    const toggles = [...document.querySelectorAll('.motion-toggle')];
    let inView = true, raf = 0, t = 0, last = 0, shown = false;
    const paused = () => toggles.some((b) => b.getAttribute('aria-pressed') === 'true') || reduce.matches;
    const running = () => !paused() && inView && !document.hidden;

    function reveal() { if (!shown) { shown = true; cv.style.opacity = '1'; img.style.opacity = '0'; } }
    function frame(now) {
      raf = 0;
      if (!running()) return;
      t += Math.min(0.05, (now - last) / 1000); last = now;
      place(); draw(t, true); reveal();
      raf = requestAnimationFrame(frame);
    }
    function sync() {
      if (running()) { if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); } }
      else { if (raf) { cancelAnimationFrame(raf); raf = 0; } place(); draw(0, false); reveal(); }
    }

    toggles.forEach((b) => new MutationObserver(sync).observe(b, { attributes: true, attributeFilter: ['aria-pressed'] }));
    toggles.forEach((b) => b.addEventListener('click', () => setTimeout(sync, 0)));
    document.addEventListener('visibilitychange', sync);
    addEventListener('resize', () => { place(); if (!running()) draw(0, false); });
    if (reduce.addEventListener) reduce.addEventListener('change', sync);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((e) => { inView = e[0].isIntersecting; sync(); }).observe(host);
    }
    sync();
  }
})();
