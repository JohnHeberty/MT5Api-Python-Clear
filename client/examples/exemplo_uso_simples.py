"""
Exemplo 3: Uso simples (síncrono) do cliente

Este exemplo demonstra o uso da interface síncrona para:
- Scripts simples sem async/await
- Monitoramento básico
- Relatórios rápidos
"""
import sys
import os
import time
from datetime import datetime

# Adicionar pasta pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mt5_client import SimpleMT5Client


def exemplo_uso_simples():
    """Exemplo de uso da interface síncrona"""
    
    print("🚀 Conectando ao MT5 (modo síncrono)...")
    
    # Usar cliente simples com context manager
    with SimpleMT5Client(api_url="http://localhost:8000") as client:
        
        try:
            # 1. Verificar conexão
            print("\n1️⃣ Verificando conexão:")
            health = client.check_health()
            print(f"   Status: {health.status}")
            
            if not health.mt5_connected:
                print("❌ MT5 não está conectado!")
                return
            
            # 2. Obter símbolos
            print("\n2️⃣ Obtendo símbolos:")
            symbols = client.get_symbols()
            print(f"   Total: {len(symbols)} símbolos")
            
            # 3. Listar principais pares
            principais_pares = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "NZDUSD"]
            
            print(f"\n3️⃣ Verificando disponibilidade dos principais pares:")
            pares_disponiveis = []
            
            for pair in principais_pares:
                symbol_info = None
                # Procurar o par na lista de símbolos
                for symbol in symbols:
                    if symbol.name == pair:
                        symbol_info = symbol
                        break
                
                if symbol_info:
                    pares_disponiveis.append(pair)
                    print(f"   ✅ {pair} - {symbol_info.description}")
                else:
                    print(f"   ❌ {pair} - Não disponível")
            
            if not pares_disponiveis:
                print("\n❌ Nenhum par principal disponível!")
                return
            
            # 4. Obter preços atuais
            print(f"\n4️⃣ Preços atuais dos pares disponíveis:")
            try:
                prices = client.get_current_prices(pares_disponiveis)
                for symbol, price in prices.items():
                    print(f"   💰 {symbol}: {price}")
            except Exception as e:
                print(f"   ❌ Erro ao obter preços: {e}")
            
            # 5. Obter variações do dia
            print(f"\n5️⃣ Variações diárias:")
            try:
                changes = client.get_daily_changes(pares_disponiveis)
                for symbol, change in changes.items():
                    if change > 0:
                        status = "🟢 ↗"
                    elif change < 0:
                        status = "🔴 ↘"
                    else:
                        status = "⚪ →"
                    
                    print(f"   {status} {symbol}: {change:+.2f}%")
            except Exception as e:
                print(f"   ❌ Erro ao obter variações: {e}")
            
            print(f"\n✅ Consulta concluída com sucesso!")
        
        except Exception as e:
            print(f"❌ Erro durante execução: {e}")


def exemplo_monitoramento_continuo():
    """Exemplo de monitoramento contínuo simples"""
    
    print("\n🔄 Iniciando monitoramento contínuo...")
    print("   (Pressione Ctrl+C para parar)")
    
    simbolos_monitorar = ["EURUSD", "GBPUSD"]
    
    try:
        with SimpleMT5Client(api_url="http://localhost:8000") as client:
            
            # Verificar conexão inicial
            health = client.check_health()
            if not health.mt5_connected:
                print("❌ MT5 não está conectado!")
                return
            
            contador = 0
            
            while True:
                contador += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"\n📊 [{timestamp}] Atualização #{contador}:")
                
                try:
                    # Obter preços atuais
                    prices = client.get_current_prices(simbolos_monitorar)
                    
                    for symbol, price in prices.items():
                        print(f"   {symbol}: {price}")
                    
                    # Aguardar 10 segundos
                    print("   ⏳ Aguardando 10 segundos...")
                    time.sleep(10)
                
                except KeyboardInterrupt:
                    print("\n⏹️ Monitoramento interrompido pelo usuário")
                    break
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    print("   ⏳ Aguardando 30 segundos antes de tentar novamente...")
                    time.sleep(30)
    
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")


def exemplo_relatorio_rapido():
    """Gerar relatório rápido de mercado"""
    
    print("\n📋 Gerando relatório rápido de mercado...")
    
    with SimpleMT5Client(api_url="http://localhost:8000") as client:
        
        try:
            # Obter dados
            health = client.check_health()
            symbols = client.get_symbols()
            
            # Definir símbolos para relatório
            principais_pares = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
            
            # Filtrar pares disponíveis
            pares_disponiveis = []
            for pair in principais_pares:
                if any(s.name == pair for s in symbols):
                    pares_disponiveis.append(pair)
            
            if pares_disponiveis:
                prices = client.get_current_prices(pares_disponiveis)
                changes = client.get_daily_changes(pares_disponiveis)
            
            # Gerar relatório
            print("\n" + "=" * 50)
            print("📊 RELATÓRIO DE MERCADO MT5")
            print("=" * 50)
            print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"🔗 Status API: {health.status}")
            print(f"📈 Total símbolos: {len(symbols)}")
            print(f"💱 Pares analisados: {len(pares_disponiveis)}")
            
            if pares_disponiveis:
                print(f"\n💰 PREÇOS ATUAIS:")
                print("-" * 30)
                for symbol in pares_disponiveis:
                    price = prices.get(symbol, "N/A")
                    change = changes.get(symbol, 0)
                    trend = "↗️" if change > 0.1 else "↘️" if change < -0.1 else "→"
                    print(f"{symbol:<8} {price:<10} {trend} {change:+6.2f}%")
                
                # Estatísticas resumidas
                valid_changes = [c for c in changes.values() if c != 0]
                if valid_changes:
                    avg_change = sum(valid_changes) / len(valid_changes)
                    max_change = max(valid_changes)
                    min_change = min(valid_changes)
                    
                    print(f"\n📊 RESUMO ESTATÍSTICO:")
                    print("-" * 30)
                    print(f"Variação média: {avg_change:+.2f}%")
                    print(f"Maior alta:     {max_change:+.2f}%")
                    print(f"Maior baixa:    {min_change:+.2f}%")
            
            print("=" * 50)
            print("✅ Relatório gerado com sucesso!")
        
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("MT5 Trading Client - Uso Simples (Síncrono)")
    print("=" * 60)
    
    # Menu de opções
    print("\nEscolha uma opção:")
    print("1. Exemplo básico")
    print("2. Monitoramento contínuo") 
    print("3. Relatório rápido")
    
    try:
        opcao = input("\nDigite o número da opção (1-3): ").strip()
        
        if opcao == "1":
            exemplo_uso_simples()
        elif opcao == "2":
            exemplo_monitoramento_continuo()
        elif opcao == "3":
            exemplo_relatorio_rapido()
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n👋 Execução cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")