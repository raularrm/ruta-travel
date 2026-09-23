from playwright.sync_api import sync_playwright
import pandas as pd
import json
import time

print("=" * 70)
print("GOOGLE TRENDS — Extracción directa desde la UI con Playwright")
print("=" * 70)

keywords = [
    'agencia de viajes',
    'viajes a Cancún',
    'viajes a Los Cabos',
    'pueblos mágicos',
    'tour tequila México',
    'luna de miel México',
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    # Ir a Google Trends
    print("\n🌐 Navegando a trends.google.com...")
    page.goto('https://trends.google.com/trendingtopic', timeout=30000)
    page.wait_for_timeout(3000)
    
    # Ir al explore
    page.goto('https://trends.google.com/trends/explore?geo=MX&hl=es', timeout=30000)
    page.wait_for_timeout(3000)
    
    # Buscar la área de input para keywords
    print("📝 Buscando campo de entrada de keywords...")
    
    # Intentar encontrar el input por su selector
    selectors_to_try = [
        'input[name="q"]',
        '#input-field',
        '[data-testid="search-input"]',
        'input[placeholder*="search" i]',
        'textarea[name="q"]',
        '.search-box__input',
    ]
    
    input_field = None
    for selector in selectors_to_try:
        try:
            input_field = page.query_selector(selector)
            if input_field:
                print(f"  ✅ Input encontrado con selector: {selector}")
                break
        except:
            pass
    
    if not input_field:
        # Fallback: buscar cualquier input de texto en el área principal
        inputs = page.query_selector_all('input[type="text"], input[type="search"], textarea')
        for inp in inputs:
            try:
                placeholder = inp.get_attribute('placeholder') or ''
                if 'search' in placeholder.lower() or 'trend' in placeholder.lower() or len(placeholder) == 0:
                    input_field = inp
                    print(f"  ✅ Input encontrado (placeholder: '{placeholder[:30]}')")
                    break
            except:
                pass
    
    if input_field:
        # Buscar el botón de búsqueda
        search_btn = page.query_selector('button[type="submit"], .search-btn, [data-testid="search-button"]')
        
        for keyword in keywords:
            print(f"\n🔍 Buscando: '{keyword}'...")
            try:
                # Limpiar el input
                input_field.click()
                page.keyboard.press('Control+a')
                page.keyboard.press('Delete')
                page.wait_for_timeout(500)
                
                # Escribir el keyword
                input_field.fill(keyword)
                page.wait_for_timeout(500)
                
                # Hacer búsqueda
                if search_btn:
                    search_btn.click()
                else:
                    input_field.press('Enter')
                
                page.wait_for_timeout(3000)
                
                # Extraer datos de la tabla/chart
                print("  📊 Extrayendo datos...")
                
                # Intentar extraer de la tabla de datos
                table_data = []
                
                # Opción 1: extraer de elementos de la UI
                try:
                    # Buscar filas de datos o elementos con valores numéricos
                    rows = page.query_selector_all('[role="row"], tr, [class*="row"]')
                    for row in rows:
                        cells = row.query_selector_all('td, th, [role="gridcell"], [class*="cell"]')
                        cell_texts = [c.inner_text() for c in cells]
                        if any(c for c in cell_texts if c and any(c.isdigit() for c in c)):
                            table_data.append(cell_texts)
                except:
                    pass
                
                if table_data:
                    print(f"    Tabla encontrada: {len(table_data)} filas")
                    for row in table_data[:5]:
                        print(f"    {' | '.join(row)}")
                else:
                    # Opción 2: screenshot y análisis
                    print("    Capturando screenshot de la página...")
                    screenshot = page.screenshot()
                    print(f"    Screenshot capturado: {len(screenshot)} bytes")
                
                page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"  Error: {e}")
            
            page.wait_for_timeout(1000)
    else:
        print("❌ No se pudo encontrar el campo de entrada")
    
    browser.close()

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
