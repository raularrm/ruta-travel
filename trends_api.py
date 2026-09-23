import requests
import json
import time

# Intentar con la API de Google Trends (Google Cloud)
# Esta es la API oficial de Google Trends

print("=" * 70)
print("GOOGLE TRENDS — API de Google Cloud (tendencias)")
print("=" * 70)

# Google Trends API endpoint
API_URL = "https://trends.googleapis.com/v1beta/insights/search"

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# Intentar con queries específicos
keywords = [
    'agencia de viajes',
    'viajes a Cancún',
    'viajes a Los Cabos', 
    'pueblos mágicos',
]

for keyword in keywords:
    print(f"\n🔍 '{keyword}'...")
    try:
        # API de Google Trends Insights
        url = "https://trends.google.com/trendingsearch"
        params = {
            'q': keyword,
            'geo': 'MX',
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"  Respuesta: {len(resp.text)} chars")
            # La respuesta es HTML de la UI de trends
            # Extraer datos si es posible
            if 'interestovertime' in resp.text.lower() or 'chart' in resp.text.lower():
                print("  ✅ Contiene datos de tendencia")
        else:
            print(f"  Cuerpo: {resp.text[:200]}")
            
    except Exception as e:
        print(f"  Error: {e}")

# Alternativa 2: Usar la API de Google Trends v1
print("\n" + "=" * 70)
print("API Alternativa: Google Trends v1beta")
print("=" * 70)

try:
    url = "https://trends.googleapis.com/v1beta/insights/search"
    payload = {
        "requests": [
            {
                "request_id": "1",
                "keyword": "agencia de viajes",
                "geo": "MX",
                "timeframe": "now-60d"
            },
            {
                "request_id": "2", 
                "keyword": "viajes a Cancún",
                "geo": "MX",
                "timeframe": "now-60d"
            }
        ]
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response: {resp.text[:1000]}")
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Alternativa 3: Google Trends API pública (no requiere clave)
print("\n" + "=" * 70)
print("API Pública: Google Trends (sin auth)")
print("=" * 70)

try:
    # Endpoint que usa la UI de Google Trends
    url = "https://trends.google.com/trendingsearch"
    
    # Query con formato de búsqueda
    search_url = f"{url}?q=agencia+de+viajes&geo=MX&hl=es"
    resp = requests.get(search_url, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('content-type', 'unknown')}")
    
    if resp.status_code == 200:
        # La respuesta es HTML — extraer datos de interés
        if 'interestovertime' in resp.text:
            print("✅ La página contiene gráfico de interés sobre tiempo")
        
        # Intentar encontrar datos JSON embebidos
        import re
        json_patterns = re.findall(r'\{[^}]*"interest"[^{}]*\}', resp.text)
        if json_patterns:
            print(f"✅ Encontró {len(json_patterns)} patrones JSON")
            for p in json_patterns[:2]:
                print(f"  {p[:200]}")
        
except Exception as e:
    print(f"Error: {e}")

# Alternativa 4: Intentar con curl directamente
print("\n" + "=" * 70)
print("Test con requests más completa")
print("=" * 70)

try:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://trends.google.com/',
        'Connection': 'keep-alive',
    })
    
    # Primero navegar a la página principal para obtener cookies
    print("  Navegando a trends.google.com...")
    resp_main = session.get('https://trends.google.com/trendingtopic', timeout=15)
    print(f"  Main page: {resp_main.status_code} ({len(resp_main.text)} chars)")
    
    # Luego hacer la búsqueda
    print("  Haciendo búsqueda...")
    resp_search = session.get(
        'https://trends.google.com/trendingsearch',
        params={'q': 'agencia de viajes', 'geo': 'MX'},
        timeout=15
    )
    print(f"  Search: {resp_search.status_code} ({len(resp_search.text)} chars)")
    
    if resp_search.status_code == 200:
        print("  ✅ Página de búsqueda cargada")
        # Buscar datos de interés en el HTML
        if 'interestovertime-service' in resp_search.text:
            print("  ✅ Contiene servicio de interés sobre tiempo")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
