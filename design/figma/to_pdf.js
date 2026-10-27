// Prints a board page (odys-figma.html, or the screenshot board's index.html) to a PDF to share with people or other
// AI models. Each section starts on a new page with its title; phones and panels are packed into rows that fit the
// page, never split, and every later page of a section repeats its title. Text stays text.
// Run: NODE_PATH=$(npm root -g) node design/figma/to_pdf.js <page.html> <out.pdf> [columns] [rows of phones a page]
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [, , src, out, cols = '4', rowsArg = '1'] = process.argv;
  const rows = parseInt(rowsArg, 10);
  const columns = parseInt(cols, 10);
  const margin = 64, gapX = 48, gapY = 40;
  const inner = columns * 402 + (columns - 1) * gapX;
  const width = inner + 2 * margin;
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 2400, height: 1200 } });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(src), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);

  const height = await page.evaluate(({ inner, margin, gapX, gapY, rows }) => {
    const board = document.querySelector('.board');
    const secs = [...board.querySelectorAll(':scope > .sec, :scope > div')].filter(s => s.querySelector('.shot, .panel, h1, h2'));
    // measure everything where it stands, before moving it
    const sections = secs.map(sec => {
      const head = sec.querySelector(':scope > .sec-h') || sec.querySelector(':scope > h2') || sec.querySelector(':scope > h1')?.parentElement;
      const title = (sec.querySelector('h2, h1') || {}).textContent || '';
      const items = [...sec.querySelectorAll('.shot, .panel')].filter(e => !e.parentElement.closest('.shot, .panel'))
        .map(el => ({ el, w: el.getBoundingClientRect().width, h: el.getBoundingClientRect().height }));
      return { sec, head, title, headH: head ? head.getBoundingClientRect().height : 0, items };
    });
    const tallest = Math.max(...sections.flatMap(s => s.items.map(i => i.h)), 800);
    const firstHead = Math.max(...sections.map(s => s.headH), 60);
    const pageInner = Math.ceil(rows * tallest + (rows - 1) * gapY + firstHead + gapY);
    const pages = [];
    for (const s of sections) {
      let pg = null, lineW = 0, lineH = 0, usedH = 0;
      const open = first => {
        pg = { first, s, lines: [[]] };
        pages.push(pg);
        usedH = first ? s.headH + gapY : 56 + gapY;
        lineW = 0; lineH = 0;
      };
      open(true);
      if (!s.items.length) continue;
      for (const it of s.items) {
        const fitsLine = lineW === 0 || lineW + gapX + it.w <= inner;
        if (!fitsLine) {   // a new line
          usedH += lineH + gapY;
          lineW = 0; lineH = 0;
          pg.lines.push([]);
        }
        if (usedH + Math.max(lineH, it.h) > pageInner && (lineW > 0 || pg.lines.length > 1 || pg.lines[0].length)) {
          if (lineW > 0) { usedH += lineH + gapY; }
          open(false);
        }
        pg.lines[pg.lines.length - 1].push(it);
        lineW = lineW === 0 ? it.w : lineW + gapX + it.w;
        lineH = Math.max(lineH, it.h);
      }
    }
    // rebuild the document as pages
    const wrap = document.createElement('div');
    wrap.className = 'pdf-pages';
    for (const p of pages) {
      const div = document.createElement('div');
      div.className = 'pdf-page';
      if (p.first && p.s.head) div.appendChild(p.s.head);
      else if (!p.first) {
        const t = document.createElement('div');
        t.className = 'pdf-cont';
        t.textContent = p.s.title + ' (continued)';
        div.appendChild(t);
      }
      for (const line of p.lines.filter(l => l.length)) {
        const row = document.createElement('div');
        row.className = 'pdf-row';
        line.forEach(it => row.appendChild(it.el));
        div.appendChild(row);
      }
      wrap.appendChild(div);
    }
    board.replaceWith(wrap);
    const style = document.createElement('style');
    style.textContent = `
      @page { margin: 0 }
      * { -webkit-print-color-adjust: exact; print-color-adjust: exact }
      body { margin: 0; background: #E7E3DA }
      .pdf-page { box-sizing: border-box; width: ${inner + 2 * margin}px; height: ${pageInner + 2 * margin}px; padding: ${margin}px;
        display: flex; flex-direction: column; gap: ${gapY}px; overflow: hidden; break-after: page; background: #E7E3DA }
      .pdf-row { display: flex; gap: ${gapX}px; align-items: flex-start }
      .pdf-cont { font-family: Newsreader, Georgia, serif; font-size: 34px; color: #4C5156; height: 56px }
      .sec-h { max-width: ${inner}px }`;
    document.head.appendChild(style);
    return pageInner + 2 * margin;
  }, { inner, margin, gapX, gapY, rows });

  await page.setViewportSize({ width, height: 1200 });
  await page.waitForTimeout(300);
  await page.pdf({ path: out, width: `${width}px`, height: `${height}px`, printBackground: true });
  const n = await page.evaluate(() => document.querySelectorAll('.pdf-page').length);
  console.log(`wrote ${out}: ${n} pages of ${width} × ${height} px`);
  await browser.close();
})();
