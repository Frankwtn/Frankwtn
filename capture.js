/**
 * capture.js
 * Uses Puppeteer to screenshot card.html frame-by-frame,
 * then encodes to GIF using gif-encoder-2.
 *
 * Strategy:
 *   - Inject a controllable animation tick (no real-time RAF)
 *   - Render SCAN_FRAMES frames for scan reveal (3.2s)
 *   - Render IDLE_FRAMES frames for idle with blinking cursor/live dot
 *   - All at 80ms/frame for smooth left-panel GIF sync
 */

const puppeteer   = require('puppeteer');
const GIFEncoder  = require('gif-encoder-2');
const fs          = require('fs');
const path        = require('path');

const REPO        = __dirname;
const HTML_PATH   = path.join(REPO, 'card.html');
const OUT_PATH    = path.join(REPO, 'system-infocard-combined.gif');

const WIDTH       = 980;
const HEIGHT      = 520;
const MS_PER_FRAME = 80;

// Scan reveal: 40 frames = 3.2s
// Idle hold  : 200 frames = 16s  (cursor/live blink at ~4 frames = 320ms)
const SCAN_FRAMES = 40;
const IDLE_FRAMES = 120;
const TOTAL       = SCAN_FRAMES + IDLE_FRAMES;

function easeInOut(t) {
  return t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
}

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      `--window-size=${WIDTH},${HEIGHT}`,
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT, deviceScaleFactor: 1 });

  // Load HTML — use file:// URL so relative img src works
  const fileUrl = 'file:///' + HTML_PATH.replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 30000 });

  // Wait for fonts + GIF to load
  await new Promise(r => setTimeout(r, 800));

  // Inject controlled animation — disable the auto RAF loop
  await page.evaluate(() => {
    window._scanDone = false;

    // Collect row elements in order
    window._rowIds = [
      'r0','r1','r2','r3','r4','r5',
      'rd0',
      'r6','r7','r8','r9','r10',
      'rd1',
      'r11','r12','r13','r14','r15','r16'
    ];

    // Hide all rows, hide scan line initially
    window._rowIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.opacity = '0';
    });
    const sl = document.getElementById('scanLine');
    if (sl) sl.style.display = 'none';

    // Stop the auto scan loop that started
    // (override setTimeout to no-op after page load)
    window._blockAuto = true;
    const origSetTimeout = window.setTimeout;
    window.setTimeout = function(fn, delay, ...args) {
      if (window._blockAuto && delay > 300) return;
      return origSetTimeout(fn, delay, ...args);
    };
  });

  // Set up GIF encoder
  const encoder = new GIFEncoder(WIDTH, HEIGHT, 'neuquant', true);
  const outStream = fs.createWriteStream(OUT_PATH);
  encoder.createReadStream().pipe(outStream);
  encoder.start();
  encoder.setRepeat(0);
  encoder.setDelay(MS_PER_FRAME);
  encoder.setQuality(6); // 1=best quality, 20=worst

  console.log(`Capturing ${TOTAL} frames...`);

  const rowsEl   = await page.$('#rows');
  const rowsBox  = await rowsEl.boundingBox();
  const rowsH    = rowsBox.height;

  for (let f = 0; f < TOTAL; f++) {
    const inScan = f < SCAN_FRAMES;

    if (inScan) {
      const t      = f / (SCAN_FRAMES - 1);
      const te     = easeInOut(t);
      const scanY  = te * (rowsH + 32);

      await page.evaluate(({ scanY, rowsTop }) => {
        const sl = document.getElementById('scanLine');
        sl.style.display = 'block';
        sl.style.top = (scanY - 16) + 'px';

        window._rowIds.forEach(id => {
          const el = document.getElementById(id);
          if (!el) return;
          const elTop = el.offsetTop;
          el.style.opacity = elTop <= scanY - 8 ? '1' : '0';
        });
      }, { scanY, rowsTop: rowsBox.y });

    } else {
      // Idle: all rows visible, scan line hidden, cursor blinks via CSS
      if (f === SCAN_FRAMES) {
        await page.evaluate(() => {
          const sl = document.getElementById('scanLine');
          sl.style.display = 'none';
          window._rowIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.opacity = '1';
          });
        });
      }

      // Advance CSS animation time for cursor + live dot blink
      const idleMs = (f - SCAN_FRAMES) * MS_PER_FRAME;
      await page.evaluate((ms) => {
        document.querySelectorAll('.cursor, .live-dot').forEach(el => {
          el.style.animationDelay = `-${ms}ms`;
        });
      }, idleMs);
    }

    // Screenshot
    const png = await page.screenshot({ type: 'png' });

    // Decode PNG to raw RGBA pixels
    const decoded = await page.evaluate(async (b64) => {
      return new Promise(resolve => {
        const img = new window.Image();
        img.onload = () => {
          const c = document.createElement('canvas');
          c.width = img.width; c.height = img.height;
          const ctx = c.getContext('2d');
          ctx.drawImage(img, 0, 0);
          const d = ctx.getImageData(0, 0, img.width, img.height);
          resolve(Array.from(d.data));
        };
        img.src = 'data:image/png;base64,' + b64;
      });
    }, png.toString('base64'));

    encoder.addFrame(Buffer.from(decoded));

    if (f % 20 === 0) process.stdout.write(`\r  frame ${f+1}/${TOTAL}`);
  }

  encoder.finish();
  await browser.close();

  await new Promise(resolve => outStream.on('finish', resolve));

  const sizeMb = fs.statSync(OUT_PATH).size / (1024*1024);
  console.log(`\nDone! ${OUT_PATH}`);
  console.log(`Size: ${sizeMb.toFixed(1)} MB`);
  if (sizeMb > 25) console.log('WARNING: >25MB, GitHub may reject large files.');
})();
