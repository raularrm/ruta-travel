const { chromium } = require('playwright');

async function extractSection(url, sectionName) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const page = await context.newPage();
  
  console.log(`\n🔍 ${sectionName}...`);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(4000);
    
    const data = await page.evaluate(() => {
      const result = {
        title: document.title,
        url: window.location.href,
        text: document.body.innerText.slice(0, 8000)
      };
      return JSON.stringify(result);
    });
    
    console.log('Texto extraído:');
    console.log(data);
  } catch (e) {
    console.log(`Error: ${e.message}`);
  }
  
  await browser.close();
}

async function main() {
  // Reviews
  await extractSection('https://www.facebook.com/profile.php?id=100076746561202&sk=reviews', 'REVIEWS');
  
  // Posts recientes
  await extractSection('https://www.facebook.com/profile.php?id=100076746561202', 'POSTS');
  
  // About
  await extractSection('https://www.facebook.com/profile.php?id=100076746561202&sk=about', 'ABOUT');
}

main().catch(console.error);
