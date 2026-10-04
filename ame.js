// Ame-chan player: shows sprite-sheet frames from window.AME clips.
// "all" mode deals every action once per round; picking an action in the menu loops just that one.
(() => {
  const A = window.AME;
  const el = document.querySelector('.ame');
  if (!A || !el) return;
  el.style.aspectRatio = `${A.cell[0]} / ${A.cell[1]}`;
  // fit inside the window at any size without distortion
  el.style.height = `min(100vh, calc(100vw * ${A.cell[1]} / ${A.cell[0]}))`;
  // Frames live in several sheets (one huge sheet is not drawn) and are painted on a canvas from images
  // decoded up front: swapping a CSS background between sheets showed an empty frame (flicker) while decoding.
  // The canvas keeps the cell's own size and gets a 1:1 copy; the browser scales the element once, like it did
  // the background. Sizing the bitmap to the window resampled twice (CanvasTTY zoom is invisible here) - blurry.
  const [cw, ch] = A.cell;
  const canvas = document.createElement('canvas');
  canvas.width = cw;
  canvas.height = ch;
  canvas.style.cssText = 'width:100%;height:100%;display:block';
  el.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  const sheets = A.sheets.map((s) => { const img = new Image(); img.src = s.file; return img; });
  const ready = Promise.all(sheets.map((img) => img.decode().catch(() => {})));
  const show = (i) => {
    const s = Math.floor(i / A.perSheet), local = i % A.perSheet, img = sheets[s];
    if (!img.complete || !img.naturalWidth) return;               // not decoded yet: keep the previous frame
    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, (local % A.cols) * cw, Math.floor(local / A.cols) * ch, cw, ch, 0, 0, cw, ch);
  };

  // switching the menu bumps the generation; a running clip notices and stops at the next frame
  let gen = 0;
  class Switched extends Error {}
  const sleep = (s, g) => new Promise((ok, fail) => {
    const check = setInterval(() => { if (g !== gen) { clearTimeout(t); clearInterval(check); fail(new Switched()); } }, 50);
    const t = setTimeout(() => { clearInterval(check); ok(); }, s * 1000);
  });
  const has = (name) => (A.clips[name] || []).length > 0;
  const chance = (p) => Math.random() < p;
  const play = async (name, g, times = 1, from = 0) => {
    const clip = (A.clips[name] || []).slice(from);
    for (let t = 0; t < times; t++) for (const [i, d] of clip) { show(i); await sleep(d, g); }
  };
  // an action with entry/exit frames: standing -> to-X -> X -> from-X -> standing
  const perform = async (name, g, times = 1) => {
    await play(`${name}:in`, g);
    await play(name, g, times);
    await play(`${name}:out`, g);
  };

  const LABELS = {
    all: 'All actions', idle: 'Idle', dance: 'Dance', energy: 'Energy drink', smoke: 'Smoke',
    laptop: 'Code', selfie: 'Selfie', phone: 'Phone', game: 'Game', snack: 'Snack',
    music: 'Music', plush: 'Hug a plush', rainbow: 'Rainbow', sleepy: 'Yawn', doze: 'Doze',
    look: 'Look around', wavecam: 'Wave at camera', alert: 'Call out', tuck: 'Fix hair', wave: 'Wave',
    sad: 'Sad',
  };
  // shuffle bag: every action plays once per round (dance twice), in random order, no repeats back to back
  const DECK = ['dance', 'dance', 'phone', 'selfie', 'look', 'energy', 'smoke', 'rainbow', 'wavecam',
    'sleepy', 'doze', 'alert', 'tuck', 'wave', 'game', 'snack', 'music', 'plush', 'laptop', 'sad'];
  // picked in the menu, an action enters once and then loops without going back to standing;
  // repeats start from this frame (energy: the can is already open, skip looking at it and opening it)
  const AGAIN = { energy: 2 };
  const shuffle = (list) => {
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [list[i], list[j]] = [list[j], list[i]];
    }
    return list;
  };
  const deal = (last) => {
    const deck = shuffle(DECK.filter(has));
    for (let i = 1; i < deck.length; i++) {            // separate identical neighbours
      if (deck[i] === deck[i - 1]) {
        const k = deck.findIndex((n, j) => j > i && n !== deck[i]);
        if (k > 0) [deck[i], deck[k]] = [deck[k], deck[i]];
      }
    }
    if (deck[0] === last && deck.length > 1) deck.push(deck.shift());
    return deck;
  };

  // menu: "all", "idle" and every action that has frames
  let mode = 'all';
  const select = document.getElementById('mode');
  if (select) {
    const names = ['all', 'idle', ...new Set(DECK.filter(has))];
    for (const n of names) select.add(new Option(LABELS[n] || n, n));
    select.addEventListener('change', () => { mode = select.value; gen++; });
  }

  const step = async (g, last) => {
    if (!has('idle')) { await play('dance', g); return last; }   // no idle frames: dance non-stop
    if (mode === 'idle') { await play('idle', g); return last; }
    if (mode !== 'all') {
      await play(`${mode}:in`, g);                               // enter once, then loop until the menu changes
      await play(mode, g);
      for (;;) await play(mode, g, 1, AGAIN[mode] || 0);
    }
    const deck = deal(last);
    if (!deck.length) { await play('idle', g); return last; }   // nothing to deal: keep breathing
    for (const action of deck) {
      await play('idle', g, chance(0.6) ? 1 : 2);                // short pause: one or two breaths
      await perform(action, g, action === 'dance' ? 2 : 1);
      if (action === 'dance' && has('cheer') && chance(0.35)) await perform('cheer', g);
      last = action;
    }
    return last;
  };

  (async () => {
    await ready;                                                 // start only when every sheet is decoded
    let lastAction = '';
    for (;;) {
      try { lastAction = await step(gen, lastAction); }
      catch (e) { if (!(e instanceof Switched)) throw e; }       // menu changed: start the new mode at once
    }
  })();
})();
