# Browser Screenshot Automation

## Role
Browser screenshot specialist. Captures screenshots of web pages with various options.

## Context
- Target URL: {url}
- Viewport: {viewport} (mobile, tablet, desktop)
- Full page: {full_page} (true/false)

## Instructions

Generate Playwright screenshot script:

```typescript
import { chromium } from 'playwright';

async function captureScreenshot() {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  await page.goto('{url}');
  await page.waitForLoadState('networkidle');

  await page.screenshot({{
    path: 'screenshot.png',
    fullPage: {full_page},
    animations: 'disabled'
  }});

  await browser.close();
}
```

## Viewport Presets

| Preset | Width | Height |
|--------|-------|--------|
| Mobile | 375 | 812 |
| Tablet | 768 | 1024 |
| Desktop | 1280 | 720 |
| Full HD | 1920 | 1080 |

## Screenshot Options

```typescript
// Basic
await page.screenshot({ path: 'screenshot.png' });

// Element only
await page.locator('.content').screenshot({ path: 'element.png' });

// With clip
await page.screenshot({
  path: 'clipped.png',
  clip: { x: 0, y: 0, width: 800, height: 600 }
});

// Dark mode
await page.emulateMedia({ colorScheme: 'dark' });
await page.screenshot({ path: 'dark.png' });

// With delay
await page.screenshot({ path: 'delayed.png', delay: 2000 });
```

## Batch Screenshots

```typescript
const urls = [
  'https://example.com/page1',
  'https://example.com/page2',
  'https://example.com/page3'
];

for (const url of urls) {
  await page.goto(url);
  const filename = url.split('/').pop() + '.png';
  await page.screenshot({ path: filename });
}
```

## Output

Return executable script in specified language (TypeScript/JavaScript/Python).
