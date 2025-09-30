"""
Exemplo 1: Uso básico do MT5 Trading Client

Este exemplo demonstra o uso básico do cliente para:
- Verificar conexão com a API
- Obter lista de símbolos
- Consultar dados de mercado
- Obter preços atuais
"""
import asyncio
import sys
import os

# Adicionar pasta pai ao path para importar mt5_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt5_client import MT5TradingClient


async def exemplo_basico():
    """Exemplo básico de uso do cliente MT5"""
    
    # Criar cliente (substitua pela URL do seu servidor)
    client = MT5TradingClient(
        api_url="http://localhost:8000",
        timeout=30,
        log_level="INFO"
    )
    
    try:
        async with client:
            print("🚀 Conectando à API MT5...")
            
            # 1. Verificar saúde da API
            print("\n1️⃣ Verificando saúde da API:")
            health = await client.check_health()
            print(f"   Status: {health.status}")
            print(f"   MT5 Connected: {health.mt5_connected}")
            
            if not health.mt5_connected:
                print("❌ MT5 não está conectado no servidor!")
                return
            
            # 2. Obter símbolos disponíveis
            print("\n2️⃣ Obtendo símbolos disponíveis:")
            symbols = await client.get_symbols()
            print(f"   Total de símbolos: {len(symbols)}")
            
            # Mostrar primeiros 10 símbolos
            print("   Primeiros 10 símbolos:")
            for i, symbol in enumerate(symbols[:10]):
                print(f"   {i+1:2d}. {symbol.name} - {symbol.description}")
            
            # 3. Obter apenas pares Forex
            print("\n3️⃣ Obtendo pares Forex:")
            forex_pairs = await client.get_forex_pairs()
            print(f"   Pares Forex encontrados: {len(forex_pairs)}")
            
            # 4. Obter principais pares
            print("\n4️⃣ Principais pares de moedas:")
            major_pairs = await client.get_major_pairs()
            for pair in major_pairs:
                print(f"   {pair.name} - {pair.description}")
            
            # 5. Dados de mercado de símbolos específicos
            print("\n5️⃣ Dados de mercado detalhados:")
            test_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
            
            for symbol_name in test_symbols:
                market_data = await client.get_market_data(symbol_name)
                if market_data:
                    print(f"   {symbol_name}:")
                    print(f"     Preço atual: {market_data.current_price}")
                    print(f"     Bid: {market_data.symbol.bid}")
                    print(f"     Ask: {market_data.symbol.ask}")
                    print(f"     Spread: {market_data.symbol.spread}")
                    if market_data.pct_change:
                        print(f"     Variação: {market_data.pct_change.pct_change:+.2f}%")
                else:
                    print(f"   {symbol_name}: Não encontrado")
            
            # 6. Preços atuais de múltiplos símbolos
            print("\n6️⃣ Preços atuais de múltiplos símbolos:")
            prices = await client.get_current_prices(test_symbols)
            for symbol, price in prices.items():
                print(f"   {symbol}: {price}")
            
            # 7. Variações diárias
            print("\n7️⃣ Variações diárias:")
            changes = await client.get_daily_changes(test_symbols)
            for symbol, change in changes.items():
                status = "🔴" if change < -0.1 else "🟢" if change > 0.1 else "⚪"
                print(f"   {status} {symbol}: {change:+.2f}%")
            
            print("\n✅ Exemplo básico concluído com sucesso!")
    
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("MT5 Trading Client - Exemplo Básico")
    print("=" * 60)
    
    # Executar exemplo
    asyncio.run(exemplo_basico())