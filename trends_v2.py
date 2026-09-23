from pytrends.request import TrendReq
import requests
from fake_useragent import UserAgent
import time
import json

# User-Agent realista
ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
}

# Crear sesión con headers personalizados
session = requests.Session()
session.headers.update(headers)

# Inicializar pytrends con la sesión personalizada
pytrends = TrendReq(hl='es-MX', tz=360, timeout=120)

# Sobrescribir el método de conexión para usar nuestra sesión
original_connections = pytrends.connections

def custom_connect(keyword_list, export_cookie=True, **kwargs):
    """Conexión personalizada con headers realistas"""
    try:
        # Usar la sesión con headers
        pytrends.sess = session
        return pytrends._build_payload(keyword_list, **kwargs)
    except Exception as e:
        print(f"  Fallback: {e}")
        return pytrends._build_payload(keyword_list, **kwargs)

keywords_prueba = ['viajes a Cancún', 'pueblos mágicos']

print("=" * 70)
print("GOOGLE TRENDS — Intento con headers personalizados")
print("=" * 70)

for attempt in range(3):
    print(f"\n🔍 Intento {attempt + 1}/3...")
    try:
        pytrends.build_payload(
            kw_list=keywords_prueba,
            cat=0,
            timeframe='now-60d',
            geo='MX',
            gprop=''
        )
        time_data = pytrends.interest_over_time()
        if not time_data.empty:
            print(f"✅ Éxito! Últimos datos:")
            print(time_data.tail(5))
            break
        else:
            print("⚠️  Datos vacíos")
    except Exception as e:
        print(f"  Error: {e}")
        time.sleep(3)
else:
    print("\n❌ Todos los intentos fallaron. Probando alternativa...")

# Alternativa: usar pytrends con configuración manual
print("\n🔄 Probando configuración alternativa...")
try:
    from pytrends.request import TrendReq
    
    # Versión más simple sin hl específico
    pytrends2 = TrendReq(hl='mx', tz=360)
    
    pytrends2.build_payload(
        kw_list=['viajes'],
        cat=0,
        timeframe='today 60-d',
        geo='MX',
        gprop=''
    )
    data = pytrends2.interest_over_time()
    if not data.empty:
        print("✅ Alternativa funcionó!")
        print(data.tail(10))
    else:
        print("⚠️  Datos vacíos en alternativa")
except Exception as e:
    print(f"  Error: {e}")

# Última alternativa: requests directos a la API de Google Trends
print("\n🔄 Probando requests directos...")
try:
    from pytrends.exceptions import ResponseError
    
    pytrends3 = TrendReq(hl='es-MX', tz=360, session=session)
    
    # Intentar con timeframe más corto (30 días)
    pytrends3.build_payload(
        kw_list=['viajes a Cancún', 'pueblos mágicos'],
        timeframe='today 30-d',
        geo='MX'
    )
    data30 = pytrends3.interest_over_time()
    if not data30.empty:
        print("✅ Con 30 días funcionó!")
        print(data30.tail(5))
        print(f"\nPromedio 30 días:")
        for col in data30.columns:
            print(f"  {col}: {data30[col].mean():.1f}")
except ResponseError as e:
    print(f"  ResponseError: {e}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("RESULTADO FINAL")
print("=" * 70)
