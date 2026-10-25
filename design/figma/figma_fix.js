// Runs inside Figma (the connector's use_figma) after to_svg.js's SVGs are uploaded. It reads what each layer's name
// carries and makes the import editable: lines of a paragraph become one wrapping text box, with the right weight,
// letter spacing, line height and alignment; shadows go back on; the codes come off the layer names.
// Set FIX to the uploaded frames' node ids (at most ~26 a call keeps each call quick).
const FIX = [];
const W = { Inter: { 400: 'Regular', 500: 'Medium', 600: 'Semi Bold', 700: 'Bold' },
  Newsreader: { 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold' } };
const loaded = new Set();
async function font(fam, w, it) {
  const fm = W[fam] ? fam : 'Inter';
  let s = W[fm][w] || 'Regular';
  if (it) s = s === 'Regular' ? 'Italic' : s + ' Italic';
  const f = { family: fm, style: s };
  if (!loaded.has(fm + '/' + s)) { await figma.loadFontAsync(f); loaded.add(fm + '/' + s); }
  return f;
}
function meta(name) {
  const o = {};
  name.split('~').slice(2).forEach(p => { if (p.startsWith('sh')) o.sh = p.slice(2); else o[p[0]] = p.slice(1); });
  return o;
}
let texts = 0, merged = 0, shadows = 0;
const errs = [];
async function fixP(n) {
  const m = meta(n.name);
  const x = +m.x, y = +m.y, w = +m.w, lh = +m.l, wt = +m.f || 400, it = m.i === '1', ls = +m.s || 0;
  const al = m.a === 'C' ? 'CENTER' : m.a === 'R' ? 'RIGHT' : 'LEFT';
  const lines = n.type === 'TEXT' ? [n] : n.findAllWithCriteria({ types: ['TEXT'] });
  if (!lines.length) return;
  lines.sort((a, b) => (a.y - b.y) || (a.x - b.x));
  const fam = lines[0].fontName === figma.mixed ? 'Inter' : lines[0].fontName.family;
  const f = await font(fam, wt, it);
  let t;
  if (n.type === 'TEXT') {
    t = n;
    if (t.fontName !== figma.mixed) await figma.loadFontAsync(t.fontName);
  } else {
    let s = '';
    lines.forEach((k, i) => { if (i) s += /~h$/.test(k.name) ? '\n' : ' '; s += k.characters; });
    t = figma.createText();
    t.fontName = f; t.characters = s; t.fontSize = lines[0].fontSize; t.fills = lines[0].fills;
    const p = n.parent;
    p.insertChild(p.children.indexOf(n), t);
    n.remove();
    merged++;
  }
  t.fontName = f;
  if (lh) t.lineHeight = { unit: 'PIXELS', value: lh };
  t.letterSpacing = { unit: 'PIXELS', value: ls };
  t.textAlignHorizontal = al;
  if (w > 0) { t.textAutoResize = 'HEIGHT'; t.resize(w + 2, Math.max(t.height, 1)); } else t.textAutoResize = 'WIDTH_AND_HEIGHT';
  t.x = x; t.y = y; t.autoRename = true;
  texts++;
}
async function fixFrame(root) {
  for (const n of root.findAll(n => n.name.startsWith('P~'))) {
    try { await fixP(n); } catch (e) { errs.push(root.name + ': ' + String(e).slice(0, 120)); }
  }
  for (const t of root.findAll(n => n.type === 'TEXT' && n.name.startsWith('N~'))) {
    if (t.fontName === figma.mixed) continue;
    await figma.loadFontAsync(t.fontName);
    t.fontName = await font(t.fontName.family, +meta(t.name).f || 400, false);
    t.autoRename = true;
  }
  for (const n of root.findAll(n => n.name.includes('~'))) {
    if (n.type === 'TEXT') continue;
    const m = meta(n.name);
    if (m.sh && 'effects' in n) {
      const [dx, dy, b, hex, a] = m.sh.split('_');
      const v = parseInt(hex, 16);
      n.effects = [{ type: 'DROP_SHADOW', color: { r: (v >> 16 & 255) / 255, g: (v >> 8 & 255) / 255, b: (v & 255) / 255, a: +a / 100 },
        offset: { x: +dx, y: +dy }, radius: +b, spread: 0, visible: true, blendMode: 'NORMAL' }];
      shadows++;
    }
    n.name = n.name.split('~')[0];
  }
}
for (const id of FIX) { const r = await figma.getNodeByIdAsync(id); if (r) await fixFrame(r); }
return { texts, merged, shadows, errs: errs.slice(0, 10), nErr: errs.length };
