"""
Script para executar todos os exemplos do MT5 Trading Client

Execute este arquivo para testar todos os exemplos disponíveis.
"""
import sys
import os
import asyncio

# Adicionar pasta pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def mostrar_menu():
    """Mostrar menu de opções"""
    print("=" * 70)
    print("🚀 MT5 TRADING CLIENT - EXEMPLOS INTERATIVOS")
    print("=" * 70)
    print("\nEscolha um exemplo para executar:")
    print()
    print("1. 📋 Exemplo Básico")
    print("   - Verificar conexão")
    print("   - Listar símbolos")
    print("   - Obter dados de mercado")
    print("   - Preços e variações atuais")
    print()
    print("2. 📊 Análise de Mercado")
    print("   - Cotações históricas")
    print("   - Médias móveis")
    print("   - Análise de volatilidade")
    print("   - Identificação de tendências")
    print()
    print("3. ⚡ Uso Simples (Síncrono)")
    print("   - Interface sem async/await")
    print("   - Monitoramento contínuo")
    print("   - Relatório rápido")
    print()
    print("4. 🔧 Testar Configuração")
    print("   - Verificar conectividade")
    print("   - Validar dependências")
    print()
    print("0. 🚪 Sair")
    print()


async def testar_configuracao():
    """Testar se tudo está funcionando"""
    
    print("\n🔧 TESTANDO CONFIGURAÇÃO")
    print("=" * 40)
    
    try:
        # Testar imports
        print("1️⃣ Testando imports...")
        from mt5_client import MT5TradingClient, SimpleMT5Client
        print("   ✅ Imports OK")
        
        # Testar conexão básica
        print("\n2️⃣ Testando conexão com API...")
        client = MT5TradingClient(
            api_url="http://localhost:8000",
            timeout=10
        )
        
        try:
            async with client:
                health = await client.check_health()
                print(f"   ✅ API Status: {health.status}")
                print(f"   📡 MT5 Connected: {health.mt5_connected}")
                
                if health.mt5_connected:
                    # Testar operação básica
                    print("\n3️⃣ Testando operação básica...")
                    symbols = await client.get_symbols()
                    print(f"   ✅ {len(symbols)} símbolos obtidos")
                    
                    if symbols:
                        # Testar dados de mercado
                        test_symbol = symbols[0].name
                        market_data = await client.get_market_data(test_symbol)
                        if market_data:
                            print(f"   ✅ Dados de mercado OK ({test_symbol})")
                        else:
                            print(f"   ⚠️ Dados de mercado não obtidos ({test_symbol})")
                else:
                    print("   ⚠️ MT5 não está conectado no servidor")
                
        except Exception as e:
            print(f"   ❌ Erro de conexão: {e}")
            print("   💡 Verifique se o servidor está rodando em localhost:8000")
            return False
        
        print("\n✅ CONFIGURAÇÃO OK - Todos os exemplos devem funcionar!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Erro de import: {e}")
        print("   💡 Execute: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False


def executar_exemplo_basico():
    """Executar exemplo básico"""
    try:
        from exemplo_basico import exemplo_basico
        asyncio.run(exemplo_basico())
    except ImportError:
        print("❌ Arquivo exemplo_basico.py não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao executar exemplo básico: {e}")


def executar_analise_mercado():
    """Executar análise de mercado"""
    try:
        from exemplo_analise_mercado import exemplo_analise_mercado
        asyncio.run(exemplo_analise_mercado())
    except ImportError:
        print("❌ Arquivo exemplo_analise_mercado.py não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao executar análise de mercado: {e}")


def executar_uso_simples():
    """Executar uso simples"""
    try:
        from exemplo_uso_simples import exemplo_uso_simples, exemplo_relatorio_rapido
        
        print("\nEscolha o sub-exemplo:")
        print("1. Uso básico síncrono")
        print("2. Relatório rápido")
        
        sub_opcao = input("Digite a opção (1-2): ").strip()
        
        if sub_opcao == "1":
            exemplo_uso_simples()
        elif sub_opcao == "2":
            exemplo_relatorio_rapido()
        else:
            print("❌ Opção inválida!")
            
    except ImportError:
        print("❌ Arquivo exemplo_uso_simples.py não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao executar uso simples: {e}")


async def main():
    """Função principal"""
    
    while True:
        try:
            mostrar_menu()
            
            opcao = input("Digite sua opção (0-4): ").strip()
            
            if opcao == "0":
                print("\n👋 Saindo... Até logo!")
                break
                
            elif opcao == "1":
                print("\n🚀 Executando Exemplo Básico...")
                executar_exemplo_basico()
                
            elif opcao == "2":
                print("\n🚀 Executando Análise de Mercado...")
                executar_analise_mercado()
                
            elif opcao == "3":
                print("\n🚀 Executando Uso Simples...")
                executar_uso_simples()
                
            elif opcao == "4":
                print("\n🚀 Testando Configuração...")
                await testar_configuracao()
                
            else:
                print("\n❌ Opção inválida! Tente novamente.")
            
            # Pausa entre execuções
            if opcao in ["1", "2", "3", "4"]:
                input("\n⏸️ Pressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Execução cancelada pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("\n⏸️ Pressione Enter para continuar...")


if __name__ == "__main__":
    print("🔧 Inicializando exemplos do MT5 Trading Client...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Programa finalizado.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        input("\nPressione Enter para sair...")