// Turns odys-figma.html into one SVG per frame, for Figma's SVG import (the connector's upload_assets), which keeps
// text as text layers. Each phone, panel, section heading and note becomes its own SVG, named for its Figma layer.
// What SVG can't carry (font weight, letter spacing, wrapping width, shadows) rides in each element's id, and
// figma_fix.js applies it inside Figma.
//
// Run: NODE_PATH=$(npm root -g) node design/figma/to_svg.js design/figma/odys-figma.html <out-dir>
// Writes <out-dir>/units.json: [{file, name, x, y, w, h}] and one .svg per unit.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [, , src, outDir] = process.argv;
  fs.mkdirSync(outDir, { recursive: true });
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1600, height: 1000 } });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(src), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  const units = await page.evaluate(() => {
    const r1 = v => Math.round(v * 10) / 10;
    const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    const canvas = document.createElement('canvas').getContext('2d');
    let uid = 0;

    function color(s) {
      const m = s && s.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
      const a = p.length > 3 ? p[3] : 1;
      if (a === 0) return null;
      const hex = '#' + p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
      return { hex, a: r1(a * 100) / 100 };
    }
    const paint = (c, attr) => c ? `${attr}="${c.hex}"` + (c.a < 1 ? ` ${attr}-opacity="${c.a}"` : '') : `${attr}="none"`;

    function splitTop(s) {   // split on commas outside parentheses
      const out = []; let depth = 0, cur = '';
      for (const ch of s) {
        if (ch === '(') depth++;
        if (ch === ')') depth--;
        if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; } else cur += ch;
      }
      if (cur.trim()) out.push(cur.trim());
      return out;
    }

    // a CSS gradient as an SVG gradient in defs; returns the fill reference
    function gradient(img, box, defs) {
      const m = img.match(/^(linear|radial)-gradient\((.*)\)$/s);
      if (!m) return null;
      const parts = splitTop(m[2]);
      let shape = null;
      if (!/^rgb|^#|^transparent/.test(parts[0])) shape = parts.shift();
      const stops = parts.map(p => {
        const cm = p.match(/(rgba?\([^)]+\))\s*([-\d.]+(px|%))?/);
        const c = color(cm[1]);
        let pos = null;
        if (cm[2]) pos = cm[3] === '%' ? parseFloat(cm[2]) / 100 : parseFloat(cm[2]);
        return { c: c || { hex: '#000000', a: 0 }, pos, px: cm[3] === 'px' };
      });
      const id = 'g' + (++uid);
      if (m[1] === 'linear') {
        const len = box.h;
        stops.forEach((s, i) => { if (s.pos === null) s.pos = i / Math.max(stops.length - 1, 1); else if (s.px) s.pos = s.pos / len; });
        defs.push(`<linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">` + stops.map(s => `<stop offset="${r1(Math.min(Math.max(s.pos, 0), 1) * 1000) / 1000}" stop-color="${s.c.hex}" stop-opacity="${s.c.a}"/>`).join('') + '</linearGradient>');
      } else {
        let cx = 0.5, cy = 0.5;
        const at = shape && shape.match(/at ([\d.]+)% ([\d.]+)%/);
        if (at) { cx = parseFloat(at[1]) / 100; cy = parseFloat(at[2]) / 100; }
        const X = box.x + cx * box.w, Y = box.y + cy * box.h;
        const R = Math.max(...[[box.x, box.y], [box.x + box.w, box.y], [box.x, box.y + box.h], [box.x + box.w, box.y + box.h]].map(([a, b]) => Math.hypot(a - X, b - Y)));
        stops.forEach((s, i) => { if (s.pos === null) s.pos = i / Math.max(stops.length - 1, 1); else if (s.px) s.pos = s.pos / R; });
        defs.push(`<radialGradient id="${id}" gradientUnits="userSpaceOnUse" cx="${r1(X)}" cy="${r1(Y)}" r="${r1(R)}">` + stops.map(s => `<stop offset="${r1(Math.min(Math.max(s.pos, 0), 1) * 1000) / 1000}" stop-color="${s.c.hex}" stop-opacity="${s.c.a}"/>`).join('') + '</radialGradient>');
      }
      return `url(#${id})`;
    }

    function shadowCode(cs) {
      if (!cs.boxShadow || cs.boxShadow === 'none') return '';
      const c = color(cs.boxShadow);
      const nums = cs.boxShadow.replace(/rgba?\([^)]+\)/, '').trim().split(/\s+/).map(parseFloat);
      return c ? `~sh${nums[0]}_${nums[1]}_${nums[2]}_${c.hex.slice(1)}_${Math.round(c.a * 100)}` : '';
    }

    const NAMES = { 'btn-p': 'Button primary', 'btn-s': 'Button secondary', 'btn-d': 'Button 999', 'btn-e': 'Button 111',
      card: 'Card', chip: 'Chip', pill: 'Help', circ: 'Icon button', close: 'Close', tile: 'Tile', opt: 'Option',
      stat: 'Stat', thumb: 'Photo', badge: 'Number', num: 'Stop number', tag: 'Tag', emerg: 'Emergency', field: 'Field',
      seg: 'Segmented', island: 'Dynamic Island', track: 'Progress', fill: 'Progress fill', hair: 'Divider',
      phone: 'Background', panel: 'Panel', 'chip-c': 'Swatch', homebar: 'Home bar', dot: 'Dot', ringdot: 'Dot', rail: 'Rail' };
    const nameOf = el => { for (const c of el.classList) if (NAMES[c]) return NAMES[c]; return 'Shape'; };

    // the text of a leaf element, line by line, from the rendered characters
    function lines(el) {
      const out = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      const rng = document.createRange();
      let node, hardNext = false;
      const brs = new Set(el.querySelectorAll('br'));
      let cur = null;
      const all = [];
      while ((node = walker.nextNode())) all.push(node);
      for (const tn of all) {
        // a <br> before this text node starts a hard line
        let prev = tn.previousSibling;
        if (prev && prev.nodeName === 'BR') hardNext = true;
        const txt = tn.textContent;
        for (let i = 0; i < txt.length; i++) {
          rng.setStart(tn, i); rng.setEnd(tn, i + 1);
          const rects = rng.getClientRects();
          if (!rects.length) continue;
          const r = rects[0];
          let ch = txt[i];
          if (/\s/.test(ch)) { if (r.width < 0.5) continue; ch = ' '; }
          if (!cur || Math.abs(r.top - cur.top) > 3) {
            cur = { top: r.top, h: r.height, left: r.left, text: '', hard: hardNext && out.length > 0 };
            hardNext = false;
            out.push(cur);
          }
          if (ch === ' ' && (cur.text === '' || cur.text.endsWith(' '))) continue;
          cur.text += ch;
        }
      }
      return out.map(l => ({ ...l, text: l.text.trimEnd() })).filter(l => l.text);
    }

    function textSVG(el, styleEl, ox, oy, items, defs) {
      const ls = lines(el);
      if (!ls.length) return;
      const cs = getComputedStyle(styleEl);
      const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
      const size = parseFloat(cs.fontSize);
      const weight = parseInt(cs.fontWeight, 10) || 400;
      const italic = cs.fontStyle === 'italic' ? 1 : 0;
      const lh = cs.lineHeight === 'normal' ? 0 : parseFloat(cs.lineHeight);
      const lsp = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing);
      const upper = cs.textTransform === 'uppercase';
      canvas.font = `${italic ? 'italic ' : ''}${weight} ${size}px "${fam}"`;
      const m = canvas.measureText('Hg');
      const asc = m.fontBoundingBoxAscent;
      const c = color(cs.color) || { hex: '#000000', a: 1 };
      const box = el.getBoundingClientRect();
      const ecs = getComputedStyle(el);
      const cl = box.left + parseFloat(ecs.paddingLeft) + parseFloat(ecs.borderLeftWidth);
      const cw = box.width - parseFloat(ecs.paddingLeft) - parseFloat(ecs.paddingRight) - parseFloat(ecs.borderLeftWidth) - parseFloat(ecs.borderRightWidth);
      const al = ecs.textAlign === 'center' ? 'C' : ecs.textAlign === 'right' || ecs.textAlign === 'end' ? 'R' : 'L';
      const L = lh || ls[0].h;
      const top = ls[0].top - (L - ls[0].h) / 2;
      const multi = ls.length > 1;
      const id = `P~${++uid}~x${r1(multi ? cl - ox : ls[0].left - ox)}~y${r1(top - oy)}~w${multi ? r1(cw) : 0}~a${al}~l${r1(lh)}~f${weight}~i${italic}~s${r1(lsp)}`;
      const spans = ls.map((l, k) => `<tspan id="L~${uid}_${k}~${l.hard ? 'h' : 's'}" x="${r1(l.left - ox)}" y="${r1(l.top + asc - oy)}">${esc(upper ? l.text.toUpperCase() : l.text)}</tspan>`).join('');
      items.push(`<text id="${id}" font-family="${fam}" font-size="${size}" font-weight="${weight}"${italic ? ' font-style="italic"' : ''} ${paint(c, 'fill')}>${spans}</text>`);
    }

    function inlineSVG(svg, ox, oy, items) {
      const r = svg.getBoundingClientRect();
      const clone = svg.cloneNode(true);
      const vb = (svg.getAttribute('viewBox') || `0 0 ${r.width} ${r.height}`).split(/[ ,]+/).map(Number);
      const sx = r.width / vb[2], sy = r.height / vb[3];
      const pre = 'n' + (++uid) + '_';
      // texts drawn centred on a point: move them to their left edge (Figma ignores text-anchor)
      const origTexts = svg.querySelectorAll('text');
      clone.querySelectorAll('text').forEach((t, i) => {
        const o = origTexts[i];
        if (t.getAttribute('text-anchor') === 'middle') {
          const bb = o.getBBox();
          t.setAttribute('x', r1(bb.x));
          t.removeAttribute('text-anchor');
        }
        const w = parseInt(t.getAttribute('font-weight') || '400', 10);
        t.setAttribute('id', `N~${++uid}~f${w}`);
        t.setAttribute('font-family', (t.getAttribute('font-family') || 'Inter').split(',')[0]);
      });
      clone.querySelectorAll('[id]').forEach(n => { if (!/^N~/.test(n.id)) n.id = pre + n.id; });
      let inner = clone.innerHTML.replace(/url\(#([^)]+)\)/g, `url(#${pre}$1)`).replace(/href="#([^"]+)"/g, `href="#${pre}$1"`);
      items.push(`<g id="Icon~${uid}" transform="translate(${r1(r.left - ox)} ${r1(r.top - oy)}) scale(${r1(sx * 1000) / 1000} ${r1(sy * 1000) / 1000})">${inner}</g>`);
    }

    function walk(el, ox, oy, items, defs, isRoot) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (el.tagName.toLowerCase() === 'svg') { inlineSVG(el, ox, oy, items); return; }
      const r = el.getBoundingClientRect();
      const box = { x: r1(r.left - ox), y: r1(r.top - oy), w: r1(r.width), h: r1(r.height) };
      const op = parseFloat(cs.opacity);
      let target = items;
      const group = [];
      if (op < 1) target = group;
      const bg = color(cs.backgroundColor);
      const img = cs.backgroundImage && cs.backgroundImage !== 'none' ? cs.backgroundImage : null;
      const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => parseFloat(cs['border' + s + 'Width']) || 0);
      const bc = ['Top', 'Right', 'Bottom', 'Left'].map(s => color(cs['border' + s + 'Color']));
      const rad = Math.min(parseFloat(cs.borderTopLeftRadius) || 0, box.w / 2, box.h / 2);
      const sh = shadowCode(cs);
      const name = nameOf(el);
      if ((bg || img || sh) && box.w > 0 && box.h > 0) {
        const rx = rad ? ` rx="${r1(rad)}"` : '';
        if (bg) target.push(`<rect id="${name}~${++uid}${sh}" x="${box.x}" y="${box.y}" width="${box.w}" height="${box.h}"${rx} ${paint(bg, 'fill')}/>`);
        if (img) {
          for (const layer of splitTop(img).reverse()) {
            const f = gradient(layer, box, defs);
            if (f) target.push(`<rect id="${name} gradient~${++uid}${bg ? '' : sh}" x="${box.x}" y="${box.y}" width="${box.w}" height="${box.h}"${rx} fill="${f}"/>`);
          }
        }
      }
      const uniform = bw.every(w => w === bw[0]) && bc.every(c => c && bc[0] && c.hex === bc[0].hex && c.a === bc[0].a);
      if (uniform && bw[0] > 0 && bc[0]) {
        const w = bw[0];
        target.push(`<rect id="${name} border~${++uid}" x="${r1(box.x + w / 2)}" y="${r1(box.y + w / 2)}" width="${r1(box.w - w)}" height="${r1(box.h - w)}"${rad ? ` rx="${r1(Math.max(rad - w / 2, 0))}"` : ''} fill="none" ${paint(bc[0], 'stroke')} stroke-width="${w}"/>`);
      } else {
        const sides = [[box.x, box.y, box.w, bw[0]], [box.x + box.w - bw[1], box.y, bw[1], box.h], [box.x, box.y + box.h - bw[2], box.w, bw[2]], [box.x, box.y, bw[3], box.h]];
        sides.forEach((s, i) => { if (bw[i] > 0 && bc[i]) target.push(`<rect id="Line~${++uid}" x="${r1(s[0])}" y="${r1(s[1])}" width="${r1(s[2])}" height="${r1(s[3])}" ${paint(bc[i], 'fill')}/>`); });
      }
      // text: a leaf (only inline, svg-free children) is one paragraph; otherwise each direct text run is its own
      const kids = [...el.children];
      const inlineOnly = kids.every(k => ['inline'].includes(getComputedStyle(k).display) && !k.querySelector('svg') && k.tagName.toLowerCase() !== 'svg');
      const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || (inlineOnly && kids.length && el.textContent.trim());
      if (hasText && inlineOnly) {
        const styleEl = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) ? el : kids.find(k => k.textContent.trim()) || el;
        textSVG(el, styleEl, ox, oy, target, defs);
      } else {
        for (const n of el.childNodes) {
          if (n.nodeType === 3 && n.textContent.trim()) {
            const span = document.createElement('span');
            n.parentNode.insertBefore(span, n); span.appendChild(n);
            textSVG(span, el, ox, oy, target, defs);
          } else if (n.nodeType === 1) {
            walk(n, ox, oy, target, defs, false);
          }
        }
      }
      if (op < 1 && group.length) items.push(`<g id="Faded~${++uid}" opacity="${op}">${group.join('')}</g>`);
    }

    function unit(el, name, kind) {
      const r = el.getBoundingClientRect();
      const items = [], defs = [];
      walk(el, r.left, r.top, items, defs, true);
      const W = r1(r.width), H = r1(r.height);
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${defs.join('')}</defs>${items.join('')}</svg>`;
      return { name, kind, x: r1(r.left - board.left), y: r1(r.top - board.top), w: W, h: H, svg };
    }

    const board = document.querySelector('.board').getBoundingClientRect();
    const out = [];
    document.querySelectorAll('.sec').forEach(sec => {
      const h = sec.querySelector('.sec-h');
      out.push(unit(h, '§ ' + h.querySelector('h2').textContent, 'heading'));
      sec.querySelectorAll(':scope > .panel, :scope > .row > .panel').forEach(p => {
        const t = p.querySelector('.ptitle');
        out.push(unit(p, (t ? t.textContent : 'Read me'), 'panel'));
      });
      sec.querySelectorAll('.shot').forEach(s => {
        const label = s.querySelector(':scope > .label').textContent;
        const note = s.querySelector(':scope > .note');
        if (note) out.push(unit(note, 'Note · ' + label, 'note'));
        const ph = s.querySelector(':scope > .phone');
        out.push(unit(ph, label, 'phone'));
      });
    });
    return out;
  });
  const meta = [];
  const seen = {};
  units.forEach((u, i) => {
    let base = u.name.replace(/[\/\\:*?"<>|]/g, '-');
    seen[base] = (seen[base] || 0) + 1;
    if (seen[base] > 1) base += ` (${seen[base]})`;
    const file = String(i).padStart(3, '0') + '.svg';
    fs.writeFileSync(path.join(outDir, file), u.svg);
    meta.push({ file, name: base, kind: u.kind, x: u.x, y: u.y, w: u.w, h: u.h, bytes: u.svg.length });
  });
  fs.writeFileSync(path.join(outDir, 'units.json'), JSON.stringify(meta, null, 1));
  console.log(units.length, 'units;', Math.round(meta.reduce((a, m) => a + m.bytes, 0) / 1024), 'KB');
  await browser.close();
})();
