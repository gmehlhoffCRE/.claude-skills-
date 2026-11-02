const { chromium } = require('playwright');
(async () => {
  const [html, prefix] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1.5 });
  await p.goto('file://' + html); await p.waitForTimeout(500);
  const over = await p.$$eval('.t', els => els.map(e => {
    const f = e.firstElementChild; const cs = getComputedStyle(e);
    const avail = e.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    return { text: f.innerText.slice(0, 40).replace(/\n/g, ' / '), need: f.scrollHeight, avail };
  }).filter(o => o.need > o.avail + 1));
  console.log(over.length ? JSON.stringify(over) : 'no overflow');
  const secs = await p.$$('section.sheet');
  for (let i = 0; i < secs.length; i++) await secs[i].screenshot({ path: `${prefix}_${i + 1}.png` });
  await p.pdf({ path: `${prefix}.pdf`, preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
