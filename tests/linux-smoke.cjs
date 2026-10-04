const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const files = execFileSync('git', ['ls-files', '-z'], { cwd: root })
  .toString().split('\0').filter(Boolean);
let packageBytes = 0;
for (const file of files) {
  const stats = fs.lstatSync(path.join(root, file));
  assert(!stats.isSymbolicLink(), `${file} is a symlink`);
  assert(stats.size <= 8_000_000, `${file} exceeds the CanvasTTY asset limit`);
  packageBytes += stats.size;
}
assert(files.length <= 500, 'Too many files for CanvasTTY');
assert(packageBytes <= 25_000_000, 'Package exceeds the CanvasTTY size limit');
assert(!files.some((file) => file.endsWith('.mp4')), 'Demo video entered the plugin package');

const manifest = JSON.parse(fs.readFileSync(path.join(root, 'canvastty.plugin.json')));
assert.equal(manifest.apiVersion, 1);
assert.equal(manifest.contributions[0].entry, 'index.html');

const types = { '.html': 'text/html', '.js': 'text/javascript', '.webp': 'image/webp' };
const server = http.createServer((request, response) => {
  if (request.url === '/harness') {
    response.setHeader('Content-Type', 'text/html');
    response.end('<iframe sandbox="allow-scripts" src="/index.html" width="320" height="520"></iframe>');
    return;
  }
  const file = path.resolve(root, decodeURIComponent(request.url.slice(1)));
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {
    response.writeHead(404).end();
    return;
  }
  response.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  response.setHeader('Content-Security-Policy', "default-src 'none'; script-src 'self'; img-src 'self'; style-src 'unsafe-inline'");
  fs.createReadStream(file).pipe(response);
});

(async () => {
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('response', (response) => {
      if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
    });
    await page.goto(`http://127.0.0.1:${server.address().port}/harness`);
    const frame = page.frameLocator('iframe');
    await frame.locator('canvas').waitFor();
    await frame.locator('select').waitFor();
    const sprite = frame.locator('canvas');
    await sprite.evaluate((canvas) => { canvas.style.opacity = '0'; });
    const blank = await sprite.screenshot();
    await sprite.evaluate((canvas) => { canvas.style.opacity = '1'; });
    let painted = false;
    for (let attempt = 0; attempt < 40; attempt++) {
      if (!(await sprite.screenshot()).equals(blank)) { painted = true; break; }
      await page.waitForTimeout(250);
    }
    assert(painted, 'The sprite canvas stayed visually empty');
    const options = await frame.locator('select option').allTextContents();
    assert(options.includes('Dance') && options.includes('All actions'));
    await frame.locator('select').selectOption('dance');
    assert.equal(await frame.locator('select').inputValue(), 'dance');
    await frame.locator('body').hover();
    await frame.locator('.pick').evaluate(async (element) => {
      for (let attempt = 0; attempt < 20; attempt++) {
        if (Number(getComputedStyle(element).opacity) > 0.95) return;
        await new Promise((resolve) => setTimeout(resolve, 25));
      }
      throw new Error('The animation picker did not appear on hover');
    });
    assert.deepEqual(errors, []);
    console.log(`Linux Chromium smoke test passed; ${files.length} files, ${packageBytes} bytes`);
  } finally {
    await browser.close();
    server.close();
  }
})().catch((error) => { console.error(error); process.exitCode = 1; server.close(); });
