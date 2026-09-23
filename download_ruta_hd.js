const { chromium } = require('playwright');
const fs = require('fs');
const https = require('https');
const path = require('path');

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (res) => {
      res.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const page = await context.newPage();

  console.log("Navigating to Ruta Travel photos...");
  await page.goto('https://www.facebook.com/profile.php?id=100076746561202&sk=photos', {
    waitUntil: 'networkidle',
    timeout: 35000
  });

  await page.waitForTimeout(3000);

  // Find all photo links
  const photoLinks = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/photo"], a[href*="photo.php"], a[href*="photos"]'));
    return Array.from(new Set(anchors.map(a => a.href).filter(h => h.includes('fbid=') || h.includes('/photos/'))));
  });

  console.log(`Found ${photoLinks.length} photo page links.`);

  const downloadedImages = [];
  const outDir = 'C:/Users/oraul/ProyectosWeb/ruta-travel/assets/rutatravel_hd';
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  // Iterate over photo pages to get the full resolution image
  for (let i = 0; i < Math.min(photoLinks.length, 12); i++) {
    const link = photoLinks[i];
    console.log(`Opening photo [${i+1}/${photoLinks.length}]: ${link}`);
    try {
      await page.goto(link, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.waitForTimeout(2500);

      // Extract the largest image currently in the photo viewer
      const largeSrc = await page.evaluate(() => {
        const imgs = Array.from(document.querySelectorAll('img[src*="fbcdn.net"]'));
        // Find the image with largest naturalWidth/naturalHeight or largest rendered dimensions
        let best = null;
        let maxArea = 0;
        imgs.forEach(img => {
          const area = (img.naturalWidth || img.width || 0) * (img.naturalHeight || img.height || 0);
          if (area > maxArea) {
            maxArea = area;
            best = img.src;
          }
        });
        return best;
      });

      if (largeSrc) {
        const dest = path.join(outDir, `ruta_photo_${(i+1).toString().padStart(2, '0')}.jpg`);
        console.log(`Downloading high-res: ${largeSrc.slice(0, 80)}...`);
        await downloadFile(largeSrc, dest);
        downloadedImages.push(dest);
      }
    } catch (err) {
      console.log(`Error on photo ${i}: ${err.message}`);
    }
  }

  // If photo links were few, download the full URLs from fb_scraped_urls.json modifying query params to remove s206x206
  const rawUrls = JSON.parse(fs.readFileSync('C:/Users/oraul/ProyectosWeb/ruta-travel/assets/fb_scraped_urls.json', 'utf8'));
  for (let i = 0; i < rawUrls.length; i++) {
    let url = rawUrls[i];
    // Remove thumbnail crop restrictions to get maximum size
    let hdUrl = url.replace(/ctp=s\d+x\d+/g, 'ctp=s1600x1600').replace(/_s\d+x\d+_/g, '_');
    const dest = path.join(outDir, `ruta_direct_${(i+1).toString().padStart(2, '0')}.jpg`);
    try {
      await downloadFile(hdUrl, dest);
      console.log(`Downloaded direct HD: ruta_direct_${(i+1).toString().padStart(2, '0')}.jpg`);
    } catch (e) {
      // fallback to original url
      await downloadFile(url, dest);
    }
  }

  await browser.close();
  console.log("Finished downloading Ruta Travel HD photos.");
})();
