from playwright.sync_api import sync_playwright

print("=" * 70)
print("GOOGLE TRENDS — Playwright con navegación interactiva")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 1000},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Ir a Google Trends Explore
    print("🌐 Navegando a Google Trends...")
    page.goto('https://trends.google.com/trendingtopic', timeout=60000)
    page.wait_for_timeout(8000)
    
    # Capturar screenshot
    print("📸 Capturando screenshot...")
    page.screenshot(path='C:/Users/oraul/ProyectosWeb/ruta-travel/trends_debug.png')
    print("✅ Screenshot capturado")
    
    # Extraer título y texto visible
    title = page.title()
    print(f"\nTítulo: {title}")
    
    body_text = page.evaluate('document.body.innerText')
    print(f"Texto visible: {body_text[:2000]}")
    
    browser.close()

print("\n✅ Análisis completado")
