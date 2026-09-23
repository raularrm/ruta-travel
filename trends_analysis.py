from pytrends.request import TrendReq
import json
import time

# Inicializar pytrends — usa México como geolocalización
pytrends = TrendReq(hl='es-MX', tz=360)

# Palabras clave relevantes para Ruta Travel — Toluca / Edomex
keywords_local = [
    'agencia de viajes Toluca',
    'agencia de viajes Tenango del Valle',
    'viajes desde Toluca',
    'excursiones Tenango del Valle',
    'Ruta Travel',
    'Pueblo Mágico cerca de Toluca',
    'Teotihuacan tour',
    'viajes a Cancún desde Toluca',
    'viajes a Los Cabos desde Estado de México',
    'pueblos mágicos México',
    'tour tequila México',
    'luna de miel México',
]

keywords_generales = [
    'agencia de viajes',
    'viajes',
    'viajes a Cancún',
    'viajes a Los Cabos',
    'pueblos mágicos',
]

print("=" * 70)
print("GOOGLE TRENDS — DATOS REALES (Últimos 60 días, México)")
print("=" * 70)

# 1. Datos de interés por región (estados de México)
print("\n📍 INTERÉS POR REGIÓN — Estado de México vs otros estados")
print("-" * 70)

try:
    pytrends.build_payload(
        kw_list=['agencia de viajes', 'viajes a Cancún', 'viajes a Los Cabos', 'pueblos mágicos'],
        cat=0,
        timeframe='now-60d',
        geo='MX',
        gprop=''
    )
    region_data = pytrends.interest_by_region(
        resolution='region',
        inc_geo_url=True,
        relative_to_country=True
    )
    
    # Filtrar solo Estado de México, CDMX, y estados cercanos
    estados_interes = ['Estado de México', 'Ciudad de México', 'Morelos', 'Puebla', 'Michoacán', 'Jalisco']
    
    print(f"\n{'Estado':<25} {'Agencia':>8} {'Cancún':>8} {'Cabos':>8} {'Pueblos Mágicos':>15}")
    print("-" * 70)
    
    for estado in estados_interes:
        if estado in region_data.index:
            row = region_data.loc[estado]
            print(f"{estado:<25} {row[0]:>8.1f} {row[1]:>8.1f} {row[2]:>8.1f} {row[3]:>15.1f}")
    
    # Guardar datos de Estado de México
    if 'Estado de México' in region_data.index:
        em_data = region_data.loc['Estado de México'].to_dict()
        print(f"\n📊 Estado de México — Intereses relativos (1-100):")
        for k, v in em_data.items():
            print(f"  {k}: {v}")
        
except Exception as e:
    print(f"Error en región: {e}")

# 2. Tendencia temporal — últimos 60 días
print("\n\n📈 TENDENCIA TEMPORAL — Últimos 60 días (México)")
print("-" * 70)

try:
    pytrends.build_payload(
        kw_list=['agencia de viajes', 'viajes a Cancún', 'viajes a Los Cabos', 'pueblos mágicos'],
        cat=0,
        timeframe='now-60d',
        geo='MX',
        gprop=''
    )
    time_data = pytrends.interest_over_time()
    
    if not time_data.empty:
        print(f"\n{'Fecha':<12} {'Agencia':>8} {'Cancún':>8} {'Cabos':>8} {'Pueblos Mág':>12}")
        print("-" * 55)
        
        # Mostrar datos semanales (cada 7 días)
        for i, (date, row) in enumerate(time_data.iterrows()):
            if i % 7 == 0:  # Cada semana
                date_str = str(date)[:10]
                print(f"{date_str:<12} {row[0]:>8.1f} {row[1]:>8.1f} {row[2]:>8.1f} {row[3]:>12.1f}")
        
        # Promedio de los últimos 60 días
        print(f"\n📊 Promedio últimos 60 días (México):")
        for col in time_data.columns:
            print(f"  {col}: {time_data[col].mean():.1f}")
        
        # Promedio de agosto vs septiembre
        time_data['mes'] = time_data.index.month
        ago_avg = time_data[time_data['mes'] == 8].mean(numeric_only=True)
        sep_avg = time_data[time_data['mes'] == 9].mean(numeric_only=True)
        
        if len(ago_avg) > 0 and len(sep_avg) > 0:
            print(f"\n📊 Comparativa Agosto vs Septiembre 2026:")
            print(f"  {'Término':<20} {'Agosto':>10} {'Septiembre':>12} {'Cambio':>10}")
            print("  " + "-" * 55)
            for col in time_data.columns:
                a = ago_avg[col] if col in ago_avg else 0
                s = sep_avg[col] if col in sep_avg else 0
                change = ((s - a) / (a + 0.001)) * 100
                print(f"  {col:<20} {a:>10.1f} {s:>12.1f} {change:>+10.1f}%")
        
        # Guardar para archivo
        time_data.to_csv('/c/Users/oraul/ProyectosWeb/ruta-travel/trends_60d_mexico.csv')
        print(f"\n💾 Datos guardados en trends_60d_mexico.csv")
    
