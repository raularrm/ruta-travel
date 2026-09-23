const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log("Launching headless browser to extract Ruta Travel Facebook photos...");
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  try {
    await page.goto('https://www.facebook.com/profile.php?id=100076746561202&sk=photos', {
      waitUntil: 'networkidle',
      timeout: 30000
    });
  } catch (e) {
    console.log("Navigation timeout or partial load:", e.message);
  }

  await page.waitForTimeout(4000);

  // Extract all image URLs
  const imgUrls = await page.evaluate(() => {
    const images = Array.from(document.querySelectorAll('img'));
    return images.map(img => img.src).filter(src => src && src.includes('fbcdn.net'));
  });

  console.log(`Found ${imgUrls.length} fbcdn images on photos tab.`);
  
  // Also check main profile page if photos tab required login
  if (imgUrls.length < 5) {
    console.log("Navigating to main profile page...");
    try {
      await page.goto('https://www.facebook.com/profile.php?id=100076746561202', {
        waitUntil: 'networkidle',
        timeout: 30000
      });
      await page.waitForTimeout(4000);
      const moreUrls = await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        return images.map(img => img.src).filter(src => src && src.includes('fbcdn.net'));
      });
      imgUrls.push(...moreUrls);
    } catch (e) {
      console.log("Error on main page:", e.message);
    }
  }

  console.log(`Total unique fbcdn images: ${new Set(imgUrls).size}`);
  const uniqueUrls = Array.from(new Set(imgUrls));
  fs.writeFileSync('C:/Users/oraul/ProyectosWeb/ruta-travel/assets/fb_scraped_urls.json', JSON.stringify(uniqueUrls, null, 2));

  await browser.close();
})();
