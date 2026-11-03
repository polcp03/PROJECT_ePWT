/* Motor3D — Pol's motor as it is built: an interior-magnet PMSM with an inner rotor and an outer
   slotted stator, p = 3. One scene for every lesson; a lesson changes its state with presets.
   Proportions and slot count (18, q = 1) are illustrative: slot count and magnet layout are not
   measured (03_hardware/baseline.md). The air gap is drawn about twice its real size. */
window.Motor3D = (function () {
  const TAU = Math.PI * 2, D2R = Math.PI / 180;
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const fmt = (x, d) => (Math.abs(x) < 5e-10 ? 0 : x).toLocaleString('en-GB', { minimumFractionDigits: d, maximumFractionDigits: d });
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // geometry, in centimetres-ish scene units
  const P = 3, NS = 18, RSO = 6.0, RB = 3.7, RS = 5.0, R1 = RB + 0.16, W1 = 0.19, W2 = 0.38, OPEN = 0.11;
  const RR = 3.52, RSH = 0.85, L = 5.0, NLAM = 10;
  const RM = 2.85, MA = 1.15, MT = 0.32; // magnet bar: radial position, half length, thickness
  // slot n holds this phase with this sign (q = 1, full pitch, 60 deg phase belts): U+ W- V+ U- W+ V-
  const BELT = [[0, 1], [2, -1], [1, 1], [0, -1], [2, 1], [1, -1]];
  const slotAngle = n => (n + 0.5) * TAU / NS;

  const DEFAULT = { phases: 3, field: true, currents: true, labels: false, rotor: true, vectors: false, spin: true, speed: 0.2, delta: 90, endturns: true, caption: '' };

  function mount(host) {
    const vp = host.querySelector('.vp'), labelsEl = host.querySelector('.labels'), hud = host.querySelector('.hud');
    const S = Object.assign({}, DEFAULT, { wt: 30 * D2R });
    if (!window.THREE) { vp.innerHTML = '<p class="fallback">The 3D motor did not load (no connection to the 3D library). The rest of the lesson works.</p>'; return null; }
    const T = THREE;
    let renderer;
    try { renderer = new T.WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { vp.innerHTML = '<p class="fallback">This browser has no WebGL, so the 3D motor cannot run here.</p>'; return null; }
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    vp.prepend(renderer.domElement);
    const scene = new T.Scene();
    const cam = new T.PerspectiveCamera(36, 1, 0.1, 200);
    cam.position.set(4.2, -10.5, 23.5); cam.up.set(0, 0, 1); cam.lookAt(0, 0, 0);
    const controls = T.OrbitControls ? new T.OrbitControls(cam, renderer.domElement) : null;
    if (controls) { controls.enableDamping = true; controls.minDistance = 7; controls.maxDistance = 30; controls.enablePan = false; }
    scene.add(new T.HemisphereLight(0xffffff, 0x445048, 0.95));
    const key = new T.DirectionalLight(0xffffff, 0.75); key.position.set(6, -8, 14); scene.add(key);
    const rim = new T.DirectionalLight(0xffffff, 0.35); rim.position.set(-8, 6, -4); scene.add(rim);
    const col = n => new T.Color(css(n) || '#888');

    const mats = {
      steel: new T.MeshStandardMaterial({ color: 0xb9c3c8, metalness: 0.15, roughness: 0.5 }),
      steelDark: new T.MeshStandardMaterial({ color: 0x96a1a7, metalness: 0.15, roughness: 0.55 }),
      shaft: new T.MeshStandardMaterial({ color: 0xd6dadc, metalness: 0.25, roughness: 0.3 }),
      hall: new T.MeshStandardMaterial({ color: 0x1b1e1f, roughness: 0.6 }),
      magN: new T.MeshStandardMaterial({ color: col('--magN'), metalness: 0.1, roughness: 0.4 }),
      magS: new T.MeshStandardMaterial({ color: col('--magS'), metalness: 0.1, roughness: 0.4 }),
    };
    const phaseCol = () => [col('--u'), col('--v'), col('--w')];
    const copperMats = [0, 1, 2].map(k => new T.MeshStandardMaterial({ color: 0xd27b3c, metalness: 0.25, roughness: 0.35, emissive: phaseCol()[k], emissiveIntensity: 0 }));
    const endMats = [0, 1, 2].map(k => new T.MeshStandardMaterial({ color: phaseCol()[k], metalness: 0.2, roughness: 0.5, emissive: phaseCol()[k], emissiveIntensity: 0 }));

    // ---- stator lamination: outer circle, bore with 18 slots ----
    function pt(theta, rad, w) { const c = Math.cos(theta), s = Math.sin(theta); return new T.Vector2(c * rad - s * w, s * rad + c * w); }
    function boreContour() {
      const pts = [];
      for (let n = 0; n < NS; n++) {
        const th = slotAngle(n);
        pts.push(pt(th, RB, -OPEN), pt(th, RB + 0.1, -OPEN), pt(th, R1, -W1), pt(th, RS - 0.28, -W2), pt(th, RS - 0.05, -W2 * 0.62), pt(th, RS + 0.06, 0),
          pt(th, RS - 0.05, W2 * 0.62), pt(th, RS - 0.28, W2), pt(th, R1, W1), pt(th, RB + 0.1, OPEN), pt(th, RB, OPEN));
        const a0 = th + OPEN / RB, a1 = slotAngle(n + 1) - OPEN / RB;
        for (let k = 1; k < 6; k++) { const a = a0 + (a1 - a0) * k / 6; pts.push(new T.Vector2(RB * Math.cos(a), RB * Math.sin(a))); }
      }
      return pts;
    }
    const statorShape = new T.Shape(); statorShape.absarc(0, 0, RSO, 0, TAU, false);
    statorShape.holes.push(new T.Path(boreContour()));
    const lamD = L / NLAM;
    const statorG = new T.Group(); scene.add(statorG);
    const statorGeo = new T.ExtrudeGeometry(statorShape, { depth: lamD - 0.035, bevelEnabled: false, curveSegments: 80 });
    for (let k = 0; k < NLAM; k++) { const m = new T.Mesh(statorGeo, k % 2 ? mats.steel : mats.steelDark); m.position.z = -L / 2 + k * lamD; statorG.add(m); }

    // ---- copper in the slots ----
    function slotFill(th) {
      return new T.Shape([pt(th, R1 + 0.05, -(W1 - 0.04)), pt(th, RS - 0.3, -(W2 - 0.05)), pt(th, RS - 0.08, -W2 * 0.5), pt(th, RS + 0.0, 0), pt(th, RS - 0.08, W2 * 0.5), pt(th, RS - 0.3, W2 - 0.05), pt(th, R1 + 0.05, W1 - 0.04)]);
    }
    const slots = [];
    for (let n = 0; n < NS; n++) {
      const [ph, sign] = BELT[n % 6];
      const geo = new T.ExtrudeGeometry(slotFill(slotAngle(n)), { depth: L + 0.2, bevelEnabled: false });
      const m = new T.Mesh(geo, copperMats[ph]); m.position.z = -L / 2 - 0.1; statorG.add(m);
      slots.push({ n, ph, sign, th: slotAngle(n) });
    }
    // ---- end windings: each coil goes from a + slot to the - slot three slots on ----
    const endG = new T.Group(); statorG.add(endG);
    const rc = (R1 + RS) / 2;
    slots.filter(s => s.sign > 0).forEach(s => {
      [-1, 1].forEach(side => {
        const a0 = s.th, a1 = slotAngle(s.n + 3), z0 = side * (L / 2 + 0.1), pts = [];
        for (let k = 0; k <= 16; k++) { const f = k / 16, a = a0 + (a1 - a0) * f, bulge = Math.sin(Math.PI * f); pts.push(new T.Vector3((rc + 0.25 * bulge) * Math.cos(a), (rc + 0.25 * bulge) * Math.sin(a), z0 + side * (0.15 + 0.75 * bulge))); }
        const tube = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), 32, 0.2, 10, false), endMats[s.ph]);
        tube.userData.side = side; endG.add(tube);
      });
    });
    // ---- Hall sensors at the back, 40 deg mechanical apart = 120 deg electrical ----
    [0, 40, 80].forEach(d => { const a = d * D2R + TAU / NS; const h = new T.Mesh(new T.BoxGeometry(0.35, 0.5, 0.25), mats.hall); h.position.set((RB + 0.25) * Math.cos(a), (RB + 0.25) * Math.sin(a), -L / 2 - 0.15); h.rotation.z = a; statorG.add(h); });

    // ---- rotor: laminated core with interior magnet bars and flux barriers ----
    function pocket(phi) {
      const loc = [[RM - MT / 2, -MA], [RM - MT / 2, MA], [RM + 0.1, MA + 0.3], [RM + 0.32, MA + 0.22], [RM + MT / 2, MA], [RM + MT / 2, -MA], [RM + 0.32, -MA - 0.22], [RM + 0.1, -MA - 0.3]];
      return loc.map(([x, y]) => pt(phi, x, y));
    }
    const rotorShape = new T.Shape(); rotorShape.absarc(0, 0, RR, 0, TAU, false);
    const shaftHole = new T.Path(); shaftHole.absarc(0, 0, RSH, 0, TAU, true); rotorShape.holes.push(shaftHole);
    for (let j = 0; j < 2 * P; j++) rotorShape.holes.push(new T.Path(pocket(j * TAU / (2 * P))));
    const rotorG = new T.Group(); scene.add(rotorG);
    const rotorGeo = new T.ExtrudeGeometry(rotorShape, { depth: lamD - 0.035, bevelEnabled: false, curveSegments: 72 });
    for (let k = 0; k < NLAM; k++) { const m = new T.Mesh(rotorGeo, k % 2 ? mats.steel : mats.steelDark); m.position.z = -L / 2 + k * lamD; rotorG.add(m); }
    const magnets = [];
    for (let j = 0; j < 2 * P; j++) {
      const phi = j * TAU / (2 * P);
      const shp = new T.Shape([pt(phi, RM - MT / 2 + 0.02, -MA + 0.02), pt(phi, RM + MT / 2 - 0.02, -MA + 0.02), pt(phi, RM + MT / 2 - 0.02, MA - 0.02), pt(phi, RM - MT / 2 + 0.02, MA - 0.02)]);
      const m = new T.Mesh(new T.ExtrudeGeometry(shp, { depth: L - 0.04, bevelEnabled: false }), j % 2 ? mats.magS : mats.magN);
      m.position.z = -L / 2 + 0.02; rotorG.add(m); magnets.push(m);
    }
    const shaft = new T.Mesh(new T.CylinderGeometry(RSH, RSH, L + 4.5, 40), mats.shaft); shaft.rotation.x = Math.PI / 2; shaft.position.z = -0.9; rotorG.add(shaft);
    const key3 = new T.Mesh(new T.BoxGeometry(0.3, 0.3, 1.6), mats.steelDark); key3.position.set(RSH, 0, L / 2 + 0.9); rotorG.add(key3);

    // ---- air-gap field arrows on the front face ----
    const arrowG = new T.Group(); scene.add(arrowG);
    const NA = 90, arrows = [];
    for (let k = 0; k < NA; k++) { const th = k / NA * TAU; const a = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(), 0.4, 0x888888, 0.12, 0.09); a.userData.th = th; arrowG.add(a); arrows.push(a); }
    // ---- vectors: stator field axis and rotor N axis (one pole pair shown) ----
    const vecG = new T.Group(); scene.add(vecG);
    const vStator = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0, 0, L / 2 + 1.6), 3.4, 0xffffff, 0.45, 0.3);
    const vRotor = new T.ArrowHelper(new T.Vector3(1, 0, 0), new T.Vector3(0, 0, L / 2 + 1.55), 2.7, 0xffffff, 0.4, 0.28);
    vecG.add(vStator, vRotor);
    // ---- current glyphs (dot = out of the page, cross = into it) on each slot face ----
    function glyph(dot) {
      const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
      g.fillStyle = 'rgba(255,255,255,.92)'; g.beginPath(); g.arc(32, 32, 28, 0, TAU); g.fill();
      g.strokeStyle = '#111'; g.lineWidth = 5; g.beginPath(); g.arc(32, 32, 26, 0, TAU); g.stroke();
      if (dot) { g.fillStyle = '#111'; g.beginPath(); g.arc(32, 32, 8, 0, TAU); g.fill(); } else { g.beginPath(); g.moveTo(16, 16); g.lineTo(48, 48); g.moveTo(48, 16); g.lineTo(16, 48); g.stroke(); }
      const t = new T.CanvasTexture(c); return new T.SpriteMaterial({ map: t, depthTest: false });
    }
    const gDot = glyph(true), gCross = glyph(false);
    const glyphs = slots.map(s => { const sp = new T.Sprite(gDot); sp.position.set(rc * Math.cos(s.th), rc * Math.sin(s.th), L / 2 + 0.25); sp.scale.set(0.42, 0.42, 1); scene.add(sp); return sp; });

    // ---- labels ----
    const tooth = TAU / NS;
    const LABELS = [
      ['Stator lamination stack (steel)', new T.Vector3(5.5 * Math.cos(1.05), 5.5 * Math.sin(1.05), L / 2)],
      ['Tooth', new T.Vector3(4.3 * Math.cos(2 * tooth), 4.3 * Math.sin(2 * tooth), L / 2)],
      ['Slot with copper winding', new T.Vector3(4.45 * Math.cos(slotAngle(4)), 4.45 * Math.sin(slotAngle(4)), L / 2 + 0.1)],
      ['Air gap (drawn 2× real)', new T.Vector3(3.61 * Math.cos(3.3), 3.61 * Math.sin(3.3), L / 2)],
      ['Rotor lamination', new T.Vector3(1.6 * Math.cos(2.6), 1.6 * Math.sin(2.6), L / 2), true],
      ['Magnet inside the rotor', new T.Vector3(RM * Math.cos(TAU / 6 * 4), RM * Math.sin(TAU / 6 * 4), L / 2), true],
      ['Flux barrier (air)', null, true],
      ['Shaft', new T.Vector3(0, 0, L / 2 + 2.2), true],
      ['End winding', new T.Vector3(rc * Math.cos(slotAngle(10)), rc * Math.sin(slotAngle(10)), -L / 2 - 0.9)],
      ['Hall sensors', new T.Vector3((RB + 0.3) * Math.cos(TAU / NS + 0.7), (RB + 0.3) * Math.sin(TAU / NS + 0.7), -L / 2 - 0.3)],
    ];
    { const phi = TAU / 6 * 4; const p2 = pt(phi, RM + 0.25, MA + 0.28); LABELS[6][1] = new T.Vector3(p2.x, p2.y, L / 2); }
    const labelEls = LABELS.map(([t]) => { const s = document.createElement('span'); s.textContent = t; labelsEl.appendChild(s); return s; });

    function applyColors() {
      mats.magN.color = col('--magN'); mats.magS.color = col('--magS');
      const pc = phaseCol(); copperMats.forEach((m, k) => m.emissive = pc[k]); endMats.forEach((m, k) => { m.color = pc[k]; m.emissive = pc[k]; });
    }
    function resize() {
      const w = vp.clientWidth, h = vp.clientHeight; if (!w || !h) return;
      renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
    }
    new ResizeObserver(resize).observe(vp); resize();
    new MutationObserver(applyColors).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', applyColors);

    function currents(wt) {
      if (S.phases === 0) return [0, 0, 0];
      const order = S.phases === 'swap' ? [0, 2, 1] : [0, 1, 2];
      const i = [0, 1, 2].map(k => Math.cos(wt - order[k] * 120 * D2R));
      if (S.phases === 1) { i[1] = 0; i[2] = 0; }
      return i;
    }
    // field peak electrical angle; NaN when the field does not rotate
    const fieldE = () => S.phases === 3 ? S.wt : S.phases === 'swap' ? -S.wt : NaN;
    let rotorE = 0;

    let visible = true;
    new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(vp);
    let last = performance.now(), lastHud = 0;
    function frame(now) {
      const dt = Math.min(0.05, (now - last) / 1000); last = now;
      if (visible) {
        if (S.spin && !reduce && S.phases !== 0) S.wt = (S.wt + TAU * S.speed * dt) % TAU;
        const i = currents(S.wt), fE = fieldE();
        if (!isNaN(fE)) rotorE = fE - S.delta * D2R;
        rotorG.rotation.z = S.rotor ? rotorE / P : rotorG.rotation.z;
        rotorG.visible = S.rotor;
        const nC = col('--magN'), sC = col('--magS');
        arrowG.visible = S.field;
        if (S.field) arrows.forEach(a => {
          const th = a.userData.th; let B = 0;
          for (let k = 0; k < 3; k++) B += i[k] * Math.cos(P * th - k * 120 * D2R);
          const Lr = Math.max(0.03, Math.abs(B) * 0.75), out = B >= 0;
          const dir = new T.Vector3(Math.cos(th), Math.sin(th), 0).multiplyScalar(out ? 1 : -1);
          const r = out ? RB - 0.05 : RB - 0.05 + Lr;
          a.position.set(r * Math.cos(th), r * Math.sin(th), L / 2 + 0.12);
          a.setDirection(dir); a.setLength(Lr, Math.min(0.24, Lr * 0.45), 0.16); a.setColor(out ? nC : sC);
        });
        copperMats.forEach((m, k) => m.emissiveIntensity = S.currents ? 0.55 * Math.abs(i[k]) : 0);
        endMats.forEach((m, k) => m.emissiveIntensity = S.currents ? 0.45 * Math.abs(i[k]) : 0.05);
        endG.children.forEach(t => t.visible = S.endturns && (t.userData.side < 0 || S.endturns === 'both'));
        glyphs.forEach((g, n) => { const s = slots[n], v = i[s.ph] * s.sign; g.visible = S.currents && Math.abs(v) > 0.08; g.material = v >= 0 ? gDot : gCross; const sc = 0.22 + 0.3 * Math.abs(v); g.scale.set(sc, sc, 1); });
        vecG.visible = S.vectors;
        if (S.vectors) {
          vStator.visible = !isNaN(fE);
          if (!isNaN(fE)) { const a = fE / P; vStator.setDirection(new T.Vector3(Math.cos(a), Math.sin(a), 0)); vStator.setColor(col('--accent')); }
          const ar = rotorG.rotation.z; vRotor.setDirection(new T.Vector3(Math.cos(ar), Math.sin(ar), 0)); vRotor.setColor(col('--magN'));
        }
        if (controls) controls.update();
        renderer.render(scene, cam);
        // labels
        const w = vp.clientWidth, h = vp.clientHeight;
        LABELS.forEach(([, p, onRotor], k) => {
          const el = labelEls[k];
          if (!S.labels || (onRotor && !S.rotor)) { el.classList.add('hidden'); return; }
          const v = p.clone(); if (onRotor) v.applyAxisAngle(new T.Vector3(0, 0, 1), rotorG.rotation.z);
          v.project(cam);
          if (v.z > 1) { el.classList.add('hidden'); return; }
          el.classList.remove('hidden'); el.style.left = ((v.x + 1) / 2 * w) + 'px'; el.style.top = ((1 - v.y) / 2 * h - 8) + 'px';
        });
        if (now - lastHud > 120) { lastHud = now; updateReadout(i, fE); }
      }
      requestAnimationFrame(frame);
    }

    // ---- controls and readout ----
    const ro = host.querySelector('.readout'), cap = host.querySelector('.caption');
    function updateReadout(i, fE) {
      const deg = x => fmt(((x / D2R) % 360 + 360) % 360, 0) + '°';
      const rows = [['iU', fmt(i[0] * 100, 0) + ' %'], ['iV', fmt(i[1] * 100, 0) + ' %'], ['iW', fmt(i[2] * 100, 0) + ' %'],
        ['Electrical angle ωt', deg(S.wt)], ['Field peak (mechanical)', isNaN(fE) ? 'not rotating' : deg(fE / P)],
        ['Torque per amp', isNaN(fE) ? '0 on average' : fmt(Math.sin(S.delta * D2R) * 100, 0) + ' % of max']];
      ro.innerHTML = rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('');
      hud.textContent = S.phases === 0 ? 'no current' : S.phases === 1 ? 'phase U only' : S.phases === 'swap' ? 'V and W swapped' : 'U, V, W';
    }
    const segs = {};
    host.querySelectorAll('[data-set]').forEach(b => {
      const [k, v] = b.dataset.set.split('=');
      (segs[k] = segs[k] || []).push(b);
      b.addEventListener('click', () => set({ [k]: parseVal(k, v) }));
    });
    host.querySelectorAll('[data-toggle]').forEach(b => b.addEventListener('click', () => set({ [b.dataset.toggle]: !S[b.dataset.toggle] })));
    const sp = host.querySelector('#m-speed'), de = host.querySelector('#m-delta');
    sp.addEventListener('input', () => set({ speed: +sp.value })); de.addEventListener('input', () => set({ delta: +de.value }));
    function parseVal(k, v) {
      if (v === 'true' || v === 'on') return true; if (v === 'false' || v === 'off') return false;
      if (k === 'phases') return v === 'swap' ? 'swap' : +v;
      if (k === 'endturns' && v === 'both') return 'both';
      return isNaN(+v) ? v : +v;
    }
    function sync() {
      Object.entries(segs).forEach(([k, bs]) => bs.forEach(b => b.setAttribute('aria-pressed', String(String(parseVal(k, b.dataset.set.split('=')[1])) === String(S[k])))));
      host.querySelectorAll('[data-toggle]').forEach(b => b.setAttribute('aria-pressed', String(!!S[b.dataset.toggle])));
      sp.value = S.speed; host.querySelector('#o-speed').textContent = fmt(S.speed, 2) + ' cycles/s';
      de.value = S.delta; host.querySelector('#o-delta').textContent = fmt(S.delta, 0) + '°';
      cap.textContent = S.caption || '';
    }
    function set(patch) { Object.assign(S, patch); sync(); }
    function preset(attrs) {
      const p = Object.assign({}, DEFAULT);
      Object.entries(attrs || {}).forEach(([k, v]) => { p[k] = k === 'caption' ? v : parseVal(k, v); });
      if ('wt' in p) p.wt = p.wt * D2R; else delete p.wt;
      set(p);
    }
    applyColors(); sync(); requestAnimationFrame(frame);
    return { set, preset, state: S };
  }

  function panelHTML() {
    return `<div class="motor" id="motor">
  <div class="vp"><div class="labels"></div><div class="hud"></div></div>
  <div class="body">
    <p class="caption"></p>
    <div class="seg" role="group" aria-label="Phase currents">
      <button type="button" data-set="phases=0">No current</button><button type="button" data-set="phases=1">U only</button>
      <button type="button" data-set="phases=3">U, V, W</button><button type="button" data-set="phases=swap">Swap V and W</button>
    </div>
    <div class="seg" role="group" aria-label="Layers">
      <button type="button" data-toggle="labels">Labels</button><button type="button" data-toggle="field">Gap field</button>
      <button type="button" data-toggle="currents">Currents ⊙⊗</button><button type="button" data-toggle="vectors">Field and rotor axes</button>
      <button type="button" data-toggle="rotor">Rotor</button><button type="button" data-toggle="spin">Run</button>
    </div>
    <div class="ctl">
      <div><label for="m-speed">Electrical speed <output id="o-speed"></output></label><input id="m-speed" type="range" min="0.02" max="1" step="0.01"></div>
      <div><label for="m-delta">Angle δ, rotor behind field <output id="o-delta"></output></label><input id="m-delta" type="range" min="0" max="180" step="1"></div>
    </div>
    <dl class="readout"></dl>
    <p class="legend"><span><i style="background:var(--u)"></i>U</span><span><i style="background:var(--v)"></i>V</span><span><i style="background:var(--w)"></i>W</span><span><i style="background:var(--magN)"></i>N magnet · field out of rotor</span><span><i style="background:var(--magS)"></i>S magnet · field into rotor</span></p>
    <p class="src">18 slots and the magnet layout are illustrative: neither is measured yet. p = 3 is measured. Drag to turn, wheel or pinch to zoom.</p>
  </div>
</div>`;
  }
  return { mount, panelHTML };
})();
