/* Labs — small 2D interactives a lesson places with :::lab <name>. Each mounts into a .labbox. */
window.Labs = (function () {
  const D2R = Math.PI / 180, TAU = Math.PI * 2;
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const fmt = (x, d = 1) => (Math.abs(x) < 5e-10 ? 0 : x).toLocaleString('en-GB', { minimumFractionDigits: d, maximumFractionDigits: d });
  function fit(c, h) {
    const r = c.getBoundingClientRect(), dpr = window.devicePixelRatio || 1, w = Math.max(240, r.width);
    c.style.height = h + 'px'; c.width = w * dpr; c.height = h * dpr; const g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); return { g, w, h };
  }
  function arrow(g, x0, y0, x1, y1, col, w) {
    g.strokeStyle = col; g.fillStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    const a = Math.atan2(y1 - y0, x1 - x0), L = Math.hypot(x1 - x0, y1 - y0); if (L < 4) return; const hh = Math.min(10, L * 0.4);
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - hh * Math.cos(a - 0.4), y1 - hh * Math.sin(a - 0.4)); g.lineTo(x1 - hh * Math.cos(a + 0.4), y1 - hh * Math.sin(a + 0.4)); g.closePath(); g.fill();
  }
  const readout = rows => rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('');
  const slider = (id, label, min, max, step, val) => `<div><label for="${id}">${label} <output id="${id}-o"></output></label><input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${val}"></div>`;

  function clarke(box) {
    box.insertAdjacentHTML('beforeend', `
      <div class="seg" role="group" aria-label="Mode"><button type="button" id="cl-sine" aria-pressed="true">Balanced sines</button><button type="button" id="cl-free" aria-pressed="false">Free values</button><button type="button" id="cl-play">Animate ωt</button></div>
      <div class="ctl" id="cl-c-sine">${slider('cl-wt', 'Instant ωt', 0, 360, 1, 30)}${slider('cl-amp', 'Peak current', 10, 120, 1, 100)}</div>
      <div class="ctl" id="cl-c-free" hidden>${slider('cl-u', 'iU', -120, 120, 1, 100)}${slider('cl-v', 'iV', -120, 120, 1, -100)}</div>
      <div class="pair"><canvas id="cl-wave"></canvas><canvas id="cl-vec"></canvas></div>
      <dl class="readout" id="cl-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    let mode = 'sine', playing = false;
    function I() {
      if (mode === 'sine') { const wt = +$('cl-wt').value * D2R, A = +$('cl-amp').value; return [A * Math.cos(wt), A * Math.cos(wt - 120 * D2R), A * Math.cos(wt - 240 * D2R)]; }
      const u = +$('cl-u').value, v = +$('cl-v').value; return [u, v, -u - v];
    }
    function draw() {
      const [iu, iv, iw] = I();
      $('cl-wt-o').textContent = $('cl-wt').value + '°'; $('cl-amp-o').textContent = $('cl-amp').value + ' A';
      $('cl-u-o').textContent = $('cl-u').value + ' A'; $('cl-v-o').textContent = $('cl-v').value + ' A';
      const ia = (2 / 3) * (iu - 0.5 * iv - 0.5 * iw), ib = (iv - iw) / Math.sqrt(3);
      const cU = css('--u'), cV = css('--v'), cW = css('--w'), ink = css('--ink'), mut = css('--muted'), line = css('--line'), acc = css('--accent');
      const A = mode === 'sine' ? +$('cl-amp').value : 120;
      { const { g, w, h } = fit($('cl-wave'), 220); g.clearRect(0, 0, w, h); const L = 42, R = 10, T = 12, B = h - 24;
        const X = d => L + (w - L - R) * d / 360, Y = v => T + (B - T) * (1 - (v / A + 1) / 2);
        g.strokeStyle = line; g.lineWidth = 1; g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - R, Y(0)); g.stroke();
        g.font = '12px IBM Plex Mono, monospace'; g.fillStyle = mut; g.textAlign = 'right'; g.fillText('+' + A, L - 4, T + 8); g.fillText('0', L - 4, Y(0) + 4); g.fillText('−' + A, L - 4, B);
        g.textAlign = 'center'; [0, 90, 180, 270, 360].forEach(d => g.fillText(d + '°', X(d), h - 6));
        if (mode === 'sine') {
          [[0, cU], [120, cV], [240, cW]].forEach(([ph, cc]) => { g.strokeStyle = cc; g.lineWidth = 2.2; g.beginPath(); for (let d = 0; d <= 360; d += 3) { const y = Y(A * Math.cos((d - ph) * D2R)); d ? g.lineTo(X(d), y) : g.moveTo(X(d), y); } g.stroke(); });
          const d = +$('cl-wt').value; g.strokeStyle = ink; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(X(d), T); g.lineTo(X(d), B); g.stroke(); g.setLineDash([]);
          [[iu, cU], [iv, cV], [iw, cW]].forEach(([v, cc]) => { g.fillStyle = cc; g.beginPath(); g.arc(X(d), Y(v), 4.5, 0, TAU); g.fill(); });
        } else {
          const bw = (w - L - R) / 5; [[iu, cU, 'iU'], [iv, cV, 'iV'], [iw, cW, 'iW']].forEach(([v, cc, n], k) => { const x = L + bw * (0.6 + 1.5 * k); g.fillStyle = cc; g.fillRect(x, Math.min(Y(0), Y(v)), bw * 0.8, Math.abs(Y(v) - Y(0))); g.fillStyle = mut; g.textAlign = 'center'; g.fillText(n + ' = ' + fmt(v, 0), x + bw * 0.4, T + 10); });
        } }
      { const { g, w, h } = fit($('cl-vec'), 220); g.clearRect(0, 0, w, h); const cx = w / 2, cy = h / 2, Rr = Math.min(w, h) / 2 - 26, sc = Rr / (A * 1.05);
        g.font = '12px IBM Plex Mono, monospace'; g.textAlign = 'center';
        [[0, cU, 'U = α'], [120, cV, 'V'], [240, cW, 'W']].forEach(([a, cc, n]) => { const x = cx + Rr * Math.cos(a * D2R), y = cy - Rr * Math.sin(a * D2R); g.strokeStyle = line; g.lineWidth = 1; g.beginPath(); g.moveTo(2 * cx - x, 2 * cy - y); g.lineTo(x, y); g.stroke(); g.fillStyle = cc; g.fillText(n, cx + (Rr + 14) * Math.cos(a * D2R), cy - (Rr + 14) * Math.sin(a * D2R) + 4); });
        g.strokeStyle = line; g.setLineDash([2, 4]); g.beginPath(); g.moveTo(cx, cy + Rr); g.lineTo(cx, cy - Rr); g.stroke(); g.setLineDash([]); g.fillStyle = mut; g.fillText('β', cx + 10, cy - Rr + 4);
        let x = cx, y = cy; [[iu, 0, cU], [iv, 120, cV], [iw, 240, cW]].forEach(([v, a, cc]) => { const dx = (2 / 3) * v * sc * Math.cos(a * D2R), dy = -(2 / 3) * v * sc * Math.sin(a * D2R); arrow(g, x, y, x + dx, y + dy, cc, 2.5); x += dx; y += dy; });
        arrow(g, cx, cy, cx + ia * sc, cy - ib * sc, acc, 4); }
      const mag = Math.hypot(ia, ib), ang = (Math.atan2(ib, ia) / D2R + 360) % 360;
      $('cl-r').innerHTML = readout([['iU', fmt(iu) + ' A'], ['iV', fmt(iv) + ' A'], ['iW', fmt(iw) + ' A'], ['Sum', fmt(iu + iv + iw) + ' A'], ['iα', fmt(ia) + ' A'], ['iβ', fmt(ib) + ' A'], ['Length', fmt(mag) + ' A'], ['Angle', mag > 0.5 ? fmt(ang, 0) + '°' : '—']]);
    }
    ['cl-wt', 'cl-amp', 'cl-u', 'cl-v'].forEach(id => $(id).addEventListener('input', draw));
    const pressMode = m => { mode = m; $('cl-sine').setAttribute('aria-pressed', String(m === 'sine')); $('cl-free').setAttribute('aria-pressed', String(m === 'free')); $('cl-c-sine').hidden = m !== 'sine'; $('cl-c-free').hidden = m !== 'free'; $('cl-play').hidden = m !== 'sine'; if (m !== 'sine') playing = false; draw(); };
    $('cl-sine').onclick = () => pressMode('sine'); $('cl-free').onclick = () => pressMode('free');
    $('cl-play').onclick = () => { playing = !playing; $('cl-play').textContent = playing ? 'Stop' : 'Animate ωt'; if (playing) tick(); };
    function tick() { if (!playing) return; const s = $('cl-wt'); s.value = (+s.value + 2) % 361; draw(); setTimeout(() => requestAnimationFrame(tick), 30); }
    new ResizeObserver(draw).observe(box); draw();
    return draw;
  }

  function hexagon(box) {
    const Vdc = 52;
    box.insertAdjacentHTML('beforeend', `<div class="ctl">${slider('hx-m', 'Phase voltage asked (peak)', 0, 36, 0.5, 26)}${slider('hx-a', 'Angle', 0, 360, 1, 20)}</div><canvas id="hx-c"></canvas><dl class="readout" id="hx-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    function draw() {
      const m = +$('hx-m').value, a = +$('hx-a').value; $('hx-m-o').textContent = fmt(m) + ' V'; $('hx-a-o').textContent = a + '°';
      const { g, w, h } = fit($('hx-c'), 320); g.clearRect(0, 0, w, h); const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 34, Vv = 2 / 3 * Vdc, sc = R / Vv;
      const ink = css('--ink'), mut = css('--muted'), acc = css('--accent'), bad = css('--bad'), cw = css('--w');
      const names = ['100', '110', '010', '011', '001', '101'];
      g.strokeStyle = ink; g.lineWidth = 1.5; g.beginPath(); for (let k = 0; k <= 6; k++) { const x = cx + R * Math.cos(k * 60 * D2R), y = cy - R * Math.sin(k * 60 * D2R); k ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
      g.font = '12px IBM Plex Mono, monospace'; g.textAlign = 'center';
      for (let k = 0; k < 6; k++) { const x = cx + R * Math.cos(k * 60 * D2R), y = cy - R * Math.sin(k * 60 * D2R); arrow(g, cx, cy, x, y, mut, 1.2); g.fillStyle = mut; g.fillText('V' + (k + 1) + ' ' + names[k], cx + (R + 20) * Math.cos(k * 60 * D2R), cy - (R + 20) * Math.sin(k * 60 * D2R) + 4); }
      const r1 = Vdc / Math.sqrt(3) * sc, r2 = Vdc / 2 * sc;
      g.strokeStyle = acc; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r1, 0, TAU); g.stroke();
      g.strokeStyle = cw; g.setLineDash([5, 4]); g.beginPath(); g.arc(cx, cy, r2, 0, TAU); g.stroke(); g.setLineDash([]);
      const sector = Math.floor(((a % 360) + 360) % 360 / 60), th = (a - sector * 60) * D2R;
      const T1 = m * Math.sin(60 * D2R - th) / (Vv * Math.sin(60 * D2R)), T2 = m * Math.sin(th) / (Vv * Math.sin(60 * D2R)), T0 = 1 - T1 - T2, ok = T0 >= -1e-9;
      arrow(g, cx, cy, cx + m * sc * Math.cos(a * D2R), cy - m * sc * Math.sin(a * D2R), ok ? ink : bad, 3);
      $('hx-r').innerHTML = readout([['SVPWM circle', fmt(Vdc / Math.sqrt(3)) + ' V'], ['Sine-PWM circle', fmt(Vdc / 2) + ' V'], ['Sector', `V${sector + 1} → V${(sector + 1) % 6 + 1}`], ['Time in V' + (sector + 1), fmt(Math.max(0, T1) * 100, 0) + ' %'], ['Time in V' + ((sector + 1) % 6 + 1), fmt(Math.max(0, T2) * 100, 0) + ' %'], ['Zero vectors', ok ? fmt(T0 * 100, 0) + ' %' : 'out of reach']]);
    }
    ['hx-m', 'hx-a'].forEach(id => $(id).addEventListener('input', draw));
    new ResizeObserver(draw).observe(box); draw();
    return draw;
  }

  // ---- Pol's motor and VESC (04_model/params/motor_params.m) ----
  const M = { Rs: 0.02802, Ld: 99e-6, Lq: 113e-6, lam: 0.016855, p: 3, Vpk: 30, Imax: 120, Ts: 1 / 30e3, vescKp: 0.2119, vescKi: 56.20 };
  const torque = (id, iq) => 1.5 * M.p * (M.lam + (M.Ld - M.Lq) * id) * iq;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const FONT = '12px IBM Plex Mono, monospace';
  function nice(span, n) { const raw = span / n, e = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / e; return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * e; }
  // time plot frame: returns mappers; draws grid, zero line and tick labels
  function frame(g, w, h, x1, y0, y1, xl, yl) {
    const L = 46, R = 10, T = 12, B = h - 26, mut = css('--muted'), line = css('--line');
    const X = x => L + (w - L - R) * x / x1, Y = v => B - (B - T) * (v - y0) / (y1 - y0);
    g.font = FONT; g.lineWidth = 1; g.strokeStyle = line; g.fillStyle = mut;
    const sx = nice(x1, 5), sy = nice(y1 - y0, 4);
    g.textAlign = 'center'; for (let x = 0; x <= x1 + 1e-9; x += sx) { g.beginPath(); g.moveTo(X(x), T); g.lineTo(X(x), B); g.stroke(); g.fillText(fmt(x, sx < 1 ? 1 : 0), X(x), h - 10); }
    g.textAlign = 'right'; for (let v = Math.ceil(y0 / sy) * sy; v <= y1 + 1e-9; v += sy) { g.beginPath(); g.moveTo(L, Y(v)); g.lineTo(w - R, Y(v)); g.stroke(); g.fillText(fmt(v, sy < 1 ? 1 : 0), L - 4, Y(v) + 4); }
    if (y0 < 0 && y1 > 0) { g.strokeStyle = mut; g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - R, Y(0)); g.stroke(); }
    g.textAlign = 'right'; g.fillText(xl, w - R - 2, T + 10); g.textAlign = 'left'; g.fillText(yl, L + 4, T + 10);
    return { X, Y, L, R, T, B };
  }
  function trace(g, xs, ys, X, Y, col, wd, dash) { g.strokeStyle = col; g.lineWidth = wd; g.setLineDash(dash || []); g.beginPath(); xs.forEach((x, k) => k ? g.lineTo(X(x), Y(ys[k])) : g.moveTo(X(x), Y(ys[k]))); g.stroke(); g.setLineDash([]); }
  function hline(g, fr, w, y, col, label, dash) { const { Y, L, R } = fr; g.strokeStyle = col; g.lineWidth = 1.5; g.setLineDash(dash || [6, 4]); g.beginPath(); g.moveTo(L, Y(y)); g.lineTo(w - R, Y(y)); g.stroke(); g.setLineDash([]); if (label) { g.fillStyle = col; g.textAlign = 'right'; g.font = FONT; g.fillText(label, w - R - 4, Y(y) - 5); } }
  const out = (box, id, txt) => { box.querySelector('#' + id + '-o').textContent = txt; };

  // ---- park: abc → αβ → dq. In the rotor's frame the currents are flat numbers. ----
  function park(box) {
    box.insertAdjacentHTML('beforeend', `
      <div class="seg" role="group" aria-label="Animation"><button type="button" id="pk-play" aria-pressed="${!reduceMotion}">Run</button><button type="button" id="pk-e0">Angle error to 0</button></div>
      <div class="ctl">${slider('pk-d', 'id, along the magnet', -120, 120, 1, 0)}${slider('pk-q', 'iq, 90° ahead', -120, 120, 1, 80)}${slider('pk-s', 'Electrical speed (slowed)', 0, 1.5, 0.05, 0.25)}${slider('pk-e', 'Angle error of the encoder', -90, 90, 1, 0)}</div>
      <div class="pair"><canvas id="pk-wave"></canvas><canvas id="pk-vec"></canvas></div>
      <p class="legend"><span><i style="background:var(--u)"></i>ia</span><span><i style="background:var(--v)"></i>ib</span><span><i style="background:var(--w)"></i>ic</span><span><i style="background:var(--magN)"></i>d axis, id</span><span><i style="background:var(--copper)"></i>q axis, iq</span><span>dashed = what the controller measures with the angle error</span></p>
      <dl class="readout" id="pk-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    let th = 30 * D2R, playing = !reduceMotion, last = 0;
    function draw() {
      const id = +$('pk-d').value, iq = +$('pk-q').value, e = +$('pk-e').value * D2R;
      out(box, 'pk-d', id + ' A'); out(box, 'pk-q', iq + ' A'); out(box, 'pk-s', fmt(+$('pk-s').value, 2) + ' cycles/s'); out(box, 'pk-e', $('pk-e').value + '°');
      const ab = t => [id * Math.cos(t) - iq * Math.sin(t), id * Math.sin(t) + iq * Math.cos(t)];
      const abc = t => { const [a, b] = ab(t); return [a, -a / 2 + Math.sqrt(3) / 2 * b, -a / 2 - Math.sqrt(3) / 2 * b]; };
      const [ia, ib] = ab(th), [iu, iv, iw] = abc(th);
      const idm = id * Math.cos(e) + iq * Math.sin(e), iqm = -id * Math.sin(e) + iq * Math.cos(e);
      const cU = css('--u'), cV = css('--v'), cW = css('--w'), cD = css('--magN'), cQ = css('--copper'), ink = css('--ink'), mut = css('--muted'), line = css('--line');
      const A = Math.max(20, Math.ceil(Math.hypot(id, iq) / 20) * 20 + 10);
      { // time strip: abc on top, dq below, over one electrical turn
        const { g, w, h } = fit($('pk-wave'), 300); g.clearRect(0, 0, w, h);
        const L = 46, R = 10, top = [10, 150], bot = [176, 272], X = d => L + (w - L - R) * d / 360;
        const Y = (v, [t, b]) => t + (b - t) * (1 - (v / A + 1) / 2);
        g.font = FONT; g.fillStyle = mut; g.strokeStyle = line; g.lineWidth = 1;
        [top, bot].forEach(s => { g.beginPath(); g.moveTo(L, Y(0, s)); g.lineTo(w - R, Y(0, s)); g.stroke(); g.textAlign = 'right'; g.fillText('+' + A, L - 4, s[0] + 8); g.fillText('0', L - 4, Y(0, s) + 4); g.fillText('−' + A, L - 4, s[1]); });
        g.textAlign = 'left'; g.fillText('phase currents (stator)', L + 4, top[0] + 10); g.fillText('id, iq (rotor frame)', L + 4, bot[0] + 10);
        g.textAlign = 'center'; [0, 90, 180, 270, 360].forEach(d => g.fillText(d + '°', X(d), h - 8));
        [0, 1, 2].forEach(k => { const xs = [], ys = []; for (let d = 0; d <= 360; d += 3) { xs.push(d); ys.push(abc(d * D2R)[k]); } g.strokeStyle = [cU, cV, cW][k]; g.lineWidth = 2.2; g.beginPath(); xs.forEach((x, n) => n ? g.lineTo(X(x), Y(ys[n], top)) : g.moveTo(X(x), Y(ys[n], top))); g.stroke(); });
        [[id, cD, []], [iq, cQ, []], [idm, cD, [5, 4]], [iqm, cQ, [5, 4]]].forEach(([v, c, ds], k) => { if (k > 1 && Math.abs(e) < 1e-9) return; g.strokeStyle = c; g.lineWidth = 2.4; g.setLineDash(ds); g.beginPath(); g.moveTo(L, Y(v, bot)); g.lineTo(w - R, Y(v, bot)); g.stroke(); g.setLineDash([]); });
        const d = ((th / D2R) % 360 + 360) % 360; g.strokeStyle = ink; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(X(d), top[0]); g.lineTo(X(d), bot[1]); g.stroke(); g.setLineDash([]);
        [[iu, cU], [iv, cV], [iw, cW]].forEach(([v, c]) => { g.fillStyle = c; g.beginPath(); g.arc(X(d), Y(v, top), 4.5, 0, TAU); g.fill(); });
      }
      { // αβ plane with the rotating dq frame
        const { g, w, h } = fit($('pk-vec'), 300); g.clearRect(0, 0, w, h);
        const cx = w / 2, cy = h / 2, Rr = Math.min(w, h) / 2 - 28, sc = Rr / A, P = (r, a) => [cx + r * Math.cos(a), cy - r * Math.sin(a)];
        g.font = FONT; g.textAlign = 'center';
        [[0, cU, 'a = α'], [120, cV, 'b'], [240, cW, 'c']].forEach(([a, c, n]) => { const [x, y] = P(Rr, a * D2R); g.strokeStyle = line; g.lineWidth = 1; g.beginPath(); g.moveTo(2 * cx - x, 2 * cy - y); g.lineTo(x, y); g.stroke(); g.fillStyle = c; const [lx, ly] = P(Rr + 14, a * D2R); g.fillText(n, lx, ly + 4); });
        g.strokeStyle = line; g.setLineDash([2, 4]); g.beginPath(); g.moveTo(cx, cy + Rr); g.lineTo(cx, cy - Rr); g.stroke(); g.setLineDash([]); g.fillStyle = mut; g.fillText('β', cx + 10, cy - Rr + 4);
        const axis = (a, c, n, ds, wd) => { const [x, y] = P(Rr, a), [lx, ly] = P(Rr + 14, a); g.strokeStyle = c; g.lineWidth = wd; g.setLineDash(ds); g.beginPath(); g.moveTo(cx, cy); g.lineTo(x, y); g.stroke(); g.setLineDash([]); g.fillStyle = c; g.font = '600 13px IBM Plex Mono, monospace'; g.fillText(n, lx, ly + 4); g.font = FONT; };
        if (Math.abs(e) > 1e-9) { axis(th + e, cD, 'd̂', [5, 4], 1.5); axis(th + e + Math.PI / 2, cQ, 'q̂', [5, 4], 1.5); }
        axis(th, cD, 'd', [], 2.5); axis(th + Math.PI / 2, cQ, 'q', [], 2.5);
        const [dx, dy] = P(id * sc, th), [tx, ty] = P(Math.hypot(id, iq) * sc, Math.atan2(ib, ia));
        g.strokeStyle = mut; g.lineWidth = 1; g.setLineDash([3, 3]); g.beginPath(); g.moveTo(dx, dy); g.lineTo(tx, ty); g.stroke(); g.setLineDash([]);
        arrow(g, cx, cy, tx, ty, ink, 4); g.fillStyle = ink; g.fillText('i', tx + 10 * Math.sign(tx - cx || 1), ty - 6);
      }
      const rows = [['θ electrical', fmt(((th / D2R) % 360 + 360) % 360, 0) + '°'], ['ia', fmt(iu) + ' A'], ['ib', fmt(iv) + ' A'], ['ic', fmt(iw) + ' A'], ['iα', fmt(ia) + ' A'], ['iβ', fmt(ib) + ' A'], ['id', fmt(id) + ' A'], ['iq', fmt(iq) + ' A'], ['Torque made', fmt(torque(id, iq), 2) + ' Nm']];
      if (Math.abs(e) > 1e-9) rows.push(['id measured', fmt(idm) + ' A'], ['iq measured', fmt(iqm) + ' A'], ['Torque the controller thinks', fmt(torque(idm, iqm), 2) + ' Nm']);
      $('pk-r').innerHTML = readout(rows);
    }
    function tick(now) {
      if (!playing || !box.isConnected) return;
      const dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now; th = (th + TAU * +$('pk-s').value * dt) % TAU; draw(); requestAnimationFrame(tick);
    }
    const play = on => { playing = on; $('pk-play').setAttribute('aria-pressed', String(on)); $('pk-play').textContent = on ? 'Pause' : 'Run'; if (on) { last = 0; requestAnimationFrame(tick); } };
    $('pk-play').onclick = () => play(!playing); $('pk-e0').onclick = () => { $('pk-e').value = 0; draw(); };
    ['pk-d', 'pk-q', 'pk-s', 'pk-e'].forEach(id => $(id).addEventListener('input', draw));
    new ResizeObserver(draw).observe(box); draw(); play(playing);
    return draw;
  }

  // ---- idiq: the operating plane. Current circle, voltage ellipse, torque curves. ----
  function idiq(box) {
    box.insertAdjacentHTML('beforeend', `
      <div class="ctl">${slider('iq-n', 'Motor speed', 0, 8000, 50, 3000)}${slider('iq-d', 'id', -240, 120, 1, 0)}${slider('iq-q', 'iq', -150, 150, 1, 100)}</div>
      <div class="seg" role="group" aria-label="Shortcuts"><button type="button" id="iq-z">id = 0, as your VESC runs</button></div>
      <canvas id="iq-c" style="touch-action:none;cursor:crosshair"></canvas>
      <p class="legend"><span><i style="background:var(--accent)"></i>current limit 120 A</span><span><i style="background:var(--w)"></i>voltage limit 30 V peak (52 V bus ÷ √3)</span><span><i style="background:var(--muted)"></i>constant torque, Nm</span><span><i style="background:var(--copper)"></i>id = 0: field weakening OFF on your VESC</span><span>Drag the dot.</span></p>
      <dl class="readout" id="iq-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    const X0 = -240, X1 = 140, Y0 = -150, Y1 = 150;
    let map = null;
    function draw() {
      const n = +$('iq-n').value, id = +$('iq-d').value, iq = +$('iq-q').value, we = n * TAU / 60 * M.p;
      out(box, 'iq-n', fmt(n, 0) + ' rpm'); out(box, 'iq-d', id + ' A'); out(box, 'iq-q', iq + ' A');
      const ink = css('--ink'), mut = css('--muted'), line = css('--line'), acc = css('--accent'), cw = css('--w'), cop = css('--copper'), ok = css('--ok'), bad = css('--bad');
      const c = $('iq-c'), wid = Math.max(240, c.getBoundingClientRect().width), hh = Math.min(460, Math.max(260, wid * 0.82));
      const { g, w, h } = fit(c, hh); g.clearRect(0, 0, w, h);
      const pad = 30, sc = Math.min((w - 2 * pad) / (X1 - X0), (h - 2 * pad) / (Y1 - Y0)), ox = (w - sc * (X1 - X0)) / 2 - sc * X0, oy = (h - sc * (Y1 - Y0)) / 2 + sc * Y1;
      const X = x => ox + sc * x, Y = y => oy - sc * y; map = { ox, oy, sc };
      g.font = FONT; g.lineWidth = 1; g.strokeStyle = line; g.fillStyle = mut;
      for (let x = -200; x <= X1; x += 50) { g.beginPath(); g.moveTo(X(x), Y(Y0)); g.lineTo(X(x), Y(Y1)); g.stroke(); g.textAlign = 'center'; g.fillText(x, X(x), Y(Y0) + 14); }
      for (let y = -150; y <= Y1; y += 50) { g.beginPath(); g.moveTo(X(X0), Y(y)); g.lineTo(X(X1), Y(y)); g.stroke(); g.textAlign = 'right'; if (y) g.fillText(y, X(X0) - 3, Y(y) + 4); }
      g.strokeStyle = mut; g.beginPath(); g.moveTo(X(X0), Y(0)); g.lineTo(X(X1), Y(0)); g.moveTo(X(0), Y(Y0)); g.lineTo(X(0), Y(Y1)); g.stroke();
      g.fillStyle = mut; g.textAlign = 'right'; g.fillText('id, A →', X(X1), Y(0) - 5); g.textAlign = 'left'; g.fillText('iq, A', X(0) + 5, Y(Y1) + 10);
      g.save(); g.beginPath(); g.rect(X(X0), Y(Y1), sc * (X1 - X0), sc * (Y1 - Y0)); g.clip();
      // torque curves: iq = Te / (1.5 p (λ + (Ld − Lq) id))
      g.lineWidth = 1; g.strokeStyle = mut; g.setLineDash([2, 3]);
      [-8, -6, -4, -2, 2, 4, 6, 8].forEach(Te => { g.beginPath(); for (let x = X0; x <= X1; x += 4) { const y = Te / (1.5 * M.p * (M.lam + (M.Ld - M.Lq) * x)); x === X0 ? g.moveTo(X(x), Y(y)) : g.lineTo(X(x), Y(y)); } g.stroke(); const yl = Te / (1.5 * M.p * (M.lam + (M.Ld - M.Lq) * (X1 - 12))); if (yl > Y0 && yl < Y1) { g.fillStyle = mut; g.textAlign = 'right'; g.fillText(Te + ' Nm', X(X1) - 2, Y(yl) - 3); } });
      g.setLineDash([]);
      // id = 0 line (FW off)
      g.strokeStyle = cop; g.lineWidth = 3; g.globalAlpha = 0.55; g.beginPath(); g.moveTo(X(0), Y(-M.Imax)); g.lineTo(X(0), Y(M.Imax)); g.stroke(); g.globalAlpha = 1;
      // current circle
      g.strokeStyle = acc; g.lineWidth = 2.2; g.beginPath(); g.arc(X(0), Y(0), sc * M.Imax, 0, TAU); g.stroke();
      // voltage limit: V = M·i + b, |V| = Vpk  →  i = M⁻¹(Vpk·[cos φ, sin φ] − b)
      const a11 = M.Rs, a12 = -we * M.Lq, a21 = we * M.Ld, a22 = M.Rs, det = a11 * a22 - a12 * a21, b2 = we * M.lam;
      g.strokeStyle = cw; g.lineWidth = 2.2; g.beginPath();
      for (let k = 0; k <= 180; k++) { const f = k / 180 * TAU, v1 = M.Vpk * Math.cos(f), v2 = M.Vpk * Math.sin(f) - b2; const x = (a22 * v1 - a12 * v2) / det, y = (-a21 * v1 + a11 * v2) / det; k ? g.lineTo(X(x), Y(y)) : g.moveTo(X(x), Y(y)); }
      g.stroke();
      if (we > 0) { const cxE = -M.lam / M.Ld; g.fillStyle = cw; g.beginPath(); g.arc(X(cxE), Y(0), 3, 0, TAU); g.fill(); g.textAlign = 'center'; g.fillText('−λm/Ld', X(cxE), Y(0) + 15); }
      g.restore();
      // operating point
      const vd = M.Rs * id - we * M.Lq * iq, vq = M.Rs * iq + we * (M.Ld * id + M.lam), V = Math.hypot(vd, vq), I = Math.hypot(id, iq);
      const iOK = I <= M.Imax + 1e-9, vOK = V <= M.Vpk + 1e-9, feas = iOK && vOK;
      g.fillStyle = feas ? ok : bad; g.strokeStyle = ink; g.lineWidth = 2; g.beginPath(); g.arc(X(id), Y(iq), 7, 0, TAU); g.fill(); g.stroke();
      const nBase = M.Vpk / M.lam / M.p * 60 / TAU;
      $('iq-r').innerHTML = readout([['Torque', fmt(torque(id, iq), 2) + ' Nm'], ['|i|', fmt(I) + ' A' + (iOK ? '' : ' > 120')], ['vd', fmt(vd) + ' V'], ['vq', fmt(vq) + ' V'], ['|V| needed', fmt(V) + ' V' + (vOK ? '' : ' > 30')], ['Back-EMF ωe·λm', fmt(we * M.lam) + ' V'], ['Feasible', feas ? 'yes' : !iOK && !vOK ? 'no: current and voltage' : !iOK ? 'no: current' : 'no: voltage'], ['No-load top speed, id = 0', fmt(nBase, 0) + ' rpm']]);
    }
    function pick(ev) { if (!map) return; const r = $('iq-c').getBoundingClientRect(); const x = (ev.clientX - r.left - map.ox) / map.sc, y = (map.oy - (ev.clientY - r.top)) / map.sc; $('iq-d').value = Math.round(Math.max(-240, Math.min(120, x))); $('iq-q').value = Math.round(Math.max(Y0, Math.min(Y1, y))); draw(); }
    let drag = false; const c = $('iq-c');
    c.addEventListener('pointerdown', e => { drag = true; c.setPointerCapture(e.pointerId); pick(e); });
    c.addEventListener('pointermove', e => { if (drag) pick(e); });
    c.addEventListener('pointerup', () => { drag = false; }); c.addEventListener('pointercancel', () => { drag = false; });
    $('iq-z').onclick = () => { $('iq-d').value = 0; draw(); };
    ['iq-n', 'iq-d', 'iq-q'].forEach(id => $(id).addEventListener('input', draw));
    new ResizeObserver(draw).observe(box); draw();
    return draw;
  }

  // ---- rl: one phase as R-L, open-loop voltage step, rotor still (no back-EMF) ----
  function rl(box) {
    const R = M.Rs, Lh = M.Lq, tau = Lh / R;
    box.insertAdjacentHTML('beforeend', `
      <div class="ctl">${slider('rl-v', 'Voltage step on the phase', 0, 30, 0.1, 1)}</div>
      <canvas id="rl-c"></canvas>
      <p class="legend"><span><i style="background:var(--accent)"></i>i(t) = V/R · (1 − e^(−t/τ))</span><span><i style="background:var(--bad)"></i>120 A motor limit</span><span>R ${fmt(R * 1e3, 2)} mΩ, L ${fmt(Lh * 1e6, 0)} µH, rotor held still</span></p>
      <dl class="readout" id="rl-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    function draw() {
      const V = +$('rl-v').value, Iss = V / R; out(box, 'rl-v', fmt(V) + ' V');
      const acc = css('--accent'), bad = css('--bad'), mut = css('--muted'), ink = css('--ink');
      const { g, w, h } = fit($('rl-c'), 280); g.clearRect(0, 0, w, h);
      const tmax = 20, ymax = Math.max(150, Iss * 1.1), fr = frame(g, w, h, tmax, 0, ymax, 't, ms', 'i, A');
      const xs = [], ys = []; for (let k = 0; k <= 200; k++) { const t = tmax * k / 200; xs.push(t); ys.push(Iss * (1 - Math.exp(-t / (tau * 1e3)))); }
      hline(g, fr, w, M.Imax, bad, '120 A', [6, 4]);
      if (Iss > 0.5) hline(g, fr, w, Iss, mut, 'V/R = ' + fmt(Iss, 0) + ' A', [2, 3]);
      trace(g, xs, ys, fr.X, fr.Y, acc, 2.6);
      const tm = tau * 1e3, im = Iss * (1 - Math.exp(-1));
      g.strokeStyle = ink; g.setLineDash([3, 3]); g.lineWidth = 1; g.beginPath(); g.moveTo(fr.X(tm), fr.T); g.lineTo(fr.X(tm), fr.B); g.stroke(); g.setLineDash([]);
      g.fillStyle = ink; g.textAlign = 'left'; g.font = FONT; g.fillText('τ = ' + fmt(tm, 2) + ' ms', fr.X(tm) + 4, fr.T + 24);
      if (Iss > 0.5) { g.beginPath(); g.arc(fr.X(tm), fr.Y(im), 4.5, 0, TAU); g.fill(); }
      const t120 = Iss > M.Imax ? -tau * Math.log(1 - M.Imax / Iss) : NaN;
      $('rl-r').innerHTML = readout([['τ = L/R', fmt(tm, 2) + ' ms'], ['Final current V/R', fmt(Iss, 0) + ' A'], ['Per volt', fmt(1 / R, 1) + ' A/V'], ['Initial slope V/L', fmt(V / Lh / 1e3, 1) + ' A/ms'], ['At 1 τ (63 %)', fmt(im, 0) + ' A'], ['Reaches 120 A after', isNaN(t120) ? 'never' : fmt(t120 * 1e3, 2) + ' ms']]);
    }
    $('rl-v').addEventListener('input', draw);
    new ResizeObserver(draw).observe(box); draw();
    return draw;
  }

  // ---- piloop: PI current loop on the R-L phase, sampled at 30 kHz, ±30 V ----
  function piloop(box) {
    const R = M.Rs, Lh = M.Lq, Ts = M.Ts, a = Math.exp(-R * Ts / Lh), b = (1 - a) / R;
    box.insertAdjacentHTML('beforeend', `
      <div class="ctl">${slider('pl-kp', 'Kp', -2, 1, 0.01, Math.log10(M.vescKp).toFixed(2))}${slider('pl-ki', 'Ki', 0, 5, 0.01, Math.log10(M.vescKi).toFixed(2))}${slider('pl-ref', 'Step in iq reference', 0, 120, 1, 100)}</div>
      <div class="seg" role="group" aria-label="Options"><button type="button" id="pl-aw" aria-pressed="true">Anti-windup</button><button type="button" id="pl-pz">Cancel the pole: Ki = Kp·R/L</button><button type="button" id="pl-vesc">Your VESC's gains</button></div>
      <div class="seg" role="group" aria-label="Time window"><button type="button" data-tw="1">1 ms</button><button type="button" data-tw="5" aria-pressed="true">5 ms</button><button type="button" data-tw="20">20 ms</button></div>
      <div class="pair"><canvas id="pl-i"></canvas><canvas id="pl-v"></canvas></div>
      <p class="legend"><span><i style="background:var(--accent)"></i>your gains</span><span><i style="background:var(--muted)"></i>dashed: your VESC's gains, kp ${M.vescKp} V/A, ki ${M.vescKi} V/(A·s)</span><span><i style="background:var(--bad)"></i>±30 V the inverter can give</span><span>Rotor held still: no back-EMF. The voltage from sample k is applied in the next period.</span></p>
      <dl class="readout" id="pl-r"></dl>`);
    const $ = id => box.querySelector('#' + id);
    let aw = true, tw = 5;
    function sim(Kp, Ki, ref, N) {
      let i = 0, vi = 0, vApp = 0; const I = [], V = [];
      for (let k = 0; k <= N; k++) {
        I.push(i); V.push(vApp);
        const e = ref - i; let viN = vi + e * Ki * Ts; let v = viN + Kp * e;
        if (aw) { if (Math.abs(v) > M.Vpk && Math.sign(e) === Math.sign(v)) viN = vi; viN = Math.max(-M.Vpk, Math.min(M.Vpk, viN)); v = viN + Kp * e; }
        vi = viN; const vSat = Math.max(-M.Vpk, Math.min(M.Vpk, v));
        i = a * i + b * vApp; vApp = vSat; // one-sample computation delay
        if (!isFinite(i) || Math.abs(i) > 1e5) { i = Math.sign(i) * 1e5; }
      }
      return { I, V };
    }
    const flips = x => { let n = 0; for (let k = 2; k < x.length; k++) if ((x[k] - x[k - 1]) * (x[k - 1] - x[k - 2]) < 0) n++; return n; }; // oscillation, not a slow rise
    function metrics(I, ref) {
      if (ref < 1) return null;
      const N = I.length, k10 = I.findIndex(x => x >= 0.1 * ref), k90 = I.findIndex(x => x >= 0.9 * ref), tail = I.slice(Math.floor(N * 0.8));
      const mx = Math.max(...I), end = tail.reduce((s, x) => s + x, 0) / tail.length, spread = Math.max(...tail) - Math.min(...tail);
      return { rise: k10 >= 0 && k90 >= 0 ? (k90 - k10) * Ts : NaN, over: Math.max(0, mx / ref - 1), sse: ref - end, unstable: Math.abs(mx) > 5 * ref + 200 || (spread > 0.02 * ref + 0.2 && flips(tail) >= 3) };
    }
    function draw() {
      const Kp = Math.pow(10, +$('pl-kp').value), Ki = Math.pow(10, +$('pl-ki').value), ref = +$('pl-ref').value;
      out(box, 'pl-kp', fmt(Kp, Kp < 1 ? 3 : 2) + ' V/A'); out(box, 'pl-ki', fmt(Ki, Ki < 10 ? 2 : 1) + ' V/(A·s)'); out(box, 'pl-ref', ref + ' A');
      const N = Math.round(tw * 1e-3 / Ts), you = sim(Kp, Ki, ref, N), ves = sim(M.vescKp, M.vescKi, ref, N);
      const t = you.I.map((_, k) => k * Ts * 1e3);
      const acc = css('--accent'), mut = css('--muted'), bad = css('--bad'), ink = css('--ink');
      const clip = (arr, lo, hi) => arr.map(x => Math.max(lo, Math.min(hi, x)));
      { const { g, w, h } = fit($('pl-i'), 240); g.clearRect(0, 0, w, h); const ymax = Math.max(20, ref * 1.6), ymin = -0.2 * ymax, fr = frame(g, w, h, tw, ymin, ymax, 't, ms', 'iq, A');
        hline(g, fr, w, ref, ink, 'ref ' + ref + ' A', [2, 3]);
        trace(g, t, clip(ves.I, ymin, ymax), fr.X, fr.Y, mut, 1.6, [5, 4]); trace(g, t, clip(you.I, ymin, ymax), fr.X, fr.Y, acc, 2.6); }
      { const { g, w, h } = fit($('pl-v'), 240); g.clearRect(0, 0, w, h); const fr = frame(g, w, h, tw, -36, 36, 't, ms', 'v, V');
        hline(g, fr, w, M.Vpk, bad, '+30 V', [6, 4]); hline(g, fr, w, -M.Vpk, bad, '−30 V', [6, 4]);
        trace(g, t, ves.V, fr.X, fr.Y, mut, 1.6, [5, 4]); trace(g, t, you.V, fr.X, fr.Y, acc, 2.6); }
      const m = metrics(you.I, ref), bw = Kp / Lh;
      const rows = m ? [['Rise 10–90 %', m.unstable ? 'unstable / oscillating' : isNaN(m.rise) ? 'not reached' : fmt(m.rise * 1e6, 0) + ' µs'], ['Overshoot', m.unstable ? '—' : fmt(m.over * 100, 1) + ' %'], ['Error at end of window', m.unstable ? '—' : fmt(m.sse, 2) + ' A']] : [['Step', 'set a reference']];
      rows.push(['Bandwidth ≈ Kp/L', fmt(bw, 0) + ' rad/s = ' + fmt(bw / TAU, 0) + ' Hz'], ['PI zero Ki/Kp', fmt(Ki / Kp, 0) + ' 1/s'], ['Plant pole R/L', fmt(R / Lh, 0) + ' 1/s'], ['Peak voltage asked', fmt(Math.max(...you.V.map(Math.abs)), 1) + ' V']);
      $('pl-r').innerHTML = readout(rows);
    }
    const setLog = (id, v) => { $(id).value = Math.log10(v).toFixed(2); };
    $('pl-aw').onclick = () => { aw = !aw; $('pl-aw').setAttribute('aria-pressed', String(aw)); draw(); };
    $('pl-pz').onclick = () => { const Kp = Math.pow(10, +$('pl-kp').value); $('pl-ki').value = Math.log10(Kp * R / Lh); draw(); };
    $('pl-vesc').onclick = () => { setLog('pl-kp', M.vescKp); setLog('pl-ki', M.vescKi); draw(); };
    box.querySelectorAll('[data-tw]').forEach(bt => bt.onclick = () => { tw = +bt.dataset.tw; box.querySelectorAll('[data-tw]').forEach(x => x.setAttribute('aria-pressed', String(x === bt))); draw(); });
    ['pl-kp', 'pl-ki', 'pl-ref'].forEach(id => $(id).addEventListener('input', draw));
    new ResizeObserver(draw).observe(box); draw();
    return draw;
  }

  const REG = { clarke: ['Three currents become one arrow', 'Clarke'], hexagon: ['The hexagon and the two circles', 'SVPWM'], park: ['In the rotor\'s frame the currents stand still', 'Park'], idiq: ['Where the motor can operate', 'id–iq plane'], rl: ['One phase is an R-L circuit', 'R-L step'], piloop: ['Closing the current loop', 'PI loop'] };
  function mount(box) {
    const name = box.dataset.lab, fn = { clarke, hexagon, park, idiq, rl, piloop }[name];
    if (!fn) { box.textContent = 'Unknown lab: ' + name; return; }
    box.insertAdjacentHTML('afterbegin', `<h3>${box.dataset.title || REG[name][0]} <small>${REG[name][1]}</small></h3>`);
    const redraw = fn(box);
    new MutationObserver(redraw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', redraw);
  }
  return { mount };
})();
