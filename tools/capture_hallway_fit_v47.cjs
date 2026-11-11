// Rasterize the two versioned SVG sheets without changing their vector source.
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium } = require('C:/Users/aidzm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const dir = path.resolve(__dirname, '../Прихожая');
  const stems = ['112_прихожая_план_и_проходы_v47', '113_прихожая_шкаф_и_банкетка_v47'];
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 2600, height: 1700 }, deviceScaleFactor: 1 });
  for (const stem of stems) {
    const svg = fs.readFileSync(path.join(dir, stem + '.svg'), 'utf8');
    await page.setContent('<html><body style="margin:0">' + svg + '</body></html>');
    await page.evaluate(() => document.fonts.ready);
    const overflow = await page.evaluate(() => Array.from(document.querySelectorAll('svg text')).filter(t => {
      const b = t.getBBox();
      return b.x < 0 || b.y < 0 || b.x + b.width > 2600 || b.y + b.height > 1700;
    }).map(t => t.textContent));
    assert.deepEqual(overflow, [], 'labels extend beyond the sheet');
    await page.screenshot({ path: path.join(dir, stem + '.png') });
    console.log('Saved and checked:', stem);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exitCode = 1; });
