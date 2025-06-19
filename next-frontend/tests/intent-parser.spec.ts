import { test, expect } from '@playwright/test';

test.describe('Intent Parser E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app before each test
    await page.goto('/');
  });

  test('should parse a product link and display a product card', async ({ page }) => {
    // 1. Find the input and fill it with a mock Taobao link
    const userInput = page.getByTestId('user-input');
    await userInput.fill('https://item.taobao.com/item.htm?id=12345');

    // 2. Click the submit button
    const submitButton = page.getByTestId('submit-button');
    await submitButton.click();

    // 3. Wait for the product card to appear and verify its content
    const productCard = page.getByTestId('product-card-12345');
    await expect(productCard).toBeVisible({ timeout: 10000 }); // Wait up to 10s

    // Verify some text within the card from the mock API
    await expect(productCard.getByText(/【测试商品】/)).toBeVisible();
    await expect(productCard.getByText(/价格：¥99.9/)).toBeVisible();
  });

  test('should show a "no shopping intent" message for non-shopping text', async ({ page }) => {
    // 1. Find the input and fill it with non-shopping text
    const userInput = page.getByTestId('user-input');
    await userInput.fill('今天天气怎么样？');

    // 2. Click the submit button
    const submitButton = page.getByTestId('submit-button');
    await submitButton.click();

    // 3. Wait for the result message and verify its content
    // In this new implementation, an empty product list with a previous user input triggers the message.
    const productList = page.getByTestId('product-list');
    await expect(productList).not.toBeVisible();
    
    const noProductMessage = page.getByTestId('no-product-message');
    await expect(noProductMessage).toBeVisible({ timeout: 10000 });
    await expect(noProductMessage).toContainText('未识别到明确的购物意图');
  });
}); 