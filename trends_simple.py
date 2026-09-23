from playwright.sync_api import sync_playwright
import time

print("=" * 70)
print("GOOGLE TRENDS — Extraer datos con Playwright")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    # Ir a Google Trends
    print("🌐 Navegando a Google Trends...")
    try:
        page.goto('https://trends.google.com/trends/explore?geo=MX&hl=es', timeout=30000)
        page.wait_for_load_state('domcontentloaded', timeout=20000)
        time.sleep(3)
        
        # Capturar datos
        title = page.title()
        print(f"Título: {title}")
        
        # Extraer contenido visible
        data = page.evaluate('''() => {
            return {
                title: document.title,
                bodyText: document.body.innerText.slice(0, 5000),
                url: window.location.href
            };
        }''')
        
        print(f"\n📄 Contenido:")
        print(data['bodyText'][:3000])
        
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()

print("\n✅ Análisis completado")
