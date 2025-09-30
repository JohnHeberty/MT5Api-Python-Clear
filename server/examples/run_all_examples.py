"""
MT5 Trading API - Executar Todos os Exemplos
Demonstra todos os endpoints da API seguindo princípios SOLID
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import ApiClient, ApiConfig, ExampleRunner, HealthCheckExample
from config import API_BASE_URL, API_KEY

# Importar todos os exemplos
from get_symbols_example import GetSymbolsExample
from get_symbol_info_example import GetSymbolInfoExample, MultiSymbolInfoExample
from get_tickers_example import GetTickersExample, TimeframeComparisonExample
from get_tickers_pos_example import GetTickersPosExample, MultiSymbolLatestExample
from get_symbols_pct_change_example import GetSymbolsPctChangeExample, MarketSentimentExample

def create_all_examples(client: ApiClient) -> list:
    """
    Factory method para criar todos os exemplos
    Demonstra Dependency Injection e Factory Pattern
    """
    examples = [
        # Health check (sem autenticação)
        HealthCheckExample(client),
        
        # Exemplos básicos (um por endpoint)
        GetSymbolsExample(client),
        GetSymbolInfoExample(client, "EURUSD"),
        GetTickersExample(client, "EURUSD", 1),
        GetTickersPosExample(client, "EURUSD", 5, 1),
        GetSymbolsPctChangeExample(client, ["EURUSD", "USDJPY", "GBPUSD"], 1),
        
        # Exemplos avançados (demonstram extensibilidade)
        MultiSymbolInfoExample(client, ["EURUSD", "USDJPY", "GBPUSD"]),
        TimeframeComparisonExample(client, "EURUSD"),
        MultiSymbolLatestExample(client, ["EURUSD", "USDJPY", "GBPUSD"], 3),
        MarketSentimentExample(client, ["EURUSD", "USDJPY", "GBPUSD"])
    ]
    
    return examples

def main():
    """Executar todos os exemplos da MT5 API"""
    print("🚀 MT5 Trading API - Exemplos Completos")
    print("=" * 70)
    print("📚 Demonstrando todos os endpoints seguindo princípios SOLID")
    print("=" * 70)
    
    # Configurar cliente da API
    print(f"🔗 Conectando à API: {API_BASE_URL}")
    print(f"🔑 Usando API Key: {API_KEY[:20]}..." if API_KEY else "⚠️ API Key não configurada")
    print()
    
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    # Criar todos os exemplos
    examples = create_all_examples(client)
    
    # Criar runner e executar
    runner = ExampleRunner(examples)
    
    # Menu interativo
    while True:
        print("\n🎯 Menu de Exemplos:")
        print("0. Executar todos os exemplos")
        print("1. Listar exemplos disponíveis")
        print("2. Executar exemplo específico")
        print("9. Sair")
        
        try:
            choice = input("\n📝 Escolha uma opção (0-9): ").strip()
            
            if choice == "0":
                print("\n🚀 Executando todos os exemplos...")
                runner.run_all()
                
            elif choice == "1":
                runner.list_examples()
                
            elif choice == "2":
                runner.list_examples()
                try:
                    index = int(input("\n📝 Digite o número do exemplo: "))
                    runner.run_single(index)
                except (ValueError, IndexError):
                    print("❌ Número inválido")
                    
            elif choice == "9":
                print("👋 Encerrando exemplos. Obrigado!")
                break
                
            else:
                print("❌ Opção inválida. Use 0, 1, 2 ou 9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário. Tchau!")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()