except Exception as e:
    print(f"Error en tiempo: {e}")

# 3. Palabras clave relacionadas (para lectura y descubrir términos relevantes)
print("\n\n🔗 PALABRAS CLAVE RELACIONADAS — 'agencia de viajes' (México, 60 días)")
print("-" * 70)

try:
    pytrends.build_payload(
        kw_list=['agencia de viajes'],
        cat=0,
        timeframe='now-60d',
        geo='MX',
        gprop=''
    )
    related = pytrends.related_queries()
    
    if not related.empty and 'agencia de viajes' in related.columns:
        top = related['agencia de viajes'].get('top', None)
        rising = related['agencia de viajes'].get('rising', None)
        
        if top is not None and not top.empty:
            print("\n📌 Top relacionadas (volumen alto):")
            for i, row in top.head(10).iterrows():
                print(f"  {row[0]:<40} {row[1]:>8.1f}")
        
        if rising is not None and not rising.empty:
            print("\n📌 Relacionadas en tendencia (crecimiento):")
            for i, row in rising.head(10).iterrows():
                print(f"  {row[0]:<40} {row[1]:>8}")
        
except Exception as e:
    print(f"Error en related: {e}")

# 4. Palabras clave relacionadas — "viajes"
print("\n\n🔗 PALABRAS CLAVE RELACIONADAS — 'viajes' (México, 60 días)")
print("-" * 70)

try:
    pytrends.build_payload(
        kw_list=['viajes'],
        cat=0,
        timeframe='now-60d',
        geo='MX',
        gprop=''
    )
    related_v = pytrends.related_queries()
    
    if not related_v.empty and 'viajes' in related_v.columns:
        top_v = related_v['viajes'].get('top', None)
        rising_v = related_v['viajes'].get('rising', None)
        
        if top_v is not None and not top_v.empty:
            print("\n📌 Top relacionadas (volumen alto):")
            for i, row in top_v.head(15).iterrows():
                print(f"  {row[0]:<40} {row[1]:>8.1f}")
        
        if rising_v is not None and not rising_v.empty:
            print("\n📌 Relacionadas en tendencia (crecimiento):")
            for i, row in rising_v.head(10).iterrows():
                print(f"  {row[0]:<40} {row[1]:>8}")
        
except Exception as e:
    print(f"Error en related_v: {e}")

# 5. Términos específicos de la zona — búsqueda por región
print("\n\n📍 INTERÉS POR CIUDAD — Términos locales (México, 60 días)")
print("-" * 70)

try:
    pytrends.build_payload(
        kw_list=['agencia de viajes Toluca', 'Pueblo Mágico cerca de Toluca', 'Teotihuacan tour'],
        cat=0,
        timeframe='now-60d',
        geo='MX',
        gprop=''
    )
    city_data = pytrends.interest_by_region(
        resolution='metrostats',  # Más granular
        inc_geo_url=True,
        relative_to_country=True
    )
    
    if not city_data.empty:
        print(f"\n{'Ciudad/Región':<30} {'Agencia Toluca':>15} {'Pueblo Mágico':>15} {'Teotihuacan':>12}")
        print("-" * 75)
        
        for idx, row in city_data.head(15).iterrows():
            name = str(idx)[:28]
            print(f"{name:<30} {row[0]:>15.1f} {row[1]:>15.1f} {row[2]:>12.1f}")
    
except Exception as e:
    print(f"Error en ciudades: {e}")

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
