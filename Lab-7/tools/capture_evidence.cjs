// Render genuine saved subprocess output in Chromium and capture the browser page.
// Usage: NODE_PATH=<bundled node_modules> node tools/capture_evidence.cjs <chrome-path>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const escape = (s) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

(async () => {
  const browser = await chromium.launch({ executablePath: process.argv[2], headless: true,
                                         args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
  const names = fs.readdirSync(path.join(root, 'evidence/logs')).filter(f => f.endsWith('.txt')).sort();
  for (const file of names) {
    const stem = file.slice(0, -4);
    const meta = JSON.parse(fs.readFileSync(path.join(root, 'evidence/logs', stem + '.json'), 'utf8'));
    const fullOutput = fs.readFileSync(path.join(root, 'evidence/logs', file), 'utf8');
    const summary = stem === '07_after_full_suite';
    const output = summary ? fullOutput.trimEnd().split('\n').slice(-14).join('\n') : fullOutput;
    const command = [path.basename(meta.command[0]), ...meta.command.slice(1)].join(' ');
    const html = `<!doctype html><meta charset="utf-8"><title>${escape(stem)}</title>
<style>
body{margin:0;padding:26px;background:#fff;color:#17212b;font:18px/1.4 'DejaVu Sans',sans-serif}
h1{font-size:24px;margin:0 0 8px}p{margin:4px 0;font-size:16px;overflow-wrap:anywhere}
pre{font:18px/1.3 'DejaVu Sans Mono',monospace;white-space:pre-wrap;overflow-wrap:anywhere;
margin:20px 0 0;padding:18px;border:1px solid #cbd2da;background:#f7f9fb}
</style><h1>Lab 7 - Captured command output</h1>
<p>SRN: PES2UG24CS036 | ${escape(stem)} | Exit code: ${meta.exit_code}</p>
<p>Command: ${escape(command)}</p>
<p>Working directory: ${escape(meta.cwd)}</p>
${meta.stdin !== null ? `<p>stdin (escaped): ${escape(JSON.stringify(meta.stdin))}</p>` : ''}
<p>${summary ? 'Output excerpt: final 14 lines. Complete output is preserved in evidence/logs/' + file : 'Complete stdout and stderr from the recorded subprocess, displayed verbatim below.'}</p>
<pre>${escape(output)}</pre>`;
    fs.writeFileSync(path.join(root, 'evidence', stem + '.html'), html);
    await page.setContent(html);
    await page.evaluate(() => document.fonts.ready);
    await page.locator('body').screenshot({ path: path.join(root, 'screenshots', stem + '.png') });
    console.log(`Captured ${stem}.png`);
  }
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
