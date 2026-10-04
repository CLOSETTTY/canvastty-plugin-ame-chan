const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, execFileSync } = require('node:child_process');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const output = path.resolve(root, 'native-host-results');
const mode = process.argv[2];
const version = '1.7.1';
const base = `https://github.com/howdeploy/CanvasTTY/releases/download/v${version}/`;
// macOS TMPDIR is a long /var/folders path; CanvasTTY's Unix socket needs
// a short user-data path. The generated directory is isolated to this test.
const temporary = fs.mkdtempSync(path.join(process.platform === 'darwin' ? '/tmp' : os.tmpdir(), 'ame-native-'));
fs.mkdirSync(output, { recursive: true });
const run = (command, args, options = {}) => execFileSync(command, args, {
  stdio: 'inherit', ...options,
});

async function download(name) {
  const destination = path.join(temporary, name);
  run('curl', ['--fail', '--location', '--retry', '3', '--output', destination, base + name]);
  return destination;
}

async function prepare() {
  if (mode === 'macos') {
    assert.equal(process.platform, 'darwin');
    assert.equal(process.arch, 'arm64');
    const zip = await download(`CanvasTTY-${version}-mac-arm64.zip`);
    run('ditto', ['-x', '-k', zip, temporary]);
    run('python3', [path.join(root, 'frameless/mac-transparent-card.py'), 'apply',
      '--app', path.join(temporary, 'CanvasTTY.app')]);
    return path.join(os.homedir(), 'Applications/CanvasTTY Ame-chan.app/Contents/MacOS/CanvasTTY');
  }
  assert.equal(process.platform, 'linux');
  if (mode === 'appimage') {
    const image = await download(`CanvasTTY-${version}-linux-x86_64.AppImage`);
    fs.chmodSync(image, 0o755);
    run('python3', [path.join(root, 'frameless/linux-transparent-card.py'), 'apply', '--appimage', image]);
    return path.join(os.homedir(), '.local/bin/canvastty-ame-chan');
  }
  assert.equal(mode, 'deb');
  const deb = await download(`CanvasTTY-${version}-linux-amd64.deb`);
  const unpacked = path.join(temporary, 'deb');
  run('dpkg-deb', ['-x', deb, unpacked]);
  const apps = fs.readdirSync(path.join(unpacked, 'opt'));
  assert.equal(apps.length, 1, 'Ambiguous .deb application directory');
  const app = path.join(unpacked, 'opt', apps[0]);
  run('python3', [path.join(root, 'frameless/linux-transparent-card.py'), 'apply',
    '--resources', path.join(app, 'resources')]);
  return path.join(app, 'canvastty');
}

