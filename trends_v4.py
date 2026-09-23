import requests
import json
import time
from urllib.parse import quote

# Google Trends API endpoint (no oficial pero funcional)
GOOGLE_TRENDS_URL = "https://trends.googleapis.com/v1beta/insights/search"

# Headers para parecer un navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://trends.google.com/',
    'Origin': 'https://trends.google.com',
}

# Endpoint alternativo que usa la UI de Google Trends
# Esta es la URL que usa la interfaz de Google Trends cuando haces una búsqueda
TRENDS_QUERY_URL = "https://trends.google.com/trendingsearch"

def get_trends_data(keywords, timeframe='now-60d'):
    """
    Obtener datos de tendencias mediante la API de Google Trends.
    keywords: lista de términos
    timeframe: formato 'now-60d' (últimos 60 días)
    """
    results = {}
    
    # Usar la API de Google Trends Insights (beta)
    # Esta es la misma API que usa la UI cuando haces búsquedas
    
    for keyword in keywords:
        try:
            # Endpoint de búsqueda de insights
            url = "https://trends.googleapis.com/v1beta/insights/search"
            params = {
                'keyword': keyword,
                'timeframe': timeframe,
                'geo': 'MX',
                'language': 'es',
            }
            
            # Alternativa: usar la URL de la UI de Google Trends
            #Esta es la URL que se usa cuando se consulta en trends.google.com
            
            print(f"  Consultando '{keyword}'...")
            
            # Usar requests directos
            resp = requests.get(
                "https://trends.google.com/trendingsearch",
                params={'q': keyword},
                headers=headers,
                timeout=15
            )
            
            if resp.status_code == 200:
                # La respuesta es HTML, no JSON
                # Extraer datos del HTML si es posible
                print(f"    Respuesta HTML recibida ({len(resp.text)} chars)")
                # No podemos parsear fácilmente, pero al menos confirmamos que funciona
                results[keyword] = {'status': 'ok_html'}
            else:
                print(f"    Código: {resp.status_code}")
                results[keyword] = {'status': 'error', 'code': resp.status_code}
                
        except Exception as e:
            print(f"  Error en '{keyword}': {e}")
            results[keyword] = {'status': 'error', 'msg': str(e)}
        
        time.sleep(1)
    
    return results

def get_trends_via_pytrends_simple():
    """Obtener datos usando pytrends de forma más agresiva con retries"""
    from pytrends.request import TrendReq
    
    results = {}
    
    for timeframe in ['today 1-d', 'today 7-d', 'today 30-d', 'today 60-d']:
        print(f"\n  Probando timeframe: {timeframe}")
        try:
            pyt = TrendReq(hl='es', tz=360)
            pyt.build_payload(
                kw_list=['viajes', 'pueblos mágicos'],
                cat=0,
                timeframe=timeframe,
                geo='MX',
                gprop=''
            )
            data = pyt.interest_over_time()
            if not data.empty:
                print(f"  ✅ Funcionó con {timeframe}!")
                print(f"  Promedio: {data.mean().to_dict()}")
                results[timeframe] = data.mean().to_dict()
                # Si funcionó con uno, probar con más datos
                if timeframe == 'today 7-d':
                    # Probar con las keywords completas
                    pyt2 = TrendReq(hl='es', tz=360)
                    kw_full = ['agencia de viajes', 'viajes a Cancún', 'viajes a Los Cabos', 'pueblos mágicos', 'tour tequila México']
                    pyt2.build_payload(kw_list=kw_full, cat=0, timeframe='today 7-d', geo='MX')
                    data_full = pyt2.interest_over_time()
                    if not data_full.empty:
                        print(f"\n  ✅ Datos completos (7 días):")
                        for col in data_full.columns:
                            print(f"    {col}: {data_full[col].mean():.1f}")
                        results['full_7d'] = data_full.mean().to_dict()
                break
            else:
                print(f"  ⚠️  Datos vacíos")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)
    
    return results

print("=" * 70)
print("GOOGLE TRENDS — Búsqueda de datos reales")
print("=" * 70)

# 1. Intentar con pytrends — timeframes cortos primero
print("\n🔄 Probando pytrends con timeframes cortos...")
pytrends_result = get_trends_via_pytrends_simple()

# 2. Si pytrends funciona, obtener datos más detallados
if pytrends_result:
    print("\n" + "=" * 70)
    print("DATOS OBTENIDOS")
    print("=" * 70)
    
    for timeframe, data in pytrends_result.items():
        if timeframe == 'full_7d':
            print(f"\n📊 Promedios últimos 7 días (México):")
            if isinstance(data, dict):
                for keyword, value in data.items():
                    print(f"  {keyword}: {value}")
        else:
            print(f"\n📊 {timeframe}:")
            if isinstance(data, dict):
                for keyword, value in data.items():
                    print(f"  {keyword}: {value}")
    
    # 3. Intentar obtener datos de región para Estado de México
    if 'full_7d' in pytrends_result:
        print("\n" + "=" * 70)
        print("🔍 INTERÉS POR REGIÓN — Estado de México")
        print("=" * 70)
        try:
            pyt_r = TrendReq(hl='es', tz=360)
            pyt_r.build_payload(
                kw_list=['agencia de viajes', 'pueblos mágicos', 'viajes a Cancún'],
                cat=0,
                timeframe='today 7-d',
                geo='MX'
            )
            region = pyt_r.interest_by_region(resolution='region', inc_geo_url=False, relative_to_country=True)
            
            if not region.empty:
                estados_clave = ['Estado de México', 'Ciudad de México', 'Morelos', 'Puebla', 'Jalisco', 'Michoacán', 'Querétaro', 'Hidalgo']
                print(f"\n  {'Estado':<25} {'Agencia':>8} {'Pueblos Mágicos':>15} {'Cancún':>8}")
                print("  " + "-" * 55)
                for estado in estados_clave:
                    if estado in region.index:
                        row = region.loc[estado]
                        print(f"  {estado:<25} {row[0]:>8.1f} {row[1]:>15.1f} {row[2]:>8.1f}")
        except Exception as e:
            print(f"  Error región: {e}")
    
    # 4. Intentar obtener palabras clave relacionadas
    print("\n" + "=" * 70)
    print("🔗 PALABRAS CLAVE RELACIONADAS")
    print("=" * 70)
    try:
        pyt_q = TrendReq(hl='es', tz=360)
        pyt_q.build_payload(
            kw_list=['agencia de viajes', 'viajes'],
            cat=0,
            timeframe='today 7-d',
            geo='MX'
        )
        related = pyt_q.related_queries()
        
        if not related.empty:
            for kw in related.columns:
                top = related[kw].get('top', None)
                rising = related[kw].get('rising', None)
                if top is not None and not top.empty:
                    print(f"\n  🔗 Relacionadas con '{kw}' — Top:")
                    for i, row in top.head(8).iterrows():
                        print(f"    {row[0]:<35} {row[1]:>8.1f}")
                if rising is not None and not rising.empty:
                    print(f"\n  🔗 Relacionadas con '{kw}' — Tendencia:")
                    for i, row in rising.head(5).iterrows():
                        print(f"    {row[0]:<35} {row[1]}")
    except Exception as e:
        print(f"  Error related: {e}")

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
