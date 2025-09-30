"""
Exemplo 2: Análise de mercado com cotações históricas

Este exemplo demonstra:
- Obtenção de cotações históricas
- Cálculo de médias móveis
- Análise de volatilidade
- Identificação de tendências
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List

# Adicionar pasta pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt5_client import MT5TradingClient, TickerResponse


def calcular_media_movel(precos: List[float], periodo: int) -> float:
    """Calcular média móvel simples"""
    if len(precos) < periodo:
        return None
    return sum(precos[-periodo:]) / periodo


def calcular_volatilidade(precos: List[float]) -> float:
    """Calcular volatilidade (desvio padrão dos retornos)"""
    if len(precos) < 2:
        return 0
    
    # Calcular retornos
    retornos = []
    for i in range(1, len(precos)):
        retorno = (precos[i] - precos[i-1]) / precos[i-1]
        retornos.append(retorno)
    
    # Calcular média dos retornos
    media = sum(retornos) / len(retornos)
    
    # Calcular variância
    variancia = sum((r - media) ** 2 for r in retornos) / len(retornos)
    
    # Retornar desvio padrão (volatilidade)
    return (variancia ** 0.5) * 100  # Em percentual


def identificar_tendencia(precos: List[float], ma_curta: int = 10, ma_longa: int = 20) -> str:
    """Identificar tendência baseada em médias móveis"""
    if len(precos) < ma_longa:
        return "Dados insuficientes"
    
    ma_10 = calcular_media_movel(precos, ma_curta)
    ma_20 = calcular_media_movel(precos, ma_longa)
    
    if ma_10 is None or ma_20 is None:
        return "Dados insuficientes"
    
    if ma_10 > ma_20:
        return "Alta (Bullish)"
    elif ma_10 < ma_20:
        return "Baixa (Bearish)"
    else:
        return "Lateral"


async def analisar_simbolo(client: MT5TradingClient, symbol: str, dias: int = 7):
    """Análise completa de um símbolo"""
    
    print(f"\n📊 Analisando {symbol}:")
    print("-" * 40)
    
    # Definir período de análise
    end_date = datetime.now()
    start_date = end_date - timedelta(days=dias)
    
    try:
        # 1. Obter cotações H1 da última semana
        print("1. Obtendo cotações H1...")
        tickers_h1 = await client.get_tickers(
            symbol=symbol,
            date_from=start_date,
            date_to=end_date,
            timeframe=16385  # H1
        )
        
        if not tickers_h1:
            print(f"❌ Nenhuma cotação encontrada para {symbol}")
            return
        
        print(f"   📈 {len(tickers_h1)} cotações obtidas")
        
        # 2. Extrair preços de fechamento
        precos_fechamento = [ticker.close for ticker in tickers_h1]
        precos_maximos = [ticker.high for ticker in tickers_h1]
        precos_minimos = [ticker.low for ticker in tickers_h1]
        
        # 3. Calcular estatísticas básicas
        print("\n2. Estatísticas básicas:")
        preco_atual = precos_fechamento[-1]
        preco_max = max(precos_maximos)
        preco_min = min(precos_minimos)
        variacao_periodo = ((preco_atual - precos_fechamento[0]) / precos_fechamento[0]) * 100
        
        print(f"   💰 Preço atual: {preco_atual:.5f}")
        print(f"   📈 Máximo do período: {preco_max:.5f}")
        print(f"   📉 Mínimo do período: {preco_min:.5f}")
        print(f"   📊 Variação do período: {variacao_periodo:+.2f}%")
        
        # 4. Médias móveis
        print("\n3. Médias móveis:")
        ma_5 = calcular_media_movel(precos_fechamento, 5)
        ma_10 = calcular_media_movel(precos_fechamento, 10)
        ma_20 = calcular_media_movel(precos_fechamento, 20)
        
        if ma_5: print(f"   MA5: {ma_5:.5f}")
        if ma_10: print(f"   MA10: {ma_10:.5f}")
        if ma_20: print(f"   MA20: {ma_20:.5f}")
        
        # 5. Volatilidade
        print("\n4. Análise de volatilidade:")
        volatilidade = calcular_volatilidade(precos_fechamento)
        print(f"   📊 Volatilidade: {volatilidade:.2f}%")
        
        if volatilidade > 2.0:
            vol_status = "🔴 Alta volatilidade"
        elif volatilidade > 1.0:
            vol_status = "🟡 Volatilidade moderada"
        else:
            vol_status = "🟢 Baixa volatilidade"
        
        print(f"   {vol_status}")
        
        # 6. Tendência
        print("\n5. Análise de tendência:")
        tendencia = identificar_tendencia(precos_fechamento)
        print(f"   📈 Tendência: {tendencia}")
        
        # 7. Últimas 5 cotações
        print("\n6. Últimas 5 cotações H1:")
        for i, ticker in enumerate(tickers_h1[-5:], 1):
            print(f"   {i}. {ticker.time.strftime('%d/%m %H:%M')} | "
                  f"O: {ticker.open:.5f} | H: {ticker.high:.5f} | "
                  f"L: {ticker.low:.5f} | C: {ticker.close:.5f}")
        
        # 8. Sugestão baseada na análise
        print("\n7. 💡 Análise resumida:")
        
        if tendencia == "Alta (Bullish)" and volatilidade < 1.5:
            sugestao = "🟢 Cenário favorável para alta"
        elif tendencia == "Baixa (Bearish)" and volatilidade < 1.5:
            sugestao = "🔴 Cenário de baixa estabelecido"
        elif volatilidade > 2.0:
            sugestao = "⚠️ Alta volatilidade - aguardar estabilização"
        else:
            sugestao = "🟡 Mercado lateral - aguardar definição"
        
        print(f"   {sugestao}")
    
    except Exception as e:
        print(f"❌ Erro ao analisar {symbol}: {e}")


async def exemplo_analise_mercado():
    """Exemplo principal de análise de mercado"""
    
    client = MT5TradingClient(
        api_url="http://localhost:8000",
        timeout=30
    )
    
    try:
        async with client:
            print("🚀 Iniciando análise de mercado...")
            
            # Verificar conexão
            health = await client.check_health()
            if not health.mt5_connected:
                print("❌ MT5 não está conectado!")
                return
            
            # Símbolos para análise
            simbolos_analise = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
            
            print(f"\n📊 Analisando {len(simbolos_analise)} símbolos:")
            
            # Analisar cada símbolo
            for symbol in simbolos_analise:
                await analisar_simbolo(client, symbol, dias=7)
            
            # Comparação final
            print("\n" + "=" * 60)
            print("📈 RESUMO COMPARATIVO")
            print("=" * 60)
            
            # Obter variações atuais
            changes = await client.get_daily_changes(simbolos_analise)
            prices = await client.get_current_prices(simbolos_analise)
            
            print("\nDesempenho diário:")
            simbolos_ordenados = sorted(
                changes.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for i, (symbol, change) in enumerate(simbolos_ordenados, 1):
                price = prices.get(symbol, "N/A")
                status = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                print(f"{i}. {status} {symbol}: {price} ({change:+.2f}%)")
            
            print("\n✅ Análise de mercado concluída!")
    
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("MT5 Trading Client - Análise de Mercado")
    print("=" * 60)
    
    # Executar análise
    asyncio.run(exemplo_analise_mercado())