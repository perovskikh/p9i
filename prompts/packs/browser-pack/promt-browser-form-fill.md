# Browser Form Automation

## Role
Form automation specialist. Automates form filling, submission, and validation.

## Context
- Target URL: {url}
- Form selector: {form_selector}
- Fields: {fields_json}

## Instructions

Generate Playwright script that:

1. Navigates to form page
2. Fills each field with provided data
3. Handles special inputs (dropdowns, checkboxes, radio)
4. Validates field values
5. Submits form
6. Verifies success/error state

## Input Types

### Text Input
```typescript
await page.fill('#name', 'John Doe');
await page.locator('#email').fill('john@example.com');
```

### Textarea
```typescript
await page.locator('textarea#description').fill('Long text here...');
```

### Select/Dropdown
```typescript
// Select by value
await page.selectOption('#country', 'us');

// Select by label
await page.selectOption('#country', { label: 'United States' });
```

### Checkbox
```typescript
// Check
await page.check('#agree-terms');

// Uncheck
await page.uncheck('#subscribe');

// Assert checked
await expect(page.locator('#agree-terms')).toBeChecked();
```

### Radio
```typescript
await page.check('input[name="plan"][value="pro"]');
```

### File Upload
```typescript
await page.setInputFiles('input[type="file"]', './document.pdf');
```

### Date Picker
```typescript
await page.fill('input[type="date"]', '2026-04-15');
// Or click through calendar
await page.click('input[type="date"]');
await page.click('.datepicker-day:has-text("15")');
```

### Autocomplete
```typescript
await page.fill('#country-input', 'United');
await page.waitForSelector('.autocomplete-item');
await page.click('.autocomplete-item:has-text("United States")');
```

## Validation

```typescript
// Before submit
await expect(page.locator('#email')).toHaveValue(/@/);
await expect(page.locator('#name')).not.toBeEmpty();

// After submit
await expect(page.locator('.success-message')).toBeVisible();
```

## Full Example

```typescript
test('registration form', async ({ page }) => {
  await page.goto('/register');

  // Fill basic info
  await page.fill('#firstName', 'John');
  await page.fill('#lastName', 'Doe');
  await page.fill('#email', 'john@example.com');

  // Select dropdown
  await page.selectOption('#country', 'us');

  // Check agreements
  await page.check('#terms');
  await page.check('#newsletter');

  // Submit
  await page.click('button[type="submit"]');

  // Verify
  await expect(page).toHaveURL(/.*welcome/);
  await expect(page.locator('.welcome-message')).toContainText('John');
});
```

## Output

Return executable form automation script.
