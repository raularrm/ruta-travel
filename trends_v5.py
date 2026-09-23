import requests
from curl_cffi import requests as curl_requests
import json
import time
from fake_useragent import UserAgent

ua = UserAgent()

print("=" * 70)
print("GOOGLE TRENDS — Usando curl_cffi (Chromium impersonation)")
print("=" * 70)

# Usar curl_cffi que emula Chromium
session = curl_requests.Session(impersonate="chrome120")

keywords_base = ['viajes', 'pueblos mágicos', 'agencia de viajes']

# 1. Primero probar con timeframes cortos
print("\n🔄 Probando con timeframes cortos...")
for timeframe in ['today 1-d', 'today 7-d', 'today 30-d']:
    try:
        from pytrends.request import TrendReq
        
        # Usar curl_cffi como session de requests
        pyt = TrendReq(hl='es', tz=360)
        pyt.sess = session  # Sobrescribir la session
        
        pyt.build_payload(
            kw_list=keywords_base,
            cat=0,
            timeframe=timeframe,
            geo='MX',
            gprop=''
        )
        data = pyt.interest_over_time()
        if not data.empty:
            print(f"✅ {timeframe} — Funcionó!")
            print(f"  Promedio: {data.mean().round(1).to_dict()}")
            break
        else:
            print(f"⚠️  {timeframe} — Datos vacíos")
    except Exception as e:
        print(f"  {timeframe} — Error: {str(e)[:80]}")

# 2. Si funciona con uno, obtener datos completos
print("\n" + "=" * 70)
print("📊 DATOS COMPLETOS")
print("=" * 70)

try:
    from pytrends.request import TrendReq
    
    pyt_full = TrendReq(hl='es', tz=360)
    pyt_full.sess = session
    
    kw_full = [
        'agencia de viajes',
        'viajes a Cancún',
        'viajes a Los Cabos',
        'pueblos mágicos',
        'tour tequila México',
        'luna de miel México',
    ]
    
    pyt_full.build_payload(
        kw_list=kw_full,
        cat=0,
        timeframe='today 60-d',
        geo='MX',
        gprop=''
    )
    data_full = pyt_full.interest_over_time()
    
    if not data_full.empty:
        print(f"\n✅ Datos de los últimos 60 días (México):")
        print(f"\n{'Fecha':<12} {'Agencia':>8} {'Cancún':>8} {'Cabos':>8} {'Pueblos Mág':>12} {'Tequila':>8} {'Luna Miel':>10}")
        print("-" * 75)
        
        for i, (date, row) in enumerate(data_full.iterrows()):
            if i % 5 == 0:  # Cada 5 días
                date_str = str(date)[:10]
                print(f"{date_str:<12} {row[0]:>8.1f} {row[1]:>8.1f} {row[2]:>8.1f} {row[3]:>12.1f} {row[4]:>8.1f} {row[5]:>10.1f}")
        
        print(f"\n📊 PROMEDIOS ÚLTIMOS 60 DÍAS:")
        for col in data_full.columns:
            print(f"  {col:<20}: {data_full[col].mean():.1f} (máx: {data_full[col].max()})")
        
        # Calcular promedio por mes
        data_full['mes'] = [d.month for d in data_full.index]
        for mes in [8, 9]:
            mes_data = data_full[data_full['mes'] == mes]
            if not mes_data.empty:
                print(f"\n📊 Mes {mes} (agosto/sep):")
                for col in data_full.columns:
                    print(f"  {col:<20}: {mes_data[col].mean():.1f}")
        
        # Guardar datos
        data_full.to_csv('/c/Users/oraul/ProyectosWeb/ruta-travel/trends_60d_real.csv')
        print(f"\n💾 Datos guardados en trends_60d_real.csv")
        
    else:
        print("⚠️  Datos vacíos")
        
except Exception as e:
    print(f"Error: {e}")

# 3. Datos por región
print("\n" + "=" * 70)
print("📍 INTERÉS POR REGIÓN")
print("=" * 70)

try:
    pyt_r = TrendReq(hl='es', tz=360)
    pyt_r.sess = session
    
    pyt_r.build_payload(
        kw_list=['agencia de viajes', 'pueblos mágicos', 'viajes a Cancún'],
        cat=0,
        timeframe='today 60-d',
        geo='MX'
    )
    region = pyt_r.interest_by_region(
        resolution='region',
        inc_geo_url=False,
        relative_to_country=True
    )
    
    if not region.empty:
        print(f"\n  {'Estado':<25} {'Agencia':>8} {'Pueblos Mágicos':>15} {'Cancún':>8}")
        print("  " + "-" * 55)
        
        estados_interes = ['Estado de México', 'Ciudad de México', 'Morelos', 'Puebla', 'Jalisco', 'Michoacán', 'Querétaro', 'Hidalgo', 'Veracruz']
        
        for estado in estados_interes:
            if estado in region.index:
                row = region.loc[estado]
                print(f"  {estado:<25} {row[0]:>8.1f} {row[1]:>15.1f} {row[2]:>8.1f}")
    else:
        print("⚠️  Datos de región vacíos")
        
except Exception as e:
    print(f"Error región: {e}")

# 4. Palabras clave relacionadas
print("\n" + "=" * 70)
print("🔗 PALABRAS CLAVE RELACIONADAS")
print("=" * 70)

try:
    pyt_rel = TrendReq(hl='es', tz=360)
    pyt_rel.sess = session
    
    pyt_rel.build_payload(
        kw_list=['agencia de viajes', 'viajes'],
        cat=0,
        timeframe='today 60-d',
        geo='MX'
    )
    related = pyt_rel.related_queries()
    
    if not related.empty:
        for kw in related.columns:
            top = related[kw].get('top', None)
            rising = related[kw].get('rising', None)
            if top is not None and not top.empty:
                print(f"\n  🔗 Relacionadas con '{kw}' — Top (volumen alto):")
                for i, row in top.head(10).iterrows():
                    print(f"    {row[0]:<35} {row[1]:>8.1f}")
            if rising is not None and not rising.empty:
                print(f"\n  🔗 Relacionadas con '{kw}' — En tendencia (crecimiento):")
                for i, row in rising.head(6).iterrows():
                    print(f"    {row[0]:<35} {row[1]}")
    else:
        print("⚠️  Datos de relaciones vacíos")
        
except Exception as e:
    print(f"Error related: {e}")

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
