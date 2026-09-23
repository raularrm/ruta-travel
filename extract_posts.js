const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  
  const page = await context.newPage();
  
  // Ir a los posts
  console.log('📱 Cargando publicaciones...');
  await page.goto('https://www.facebook.com/profile.php?id=100076746561202', {
    waitUntil: 'domcontentloaded',
    timeout: 45000
  });
  await page.waitForTimeout(5000);
  
  // Extraer todos los posts visibles
  const posts = await page.evaluate(() => {
    const results = [];
    const postElements = document.querySelectorAll('[data-testid="post"], article, [class*="post"]');
    
    postElements.forEach((post, idx) => {
      const text = post.innerText || '';
      if (text.length > 50) {
        results.push({
          index: idx,
          text: text.slice(0, 1500)
        });
      }
    });
    
    // También extraer del feed general
    const allPs = document.querySelectorAll('div');
    const postTexts = [];
    allPs.forEach(p => {
      const t = p.innerText || '';
      if (t.includes('Ruta Travel') || t.includes('viaje') || t.includes('tour') || t.includes('paquete') || t.includes('destino')) {
        postTexts.push(t.slice(0, 500));
      }
    });
    
    return JSON.stringify({ posts: results.slice(0, 8), feedReferences: postTexts.slice(0, 10) });
  });
  
  console.log('POSTS ENCONTRADOS:');
  console.log(posts);
  
  // Extraer números de teléfono visibles
  const phones = await page.evaluate(() => {
    const allText = document.body.innerText;
    const phoneRegex = /(\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}/g;
    const matches = allText.match(phoneRegex);
    return [...new Set(matches || [])];
  });
  
  console.log('\n📞 NÚMEROS DE TELÉFONO ENCONTRADOS:');
  console.log(phones);
  
  await browser.close();
})();
