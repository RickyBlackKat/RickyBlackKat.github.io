const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.join(__dirname, 'out');
  const files = fs.readdirSync(dir).filter(f => /^K5_sheet\d+\.svg$/.test(f)).sort((a,b)=>parseInt(a.match(/\d+/))-parseInt(b.match(/\d+/)));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1700, height: 1100 }, deviceScaleFactor: 1.6 });
  for (const f of files) {
    await page.setContent(`<html><body style="margin:0">${fs.readFileSync(path.join(dir, f), 'utf8')}</body></html>`);
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: 1700, height: 1100 } });
  }
  const pages = files.map(f => `<div class="pg">${fs.readFileSync(path.join(dir, f), 'utf8').replace('width="1700" height="1100"', 'width="100%" height="100%"')}</div>`).join('');
  await page.setContent(`<html><head><style>@page{size:17in 11in;margin:0}body{margin:0}.pg{width:17in;height:11in;page-break-after:always;overflow:hidden}.pg:last-child{page-break-after:auto}</style></head><body>${pages}</body></html>`);
  await page.pdf({ path: path.join(dir, 'KAT-5_drawings.pdf'), width: '17in', height: '11in', printBackground: true });
  await browser.close(); console.log('rendered', files.length);
})();
