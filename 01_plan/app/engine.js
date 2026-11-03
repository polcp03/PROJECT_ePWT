/* ePWT Bench engine — lessons, automatic grading by Claude, spaced review of mistakes.
   Storage (artifact db):
     attempts/<lesson>-<q>  one per question: turns, verdict, history
     errors/<id>            open mistakes: question, said, correct, status red/yellow/green, due, hits
     doubts/<id>            "what I still don't get", with Claude's explanation
   Grading uses the `sample` capability. Without it, answers are saved as "ungraded" and the
   Sunday sync grades them (prompts/sincronizar.md). */
(function () {
  const DATA = JSON.parse(document.getElementById('data').textContent);
  const LESSONS = DATA.lessons;
  const view = document.getElementById('view');
  let db = null, sample = null, ready = false;
  const attempts = {};   // id -> doc
  const errors = {};     // id -> doc
  const doubts = [];
  let motor = null;

  // ---------- small helpers ----------
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const el = (tag, attrs, kids) => { const e = document.createElement(tag); Object.entries(attrs || {}).forEach(([k, v]) => { if (k === 'text') e.textContent = v; else if (k === 'html') e.innerHTML = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else if (v != null && v !== false) e.setAttribute(k, v); }); (kids || []).forEach(k => k && e.append(k)); return e; };
  const day = (offset = 0) => { const d = new Date(); d.setDate(d.getDate() + offset); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  const words = s => (s.trim().match(/\S+/g) || []).length;
  const store = { get(k) { try { return localStorage.getItem('bench:' + k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem('bench:' + k, v); } catch (e) { } } };
  const VERDICT = { right: '✓ Right', partial: '◐ Partly', wrong: '✗ Wrong', no_attempt: '✗ No attempt', saved: 'Saved · not graded yet' };

  async function save(path, data) {
    if (!db) return;
    try { const ref = db.doc(path); const cur = await ref.get(); if (cur.exists) await ref.update(data); else await ref.set(data); } catch (e) { console.warn('save failed', path, e); }
  }

  // ---------- grading prompts ----------
  const ROLE = 'You are the senior engineer who reviews Pol\'s work. Pol is a powertrain calibration engineer (combustion ECUs, SEAT/VW) learning electric machines and control from first principles on his own electric quad, to get a systems-engineer job in an Israeli robotics startup. He answers by typing or by voice dictation, in English or Spanish: ignore transcription errors and grammar. Write in plain, short English sentences.\n\n';
  function gradePrompt(q, lesson, answer) {
    return ROLE +
      'Facts about his motor (use them, never invent others):\n' + DATA.facts + '\n\n' +
      'Lesson: ' + lesson.title + '\nQuestion: ' + q.prompt_text + '\n\n' +
      'What a correct answer must contain (your private key, do not paste it):\n- ' + q.key.join('\n- ') + '\n' +
      (q.traps.length ? 'Typical mistakes to watch for:\n- ' + q.traps.join('\n- ') + '\n' : '') +
      '\nPol\'s answer (' + words(answer) + ' words):\n"""\n' + answer + '\n"""\n\n' +
      'Grade it like a senior engineer, against the key, not the wording:\n' +
      '- Attack HIS answer. Quote or paraphrase what he actually said when you correct it.\n' +
      '- Name wrong physics plainly. Do not soften it.\n' +
      '- If he answered more than was asked or mixed questions, say so in wrong.\n' +
      '- If he refused or skipped a calculation, verdict is no_attempt.\n' +
      '- "explain": only if the verdict is not right. Explain from zero the one fundamental behind his biggest gap, anchored on a concrete physical picture of his own motor (a slot, a magnet, the air gap, the copper, a number from the facts). Max 110 words. Do not just restate the key.\n' +
      '- "redo": one concrete instruction for a second try, e.g. "Explain in 3 lines why X" or "Compute Y with your λm". Never give the answer in it. If right, ask for the same idea in 2 lines as he would say it in an interview.\n' +
      '- "error": if not right, one line of what he got wrong (his idea, in English) and one line of the correct fact. Otherwise null.\n\n' +
      'Reply ONLY with JSON:\n{"verdict":"right|partial|wrong|no_attempt","good":["..."],"wrong":["..."],"missing":["..."],"explain":"...","too_long":false,"redo":"...","error":{"said":"...","correct":"..."}}\n' +
      'good / wrong / missing: max 3 short items each, concrete, empty list if none. good says why it matters.';
  }
  function redoPrompt(q, lesson, first, fb, answer) {
    return ROLE + 'Facts about his motor:\n' + DATA.facts + '\n\nLesson: ' + lesson.title + '\nQuestion: ' + q.prompt_text +
      '\nKey:\n- ' + q.key.join('\n- ') + '\n\nHis first answer:\n"""\n' + first + '\n"""\nYou told him: ' + (fb.explain || '') + '\nAnd asked: ' + fb.redo +
      '\n\nHis second try (' + words(answer) + ' words):\n"""\n' + answer + '\n"""\n\n' +
      'Judge only the second try: did he now get the idea, in his own words? Repeating your words without the reasoning is partial.\n' +
      'Reply ONLY with JSON: {"verdict":"right|partial|wrong","comment":"max 2 sentences: what is now right and what is still missing","error":{"said":"...","correct":"..."}}  (error null if right)';
  }
  function reviewPrompt(err, answer) {
    return ROLE + 'Facts about his motor:\n' + DATA.facts + '\n\nThis is a spaced-repetition check of a mistake he made before.\nQuestion: ' + err.question +
      '\nThe correct idea: ' + err.correct + '\nWhat he got wrong last time: ' + err.said +
      '\n\nHis answer now:\n"""\n' + answer + '\n"""\n\nReply ONLY with JSON: {"verdict":"right|partial|wrong","comment":"max 3 sentences, concrete; if not right, explain the fundamental briefly on his motor"}';
  }
  function doubtPrompt(lesson, text) {
    return ROLE + 'Facts about his motor:\n' + DATA.facts + '\n\nAfter the lesson "' + lesson.title + '" he wrote what he still does not understand:\n"""\n' + text +
      '\n"""\n\nFind the real doubt inside it (he may ramble). Explain it from first principles, anchored on his motor, in max 160 words, with one number from the facts. End with one question he should be able to answer if he understood.\n' +
      'Reply ONLY with JSON: {"doubt":"the doubt in one line","answer":"...","check":"..."}';
  }
  function errText(e) {
    const c = e && e.code;
    if (c === 'not_granted') return 'Claude may not grade on this page. Allow it in the page permissions, or the answer waits for Sunday.';
    if (c === 'rate_limited') return 'Too many gradings in a row. Wait a minute and press again.';
    if (c === 'invalid_json') return 'The grading came back malformed. Press again.';
    return 'Grading failed just now. Press again; the answer is saved.';
  }

  // ---------- errors (spaced repetition) ----------
  async function recordError(lesson, qid, q, err, verdict) {
    const id = lesson.id + '-' + qid;
    const prev = errors[id];
    const doc = Object.assign({}, prev || {}, {
      lesson: lesson.id, q: qid, topic: lesson.title, question: q.prompt_text,
      said: (err && err.said) || (prev && prev.said) || '', correct: (err && err.correct) || (prev && prev.correct) || q.key.join('; '),
      status: 'red', hits: 0, lastHit: null, due: day(1), verdict, updated: new Date().toISOString(), created: (prev && prev.created) || new Date().toISOString()
    });
    errors[id] = doc; await save('errors/' + id, doc); updateBadge();
  }
  const dueList = () => Object.entries(errors).filter(([, e]) => e.status !== 'green' && (!e.due || e.due <= day())).sort((a, b) => (a[1].due || '').localeCompare(b[1].due || ''));
  function updateBadge() { const n = dueList().length, b = document.getElementById('due-badge'); b.hidden = !n; b.textContent = n; }

  // ---------- question widget ----------
  function renderFeedback(fb) {
    const box = el('div', { class: 'turn grader' }, [el('span', { class: 'who', text: 'Claude' }), el('span', { class: 'verdict ' + fb.verdict, text: VERDICT[fb.verdict] || fb.verdict })]);
    const list = el('ul', { class: 'fb-list' });
    (fb.good || []).forEach(t => list.append(el('li', {}, [el('b', { text: '✓' }), el('span', { text: t })])));
    (fb.wrong || []).forEach(t => list.append(el('li', {}, [el('b', { text: '✗' }), el('span', { text: t })])));
    (fb.missing || []).forEach(t => list.append(el('li', {}, [el('b', { text: '?' }), el('span', { text: t })])));
    if (list.children.length) box.append(list);
    if (fb.too_long) box.append(el('p', { text: 'Too long. In an interview you get 30 seconds: one idea, one number, one reason.' }));
    if (fb.explain) box.append(el('div', { class: 'explain' }, [el('span', { class: 'lbl', text: 'The fundamental' }), el('span', { text: fb.explain })]));
    if (fb.comment) box.append(el('p', { text: fb.comment }));
    if (fb.redo) box.append(el('p', { class: 'redo', text: '→ ' + fb.redo }));
    return box;
  }
  const mineTurn = (text, label) => el('div', { class: 'turn mine-t' }, [el('span', { class: 'who', text: label || 'You' }), el('span', { class: 'txt', text: text })]);
  const thinking = () => el('div', { class: 'thinking' }, [el('i'), el('span', { text: 'Claude is reading your answer…' })]);

  function mountQuestion(box, lesson) {
    const qid = box.dataset.q, q = lesson.questions[qid], id = lesson.id + '-' + qid;
    if (!q) { box.textContent = 'Missing question ' + qid; return; }
    const KIND = { predict: 'Predict first', check: 'Check', lab: 'Lab', case: 'Case', error: 'Find the error', calc: 'Calculate', explain: 'Explain aloud', recall: 'From last lesson', doubt: 'What you still don\'t get' };
    function draw() {
      const a = attempts[id];
      box.innerHTML = '';
      box.append(el('div', { class: 'qtag' }, [el('span', { text: KIND[q.kind] || 'Question' }), a && a.final ? el('span', { class: 'verdict ' + a.final, text: VERDICT[a.final] }) : null]));
      box.append(el('div', { class: 'prompt', html: q.prompt }));
      if (q.kind === 'doubt') return drawDoubt();
      const turns = (a && a.turns) || [];
      turns.forEach(t => box.append(t.role === 'pol' ? mineTurn(t.text, t.n === 2 ? 'You, second try' : 'You') : renderFeedback(t.fb)));
      const stage = !a ? 'first' : a.stage;
      if (stage === 'first' || stage === 'redo') input(stage);
      if (stage === 'done' || stage === 'saved') showSolution();
      if (stage === 'done' || stage === 'saved') box.append(el('div', { class: 'row' }, [el('button', { type: 'button', class: 'btn ghost small', text: 'Try again from zero', onclick: restart })]));
    }
    function input(stage) {
      const key = 'draft:' + id + ':' + stage;
      const ta = el('textarea', { id: 'ta-' + id + '-' + stage, placeholder: stage === 'first' ? 'Your attempt, with your reasoning. "I don\'t know, but I think…" is fine. Dictation works.' : 'Second try, in your own words. Short.' });
      ta.value = store.get(key) || '';
      const btn = el('button', { type: 'button', class: 'btn', text: stage === 'first' ? 'Check my answer' : 'Check my second try' });
      const hint = el('span', { class: 'hint' });
      const sync = () => { const n = words(ta.value); btn.disabled = n < 3; hint.textContent = n < 3 ? 'Write an attempt first' : n + ' words' + (n > 150 ? ' · long: one idea, one number' : ''); };
      ta.addEventListener('input', () => { sync(); store.set(key, ta.value); });
      btn.addEventListener('click', () => submit(stage, ta.value.trim()));
      box.append(ta, el('div', { class: 'row' }, [btn, hint]));
      if (stage === 'redo') box.append(el('div', { class: 'row' }, [el('button', { type: 'button', class: 'btn ghost small', text: 'Skip the second try and see the solution', onclick: () => finish(attempts[id].turns[1].fb.verdict) })]));
      sync();
    }
    function showSolution() { if (q.solution) box.append(el('div', { class: 'solution' }, [el('span', { class: 'lbl', text: 'Reference solution' }), el('div', { html: q.solution })])); }
    async function submit(stage, text) {
      const a = attempts[id] || { lesson: lesson.id, q: qid, question: q.prompt_text, turns: [], history: [] };
      a.turns.push({ role: 'pol', n: stage === 'first' ? 1 : 2, text, at: new Date().toISOString() });
      attempts[id] = a;
      if (!sample) { a.stage = 'saved'; a.final = 'saved'; await save('attempts/' + id, a); draw(); return; }
      a.stage = 'thinking'; draw(); box.append(thinking());
      try {
        const fb = stage === 'first' ? await sample.json(gradePrompt(q, lesson, text), { modelTier: 'default' })
          : await sample.json(redoPrompt(q, lesson, a.turns[0].text, a.turns[1].fb, text), { modelTier: 'default' });
        fb.verdict = VERDICT[fb.verdict] ? fb.verdict : 'partial';
        a.turns.push({ role: 'claude', fb, at: new Date().toISOString() });
        if (stage === 'first') {
          a.first = fb.verdict;
          if (fb.verdict !== 'right') await recordError(lesson, qid, q, fb.error, fb.verdict);
          a.stage = 'redo';
        } else {
          if (fb.verdict !== 'right' && fb.error) await recordError(lesson, qid, q, fb.error, fb.verdict);
          a.final = fb.verdict; a.stage = 'done';
        }
        store.set('draft:' + id + ':' + stage, '');
        await save('attempts/' + id, a); draw();
      } catch (e) {
        a.turns.pop(); a.stage = stage; draw(); box.append(el('p', { class: 'err', text: errText(e) }));
      }
    }
    async function finish(v) { const a = attempts[id]; a.final = v; a.stage = 'done'; await save('attempts/' + id, a); draw(); }
    async function restart() { const a = attempts[id]; a.history = (a.history || []).concat([{ turns: a.turns, final: a.final }]).slice(-3); a.turns = []; a.final = null; a.stage = 'first'; await save('attempts/' + id, a); draw(); }
    function drawDoubt() {
      const mine = doubts.filter(d => d.lesson === lesson.id);
      mine.forEach(d => { box.append(mineTurn(d.text)); if (d.answer) box.append(renderFeedback({ verdict: 'saved', explain: d.answer, redo: d.check })); });
      const ta = el('textarea', { id: 'ta-' + id, placeholder: 'Write it as it is. Claude explains it now, and it goes to the "what I don\'t get" slide of the review.' });
      const btn = el('button', { type: 'button', class: 'btn', text: 'Explain it to me' });
      btn.addEventListener('click', async () => {
        const text = ta.value.trim(); if (words(text) < 3) return;
        const d = { lesson: lesson.id, text, at: new Date().toISOString() };
        box.append(thinking());
        if (sample) { try { const r = await sample.json(doubtPrompt(lesson, text), { modelTier: 'default' }); d.doubt = r.doubt; d.answer = r.answer; d.check = r.check; } catch (e) { d.error = String(e && e.code || e); } }
        doubts.push(d); await save('doubts/' + lesson.id + '-' + Date.now(), d); draw();
      });
      box.append(ta, el('div', { class: 'row' }, [btn]));
    }
    draw();
  }

  // ---------- views ----------
  function lessonProgress(l) {
    const ids = Object.keys(l.questions).filter(k => l.questions[k].kind !== 'doubt');
    const done = ids.filter(k => attempts[l.id + '-' + k] && attempts[l.id + '-' + k].turns && attempts[l.id + '-' + k].turns.length).length;
    return { done, total: ids.length };
  }
  function todayLesson() {
    const t = day(), sorted = LESSONS.slice().sort((a, b) => a.date.localeCompare(b.date));
    return sorted.find(l => l.date === t) || sorted.filter(l => l.date <= t).find(l => { const p = lessonProgress(l); return p.done < p.total; }) || sorted.filter(l => l.date <= t).pop() || sorted[0];
  }
  function showLesson(l, intro) {
    view.innerHTML = '';
    const wrap = el('div', { class: 'lesson' });
    const p = lessonProgress(l);
    const head = el('div', { class: 'lesson-head' }, [
      el('p', { class: 'eyebrow', text: (intro || 'Lesson') + ' · ' + (l.cycle || '') + ' · ' + l.date }),
      el('h1', { text: l.title }),
      l.lede ? el('p', { class: 'lede', text: l.lede }) : null,
      el('div', { class: 'meta' }, [el('span', { text: (l.minutes || 55) + ' min' }), el('span', { text: p.done + ' / ' + p.total + ' answered' }), l.sources ? el('span', { text: l.sources }) : null])
    ]);
    wrap.append(head);
    const grid = el('div', { class: 'lesson-grid' + (l.hasScene ? ' with-motor' : '') });
    const col = el('div', { class: 'col', html: l.html });
    if (l.hasScene) { const side = el('div', { class: 'side', html: Motor3D.panelHTML() }); grid.append(side, col); } else grid.append(col);
    const toc = el('nav', { class: 'toc', 'aria-label': 'Lesson parts' });
    col.querySelectorAll('section.sec').forEach(s => toc.append(el('a', { href: '#' + l.id, text: s.querySelector('h2').textContent, onclick: e => { e.preventDefault(); s.scrollIntoView({ behavior: 'smooth', block: 'start' }); } })));
    head.append(toc);
    wrap.append(grid);
    view.append(wrap);
    motor = l.hasScene ? Motor3D.mount(grid.querySelector('.motor')) : null;
    col.querySelectorAll('.qa').forEach(b => mountQuestion(b, l));
    col.querySelectorAll('.labbox').forEach(b => Labs.mount(b));
    // presets: button press anywhere; on wide screens also when the idea scrolls into view
    const refs = [...col.querySelectorAll('.scene-ref')];
    refs.forEach(r => r.querySelector('.show-scene').addEventListener('click', () => {
      if (!motor) return; motor.preset(JSON.parse(r.dataset.scene)); mark(r);
      if (!matchMedia('(min-width:1080px)').matches) grid.querySelector('.motor').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
    function mark(r) { col.querySelectorAll('.idea.live').forEach(i => i.classList.remove('live')); const idea = r.closest('.idea'); if (idea) idea.classList.add('live'); }
    if (motor && refs.length) {
      motor.preset(JSON.parse(refs[0].dataset.scene));
      const io = new IntersectionObserver(es => {
        if (!matchMedia('(min-width:1080px)').matches) return;
        es.filter(e => e.isIntersecting).forEach(e => { motor.preset(JSON.parse(e.target.dataset.scene)); mark(e.target); });
      }, { rootMargin: '-35% 0px -55% 0px' });
      refs.forEach(r => io.observe(r.closest('.idea') ? r : r));
    }
  }
  function showToday() {
    const l = todayLesson(), n = dueList().length;
    showLesson(l, 'Today');
    if (n) {
      const due = el('div', { class: 'due' }, [el('div', {}, [el('b', { text: n + (n === 1 ? ' mistake' : ' mistakes') + ' to re-answer' }), el('p', { text: 'About ' + Math.max(5, n * 2) + ' minutes. Do them before the lesson: recalling costs more than rereading, and that is why it sticks.' })]), el('a', { class: 'btn', href: '#review', text: 'Open review' })]);
      view.querySelector('.lesson-head').append(due);
    }
  }
  function showReview() {
    view.innerHTML = '';
    const page = el('div', { class: 'page' });
    page.append(el('div', { class: 'lesson-head' }, [el('p', { class: 'eyebrow', text: 'Review' }), el('h1', { text: 'Your mistakes, again' }), el('p', { class: 'lede', text: 'Every mistake comes back until you get it right on two different days. No answers shown first: try, then Claude grades.' })]));
    const due = dueList();
    if (!ready) page.append(el('p', { class: 'empty', text: 'Loading your mistakes…' }));
    else if (!db) page.append(el('p', { class: 'empty', text: 'Your mistakes live in this page\'s database, which is not available in this view. Open the page signed in to claude.ai.' }));
    else if (!due.length) page.append(el('p', { class: 'empty', text: 'Nothing due today. New mistakes from a lesson come back the next day.' }));
    const list = el('div', { class: 'list' });
    due.forEach(([id, e]) => list.append(reviewCard(id, e)));
    page.append(list);
    const later = Object.values(errors).filter(e => e.status !== 'green' && e.due > day()).length, closed = Object.values(errors).filter(e => e.status === 'green').length;
    if (ready && db) page.append(el('p', { class: 'meta', text: later + ' coming back later · ' + closed + ' closed' }));
    if (doubts.length) {
      page.append(el('h2', { text: 'What you said you don\'t get' }));
      doubts.slice().reverse().slice(0, 8).forEach(d => page.append(el('div', { class: 'card doubt' }, [el('span', { class: 'eyebrow', text: d.lesson }), el('p', { class: 'q', text: d.doubt || d.text }), d.answer ? el('p', { text: d.answer }) : el('p', { class: 'meta', text: 'Not answered yet' })])));
    }
    view.append(page);
  }
  function reviewCard(id, e) {
    const card = el('div', { class: 'qa' });
    function draw(res) {
      card.innerHTML = '';
      card.append(el('div', { class: 'qtag' }, [el('span', { text: e.topic || e.lesson }), el('span', { class: 'status ' + e.status, text: e.status === 'red' ? 'open' : e.status === 'yellow' ? 'right once' : 'closed' })]));
      card.append(el('p', { class: 'prompt', text: e.question }));
      if (res) { card.append(mineTurn(res.text), renderFeedback(res.fb)); if (res.fb.verdict !== 'right') card.append(el('div', { class: 'solution' }, [el('span', { class: 'lbl', text: 'The correct idea' }), el('p', { text: e.correct })])); return; }
      const ta = el('textarea', { id: 'rv-' + id, placeholder: 'From memory. Short.' }), btn = el('button', { type: 'button', class: 'btn', text: 'Check' });
      btn.addEventListener('click', async () => {
        const text = ta.value.trim(); if (words(text) < 3) return;
        if (!sample) { card.append(el('p', { class: 'err', text: 'Claude cannot grade in this view. Try again signed in.' })); return; }
        card.append(thinking());
        try {
          const fb = await sample.json(reviewPrompt(e, text), { modelTier: 'default' });
          fb.verdict = VERDICT[fb.verdict] ? fb.verdict : 'partial';
          const t = day();
          if (fb.verdict === 'right') { if (e.lastHit !== t) { e.hits = (e.hits || 0) + 1; e.lastHit = t; } e.status = e.hits >= 2 ? 'green' : 'yellow'; e.due = e.hits >= 2 ? null : day(3); }
          else if (fb.verdict === 'partial') e.due = day(1);
          else { e.status = 'red'; e.hits = 0; e.due = day(1); }
          e.log = (e.log || []).concat([{ at: new Date().toISOString(), text, verdict: fb.verdict }]).slice(-6);
          await save('errors/' + id, e); updateBadge(); draw({ text, fb });
        } catch (err) { card.querySelector('.thinking')?.remove(); card.append(el('p', { class: 'err', text: errText(err) })); }
      });
      card.append(ta, el('div', { class: 'row' }, [btn]));
    }
    draw(); return card;
  }
  function showLessons() {
    view.innerHTML = '';
    const page = el('div', { class: 'page' });
    page.append(el('div', { class: 'lesson-head' }, [el('p', { class: 'eyebrow', text: 'All lessons' }), el('h1', { text: 'Lessons' })]));
    const list = el('div', { class: 'list' });
    LESSONS.slice().sort((a, b) => b.date.localeCompare(a.date)).forEach(l => {
      const p = lessonProgress(l), open = Object.values(errors).filter(e => e.lesson === l.id && e.status !== 'green').length;
      list.append(el('a', { class: 'lrow', href: '#' + l.id }, [el('span', { class: 't', text: l.title }), el('span', { class: 'p', text: p.done + '/' + p.total }), el('span', { class: 'm', text: (l.cycle || '') + ' · ' + l.date + (open ? ' · ' + open + ' open mistakes' : '') })]));
    });
    page.append(list); view.append(page);
  }

  function route() {
    const h = (location.hash || '#today').slice(1);
    document.querySelectorAll('.tabs a').forEach(a => a.toggleAttribute('aria-current', false));
    const lesson = LESSONS.find(l => l.id === h);
    const tab = lesson ? 'lessons' : ['today', 'review', 'lessons'].includes(h) ? h : 'today';
    document.querySelector('.tabs a[data-tab="' + tab + '"]').setAttribute('aria-current', 'page');
    if (lesson) showLesson(lesson); else if (tab === 'review') showReview(); else if (tab === 'lessons') showLessons(); else showToday();
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route);

  // ---------- boot ----------
  route();
  (async () => {
    const c = window.claude;
    if (c && c.use) {
      try { db = await c.use('db'); } catch (e) { db = null; }
      try { sample = await c.use('sample'); } catch (e) { sample = null; }
    }
    if (db) {
      const timer = new Promise(r => setTimeout(r, 10000));
      const load = Promise.all([
        db.collection('attempts').get().then(s => s.docs.forEach(d => attempts[d.id] = d.data())),
        db.collection('errors').get().then(s => s.docs.forEach(d => errors[d.id] = d.data())),
        db.collection('doubts').get().then(s => s.docs.forEach(d => doubts.push(d.data()))),
      ]).catch(e => console.warn('load failed', e));
      await Promise.race([load, timer]);
      doubts.sort((a, b) => (a.at || '').localeCompare(b.at || ''));
    }
    ready = true; updateBadge();
    // redraw with the loaded state unless Pol is already typing
    const typing = document.activeElement && document.activeElement.tagName === 'TEXTAREA' && document.activeElement.value;
    if (!typing) { const y = window.scrollY; route(); window.scrollTo(0, y); }
  })();
})();
