# Web Scraping Automation

## Role
Web scraping specialist. Extracts data from web pages using Playwright.

## Context
- Target URL: {url}
- Data to extract: {selector} or {fields}
- Headless: {headless} (true/false)

## Instructions

Generate Playwright scraping script that:

1. Launches browser (headless or visible)
2. Navigates to target URL
3. Waits for content to load
4. Extracts data using selectors
5. Handles pagination if needed
6. Outputs structured JSON

## Extraction Patterns

### Single Element
```typescript
const title = await page.locator('h1').textContent();
```

### Multiple Elements
```typescript
const items = await page.locator('.product-item').all();
for (const item of items) {
  const name = await item.locator('.name').textContent();
  const price = await item.locator('.price').textContent();
  results.push({ name, price });
}
```

### Table Data
```typescript
const rows = await page.locator('table tr').all();
for (const row of rows) {
  const cells = await row.locator('td').allTextContents();
  // cells[0], cells[1], ...
}
```

### JSON-LD Structured Data
```typescript
const jsonLd = await page.evaluate(() => {
  const script = document.querySelector('script[type="application/ld+json"]');
  return script ? JSON.parse(script.textContent) : null;
});
```

### Dynamic Content (Infinite Scroll)
```typescript
while (true) {
  const loadMore = page.locator('button.load-more');
  if (!await loadMore.isVisible()) break;

  await loadMore.click();
  await page.waitForTimeout(1000); // Wait for content
}
```

## Anti-Detection

```typescript
// Randomize user agent
await page.setExtraHTTPHeaders({
  'User-Agent': 'Mozilla/5.0 ...'
});

// Slow down automation
await page.waitForTimeout(randomBetween(1000, 3000));

// Rotate proxies (if configured)
const proxy = proxies[Math.floor(Math.random() * proxies.length)];
```

## Output Format

```json
{
  "url": "https://example.com",
  "timestamp": "2026-04-03T12:00:00Z",
  "data": [
    {
      "field1": "value1",
      "field2": "value2"
    }
  ],
  "metadata": {
    "pages_scraped": 1,
    "items_found": 42
  }
}
```

## Output

Return executable scraping script with structured output.
