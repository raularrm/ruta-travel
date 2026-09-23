const { chromium } = require('playwright');

(async () => {
  console.log('='.repeat(70));
  console.log('GOOGLE TRENDS — Extracción directa desde la UI con Playwright');
  console.log('='.repeat(70));

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  // Keywords para analizar
  const keywords = [
    'agencia de viajes',
    'viajes a Cancún',
    'viajes a Los Cabos',
    'pueblos mágicos',
    'tour tequila México',
    'luna de miel México',
  ];

  // Navegar a Google Trends
  console.log('\n🌐 Navegando a trends.google.com...');
  await page.goto('https://trends.google.com/trends/explore?geo=MX&hl=es', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });
  await page.waitForTimeout(4000);

  // Localizar el campo de entrada de keywords
  console.log('📝 Buscando campo de entrada...');
  
  const inputField = await page.$('textarea[name="q"], input[name="q"], .search-box__input, [data-testid="search-input"]');
  
  if (!inputField) {
    // Fallback: buscar cualquier textarea/input que parezca de búsqueda
    const inputs = await page.$$('textarea, input[type="text"], input[type="search"]');
    for (const inp of inputs) {
      const placeholder = await inp.getAttribute('placeholder') || '';
      const cls = await inp.getAttribute('class') || '';
      if (placeholder.includes('search') || placeholder.includes('keyword') || placeholder === '' || cls.includes('search')) {
        console.log(`  ✅ Input encontrado (placeholder: '${placeholder.slice(0, 50)}')`);
        break;
      }
    }
  }

  if (inputField) {
    // Para cada keyword
    for (const keyword of keywords) {
      console.log(`\n🔍 Buscando: '${keyword}'...`);
      try {
        await inputField.click();
        await page.keyboard.press('Control+a');
        await page.keyboard.press('Delete');
        await page.waitForTimeout(300);
        
        await inputField.fill(keyword);
        await page.waitForTimeout(500);
        
        // Enviar
        const searchBtn = await page.$('button[type="submit"], .search-box__button, [data-testid="search-button"]');
        if (searchBtn) {
          await searchBtn.click();
        } else {
          await inputField.press('Enter');
        }
        
        await page.waitForTimeout(4000);
        
        // Extraer datos
        console.log('  📊 Extrayendo datos...');
        
        // Método 1: Extraer del gráfico/chart si hay datos
        const chartData = await page.evaluate(() => {
          // Buscar elementos con datos de tendencia
          const result = {};
          
          // Buscar la tabla de datos o el área del chart
          const chartArea = document.querySelector('[class*="chart"], [class*="graph"], [class*="timeline"]');
          if (chartArea) {
            result.chartFound = true;
            result.chartClass = chartArea.className;
          }
          
          // Buscar tablas
          const tables = document.querySelectorAll('table');
          if (tables.length > 0) {
            result.tableCount = tables.length;
            const rows = [];
            for (const table of tables) {
              const trs = table.querySelectorAll('tr');
              if (trs.length > 0) {
                for (const tr of trs) {
                  const tds = tr.querySelectorAll('td, th');
                  const row = [];
                  for (const td of tds) {
                    row.push(td.innerText.trim());
                  }
                  if (row.length > 0) rows.push(row);
                }
              }
            }
            result.rows = rows.slice(0, 15);
          }
          
          // Buscar cualquier elemento con números (de la gráfica)
          const numElements = document.querySelectorAll('[class*="number"], [class*="value"], [class*="data"], [class*="bar"]');
          if (numElements.length > 0) {
            result.numElements = numElements.length;
          }
          
          // Texto visible relevante
          const bodyText = document.body.innerText;
          result.bodySnippet = bodyText.slice(0, 3000);
          
          return result;
        });
        
        console.log('  Resultado:', JSON.stringify(chartData, null, 2).slice(0, 1500));
        
        await page.waitForTimeout(1500);
        
      } catch (e) {
        console.log(`  Error: ${e.message.slice(0, 100)}`);
      }
    }
  } else {
    console.log('❌ No se pudo localizar el campo de entrada');
    // Screenshot para diagnosis
    const screenshotPath = '/c/Users/oraul/ProyectosWeb/ruta-travel/trends_screenshot.png';
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 Screenshot guardado: ${screenshotPath}`);
  }

  await browser.close();
  console.log('\n' + '='.repeat(70));
  console.log('✅ Análisis completado');
  console.log('='.repeat(70));
})();
