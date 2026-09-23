from pytrends.request import TrendReq
import time

print("=" * 70)
print("GOOGLE TRENDS — Datos reales México, últimos 60 días")
print("=" * 70)

# Intentar con varios configuraciones
keywords_varias = [
    ['viajes a Cancún', 'pueblos mágicos'],
    ['agencia de viajes', 'viajes'],
    ['viajes a Los Cabos', 'tour tequila México'],
]

for attempt, kw_list in enumerate(keywords_varias, 1):
    print(f"\n🔍 Intento {attempt} con: {kw_list}")
    try:
        pytrends = TrendReq(hl='mx', tz=360)
        pytrends.build_payload(
            kw_list=kw_list,
            cat=0,
            timeframe='today 60-d',
            geo='MX',
            gprop=''
        )
        data = pytrends.interest_over_time()
        if not data.empty:
            print(f"✅ Éxito con {kw_list}")
            print(f"\n📊 Últimos datos:")
            print(data.tail(10).to_string())
            print(f"\n📊 Promedio 60 días:")
            for col in data.columns:
                print(f"  {col}: {data[col].mean():.1f} (máximo: {data[col].max()})")
        else:
            print("⚠️  Datos vacíos")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
