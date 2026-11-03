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

  const REG = { clarke: ['Three currents become one arrow', 'Clarke'], hexagon: ['The hexagon and the two circles', 'SVPWM'] };
  function mount(box) {
    const name = box.dataset.lab, fn = { clarke, hexagon }[name];
    if (!fn) { box.textContent = 'Unknown lab: ' + name; return; }
    box.insertAdjacentHTML('afterbegin', `<h3>${box.dataset.title || REG[name][0]} <small>${REG[name][1]}</small></h3>`);
    const redraw = fn(box);
    new MutationObserver(redraw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', redraw);
  }
  return { mount };
})();
