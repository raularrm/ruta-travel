const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  console.log('🔍 Navegando a Facebook...');
  await page.goto('https://www.facebook.com/profile.php?id=100076746561202', {
    waitUntil: 'networkidle',
    timeout: 60000
  });
  
  // Esperar a que cargue el contenido
  await page.waitForTimeout(5000);
  
  // Extraer título
  const title = await page.title();
  console.log('Título:', title);
  
  // Extraer toda el texto visible
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('\n=== TEXTO VISIBLE ===');
  console.log(bodyText.slice(0, 5000));
  
  // Extraer imágenes
  const images = await page.evaluate(() => {
    const allImages = Array.from(document.querySelectorAll('img'));
    return allImages
      .map(img => ({
        src: img.src,
        alt: img.getAttribute('alt') || '',
        width: img.naturalWidth || 0,
        height: img.naturalHeight || 0,
        className: img.className,
        // Filtrar: solo imágenes con tamaño significativo
        isLarge: (img.naturalWidth || 0) > 100 && (img.naturalHeight || 0) > 100
      }))
      .filter(img => img.isLarge || img.alt.length > 0);
  });
  
  console.log('\n=== IMÁGENES ENCONTRADAS ===');
  console.log(`Total imágenes relevantes: ${images.length}`);
  images.forEach((img, i) => {
    console.log(`[${i}] ${img.src.split('/').slice(-1)[0] || 'sin-id'} | ${img.alt.slice(0, 100)} | ${img.width}x${img.height}`);
  });
  
  // Descargar las primeras imágenes relevantes
  const fs = require('fs');
  const path = require('path');
  const outDir = 'C:/Users/oraul/ProyectosWeb/ruta-travel/assets';
  
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  
  console.log('\n=== DESCARGANDO IMÁGENES ===');
  
  for (let i = 0; i < Math.min(images.length, 15); i++) {
    const img = images[i];
    if (!img.src || !img.isLarge) continue;
    
    try {
      const response = await page.evaluate((src) => {
        return fetch(src).then(r => ({ ok: r.ok, status: r.status, type: r.headers.get('content-type') }));
      }, img.src);
      
      if (response.ok) {
        const imageBuffer = await page.evaluate((src) => {
          return fetch(src).then(r => r.blob()).then(blob => {
            return new Promise((resolve) => {
              const reader = new FileReader();
              reader.onloadend = () => resolve(new Uint8Array(reader.result));
              reader.readAsArrayBuffer(blob);
            });
          });
        }, img.src);
        
        const ext = img.src.includes('.jpg') ? 'jpg' : img.src.includes('.png') ? 'png' : 'jpg';
        const filename = `img_${i.toString().padStart(2, '0')}.${ext}`;
        const filepath = `C:/Users/oraul/ProyectosWeb/ruta-travel/assets/${filename}`;
        
        fs.writeFileSync(filepath, Buffer.from(imageBuffer));
        console.log(`✅ ${filename} (${img.width}x${img.height})`);
      }
    } catch (e) {
      console.log(`❌ Imagen ${i}: ${e.message.slice(0, 50)}`);
    }
  }
  
  // También intentar capturar screenshot de la página
  const screenshotPath = 'C:/Users/oraul/ProyectosWeb/ruta-travel/assets/perfil_screenshot.png';
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.log(`\n📸 Screenshot guardado: ${screenshotPath}`);
  
  await browser.close();
})();
