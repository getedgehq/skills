const { test, expect } = require('playwright/test');

for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 1000 }]) {
  test(`checkout at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('http://127.0.0.1:4173/');
    await expect(page).toHaveTitle(/Reserve your workshop seat/);
    await expect(page.locator('h1')).toHaveText('Reserve your seat.');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBeTruthy();
  });
}

test('validates inputs and reports checkout failure', async ({ page }) => {
  await page.goto('http://127.0.0.1:4173/');
  await page.getByRole('button', { name: /Continue to secure payment/ }).click();
  await expect(page.locator('#name-error')).toHaveText('Enter your name.');
  await page.locator('#name').fill('Test Attendee');
  await page.locator('#email').fill('not-an-email');
  await page.getByRole('button', { name: /Continue to secure payment/ }).click();
  await expect(page.locator('#email-error')).toHaveText('Enter a valid email address.');
  await page.locator('#email').fill('test@example.com');
  await page.getByRole('button', { name: /Continue to secure payment/ }).click();
  await expect(page.locator('#form-status')).toContainText('temporarily unavailable');
  await expect(page.getByRole('button', { name: /Continue to secure payment/ })).toBeEnabled();
});
