const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, ...names] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1.5 });
  for (const n of names) {
    await page.goto('file://' + path.resolve(out, n + '.html'));
    await page.waitForTimeout(300);
    const over = await page.$$eval('.t', els => els.map(e => {
      const f = e.querySelector('.flow'); const cs = getComputedStyle(e);
      const avail = e.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      const wide = [...e.querySelectorAll('p')].some(p => p.scrollWidth > p.clientWidth + 1);
      return { name: e.dataset.name, text: f.innerText.slice(0, 50), need: f.scrollHeight, avail, wide };
    }).filter(o => o.need > o.avail + 0.5 || o.wide));
    console.log(n, over.length ? JSON.stringify(over, null, 1) : 'no overflow');
    await page.pdf({ path: path.resolve(out, n + '.pdf'), preferCSSPageSize: true, printBackground: true });
    const secs = await page.$$('section.sheet');
    for (let i = 0; i < secs.length; i++) await secs[i].screenshot({ path: path.resolve(out, `${n}_${i + 1}.png`) });
  }
  await browser.close();
})();