async function main() {
  const executable = await prepare();
  const userData = path.join(temporary, 'user-data');
  const plugin = path.join(userData, 'plugins/ame-chan-claude');
  fs.mkdirSync(plugin, { recursive: true });
  const tracked = execFileSync('git', ['ls-files', '-z'], { cwd: root }).toString().split('\0').filter(Boolean);
  for (const file of tracked) {
    const target = path.join(plugin, file);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(root, file), target);
  }
  fs.writeFileSync(path.join(userData, 'plugins.json'), JSON.stringify({
    'ame-chan-claude': {
      sourceUrl: 'https://github.com/CLOSETTTY/canvastty-plugin-ame-chan',
      enabled: true, installedAt: Date.now(),
    },
  }));
  fs.writeFileSync(path.join(userData, 'settings.json'), JSON.stringify({
    locale: 'en', homeLayout: [],
    pluginCanvas: [{ id: 'ame-native', pluginId: 'ame-chan-claude', contributionId: 'ame',
      title: 'Ame-chan', position: { x: 650, y: 250 }, size: { width: 320, height: 520 } }],
  }));
  const log = fs.createWriteStream(path.join(output, `${mode}.log`));
  const env = { ...process.env, CANVASTTY_USER_DATA_DIR: userData };
  delete env.GITHUB_TOKEN;
  const args = ['--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9222'];
  // The isolated Linux CI VM has no configured Chrome sandbox; this does not
  // change the shipped application or the plugin frame's sandbox attributes.
  if (process.platform === 'linux') args.push('--no-sandbox');
  const child = spawn(executable, args, { env, stdio: ['ignore', 'pipe', 'pipe'] });
  child.stdout.pipe(log, { end: false });
  child.stderr.pipe(log, { end: false });
  let launchError;
  child.on('error', (error) => { launchError = error; });
  let browser;
  try {
    for (let i = 0; i < 90; i++) {
      if (launchError) throw launchError;
      if (child.exitCode !== null) throw new Error(`CanvasTTY exited: ${child.exitCode}`);
      try {
        browser = await chromium.connectOverCDP('http://127.0.0.1:9222', { timeout: 1000 });
        break;
      } catch { await new Promise((resolve) => setTimeout(resolve, 1000)); }
    }
    assert(browser, 'CanvasTTY debug endpoint never became ready');
    const context = browser.contexts()[0];
    let page;
    for (let i = 0; i < 60; i++) {
      page = context.pages().find((candidate) => candidate.url().includes('index.html'));
      if (page) break;
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    assert(page, 'CanvasTTY renderer not found');
    const card = page.locator('.plugin-canvas-card').filter({ has: page.locator('iframe[src*="//ame-chan-claude/"]') });
    await card.waitFor({ timeout: 60000 });
    // Allow the initial HOME camera to settle before reading the card bounds.
    await page.waitForTimeout(1500);
    const box = await card.boundingBox();
    assert(box && box.width > 0 && box.height > 0, 'Card has no visible bounds');
    const style = await card.evaluate((element) => {
      const css = getComputedStyle(element);
      return { background: css.backgroundColor, shadow: css.boxShadow, border: css.borderTopWidth };
    });
    assert.equal(style.background, 'rgba(0, 0, 0, 0)');
    assert.equal(style.shadow, 'none');
    assert.equal(style.border, '0px');
    const frame = card.frameLocator('iframe');
    const canvas = frame.locator('canvas');
    await canvas.waitFor({ timeout: 30000 });
    // The opaque-origin plugin sandbox intentionally taints its canvas.
    // Compare rendered screenshots without weakening that sandbox.
    await canvas.evaluate((element) => { element.style.opacity = '0'; });
    const blank = await canvas.screenshot();
    await canvas.evaluate((element) => { element.style.opacity = '1'; });
    let painted = false;
    for (let i = 0; i < 60; i++) {
      if (!(await canvas.screenshot()).equals(blank)) { painted = true; break; }
      await page.waitForTimeout(250);
    }
    assert(painted, 'Sprite remained visually empty');
    await page.screenshot({ path: path.join(output, `${mode}-idle.png`) });
    await card.hover();
    await frame.locator('#mode-toggle').evaluate((button) => {
      window.pickerTrace = [];
      for (const type of ['pointerdown', 'pointerup', 'click', 'focusin']) {
        document.addEventListener(type, (event) => {
          window.pickerTrace.push({ type, target: event.target.id || event.target.className,
            expanded: button.getAttribute('aria-expanded') });
        });
      }
    });
    await frame.locator('#mode-toggle').click();
    await page.screenshot({ path: path.join(output, `${mode}-menu.png`) });
    const pickerState = await frame.locator('#mode-menu').evaluate((element) => ({
      className: element.className,
      expanded: document.getElementById('mode-toggle').getAttribute('aria-expanded'),
      visibility: getComputedStyle(element).visibility,
      opacity: getComputedStyle(element).opacity,
      bounds: element.getBoundingClientRect().toJSON(),
    }));
    const pickerTrace = await frame.locator('#mode-toggle').evaluate(() => window.pickerTrace);
    console.log(`Picker after opening: ${JSON.stringify(pickerState)} events=${JSON.stringify(pickerTrace)}`);
    await frame.locator('#mode-menu [data-mode="dance"]').click();
    assert.equal(await frame.locator('#mode-menu [data-mode="dance"]').getAttribute('aria-checked'), 'true');
    const close = card.locator('.plugin-canvas-card__header > button');
    await close.evaluate(async (element) => {
      for (let i = 0; i < 20; i++) {
        if (Number(getComputedStyle(element).opacity) > 0.95) return;
        await new Promise((resolve) => setTimeout(resolve, 50));
      }
      throw new Error('Close control did not appear on hover');
    });
    await page.screenshot({ path: path.join(output, `${mode}-hover.png`) });
    await close.click();
    await card.waitFor({ state: 'detached' });
    fs.writeFileSync(path.join(output, `${mode}.json`), JSON.stringify({
      hostVersion: version, platform: process.platform, architecture: process.arch,
      transparentCard: true, spriteRendered: true, animationPicker: true, hoverClose: true,
    }, null, 2));
    console.log(`Native CanvasTTY ${version} ${mode}: transparent card, sprite and hover controls passed`);
  } finally {
    if (browser) await browser.close();
    child.kill();
    log.end();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
