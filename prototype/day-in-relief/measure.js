// Audit, 11 Nov 2026: measures the two drawings of the same day in headless Chromium (the pre-installed Playwright).
//   node prototype/day-in-relief/measure.js
// Headless Chromium draws WebGL in software (no graphics chip), so the relief times here are a worst case for a
// phone with a working GPU and say nothing about battery: only a phone can measure that.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), zlib = require('zlib');
(async () => {
  const file = path.join(__dirname, 'index.html'), raw = fs.readFileSync(file);
  const out = { bytes: raw.length, gzip_bytes: zlib.gzipSync(raw).length, network_requests: 0, console_errors: [] };
  const browser = await chromium.launch();
  for (const slow of [1, 4]) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error') out.console_errors.push(m.text()); });
    page.on('pageerror', e => out.console_errors.push(String(e)));
    page.on('request', r => { if (!r.url().startsWith('file:')) out.network_requests++; });
    const cdp = await ctx.newCDPSession(page);
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: slow });
    await page.goto('file://' + file);
    const first = await page.evaluate(() => performance.getEntriesByName('first-drawing')[0].startTime);
    const flat = await page.evaluate(() => window.bench('flat', 200));
    const heapFlat = await page.evaluate(() => performance.memory.usedJSHeapSize);
    const relief = await page.evaluate(() => window.bench('relief', 200));
    const heapRelief = await page.evaluate(() => performance.memory.usedJSHeapSize);
    const renderer = await page.evaluate(() => { const g = document.createElement('canvas').getContext('webgl');
      const e = g && g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'none'; });
    out[`cpu_${slow}x`] = { first_drawing_ms: +first.toFixed(1), flat_ms_per_drawing: +flat.toFixed(3), relief_ms_per_drawing: +relief.toFixed(3),
      heap_after_flat_kb: Math.round(heapFlat / 1024), heap_after_relief_kb: Math.round(heapRelief / 1024), webgl_renderer: renderer };
    if (slow === 1) {
      fs.mkdirSync(path.join(__dirname, 'screens'), { recursive: true });
      await page.evaluate(() => { document.getElementById('b-flat').click(); });
      await page.waitForTimeout(150); await page.screenshot({ path: path.join(__dirname, 'screens', 'flat.png') });
      await page.evaluate(() => { document.getElementById('b-relief').click(); });
      await page.waitForTimeout(150); await page.screenshot({ path: path.join(__dirname, 'screens', 'relief.png') });
      out.accessibility = await page.evaluate(() => ({
        buttons_named: [...document.querySelectorAll('button')].every(b => b.textContent.trim().length > 0),
        pressed_state: [...document.querySelectorAll('button')].map(b => b.getAttribute('aria-pressed')),
        list_rows: document.querySelectorAll('ol.day li').length,
        drawings_hidden_from_readers: [...document.querySelectorAll('canvas, .tag')].every(e => e.getAttribute('aria-hidden') === 'true'),
        stage_described: !!document.getElementById(document.getElementById('stage').getAttribute('aria-describedby')),
        smallest_button_px: Math.min(...[...document.querySelectorAll('button')].map(b => b.getBoundingClientRect().height)),
        animation_loop: 'none (one drawing per change)' }));
      // the keyboard turns it; nothing moves by itself
      await page.focus('#stage'); const before = await page.evaluate(() => document.querySelector('.tag').style.left);
      await page.keyboard.press('ArrowLeft'); await page.waitForTimeout(100);
      out.accessibility.keyboard_turns_it = before !== await page.evaluate(() => document.querySelector('.tag').style.left);
      await page.waitForTimeout(600);
      const still = await page.evaluate(() => document.querySelector('.tag').style.left); await page.waitForTimeout(600);
      out.accessibility.moves_by_itself = still !== await page.evaluate(() => document.querySelector('.tag').style.left);
    }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'measurements.json'), JSON.stringify(out, null, 1) + '\n');
  console.log(JSON.stringify(out, null, 1));
})();
