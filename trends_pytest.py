from pytrends.request import TrendReq
import time

print("=" * 70)
print("GOOGLE TRENDS — ÚltimaIntentos con pytrends")
print("=" * 70)

# Configuraciones alternativas
configs = [
    {'hl': 'en-US', 'tz': 0},
    {'hl': 'es', 'tz': 360},
    {'hl': 'mx', 'tz': 360},
]

keywords_test = ['viajes', 'pueblos mágicos']

for i, cfg in enumerate(configs, 1):
    print(f"\n🔍 Configuración {i}: {cfg}")
    try:
        pyt = TrendReq(hl=cfg['hl'], tz=cfg['tz'])
        pyt.build_payload(
            kw_list=keywords_test,
            cat=0,
            timeframe='today 1-d',
            geo='MX'
        )
        data = pyt.interest_over_time()
        if not data.empty:
            print(f"✅ Funcionó con hl={cfg['hl']}!")
            print(f"  Datos: {data.tail(3).to_string()}")
            print(f"  Promedio: {data.mean().to_dict()}")
            break
        else:
            print(f"⚠️  Datos vacíos")
    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
    time.sleep(2)

# Si ninguna funciona, intentar con timeframes diferentes
if not data.empty:
    print("\n✅ Usando datos existentes")
else:
    print("\n🔄 Intentando con diferentes timeframes...")
    for timeframe in ['today 1-d', 'today 7-d', 'today 30-d']:
        try:
            pyt = TrendReq(hl='es', tz=360)
            pyt.build_payload(
                kw_list=['viajes'],
                cat=0,
                timeframe=timeframe,
                geo='MX'
            )
            data = pyt.interest_over_time()
            if not data.empty:
                print(f"✅ {timeframe} funcionó!")
                print(f"  Promedio: {data.mean().to_dict()}")
                break
        except Exception as e:
            print(f"  {timeframe}: {str(e)[:80]}")
        time.sleep(2)

print("\n" + "=" * 70)
print("✅ Análisis completado")
print("=" * 70)
