"""
Exemplo: Testando API sem autenticação (API_KEYS vazia)

Este script demonstra como a API funciona quando não há API Keys configuradas.
Para testar, edite o .env e deixe API_KEYS vazia ou comente a linha.
"""
import asyncio
import aiohttp
import json


class MT5TestClient:
    """Cliente de teste para API sem autenticação"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_auth_info(self):
        """Verificar status de autenticação"""
        async with self.session.get(f"{self.base_url}/auth-info") as response:
            return await response.json()
    
    async def test_health(self):
        """Testar health check"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def test_get_symbols_no_auth(self):
        """Testar GetSymbols sem autenticação"""
        headers = {'Content-Type': 'application/json'}
        async with self.session.post(f"{self.base_url}/GetSymbols/", headers=headers) as response:
            return {
                "status_code": response.status,
                "data": await response.json()
            }
    
    async def test_get_symbols_with_fake_key(self):
        """Testar GetSymbols com chave falsa (para ver se ainda funciona)"""
        headers = {
            'Content-Type': 'application/json',
            'AcessKey': 'chave-falsa-para-teste'
        }
        async with self.session.post(f"{self.base_url}/GetSymbols/", headers=headers) as response:
            return {
                "status_code": response.status,
                "data": await response.json()
            }


async def testar_api_sem_autenticacao():
    """Teste completo da API sem autenticação"""
    
    print("🧪 TESTE: API SEM AUTENTICAÇÃO (API_KEYS VAZIA)")
    print("=" * 60)
    
    print("\n💡 Para este teste funcionar:")
    print("   1. Edite server/.env")
    print("   2. Deixe API_KEYS vazia ou comente a linha:")
    print("      # API_KEYS=")
    print("   3. Reinicie o servidor")
    
    async with MT5TestClient() as client:
        
        # 1. Verificar status de autenticação
        print("\n1️⃣ Verificando status de autenticação:")
        try:
            auth_info = await client.test_auth_info()
            auth_enabled = auth_info.get('api_authentication', {}).get('enabled', True)
            status = auth_info.get('api_authentication', {}).get('status', 'Unknown')
            
            print(f"   Status: {status}")
            print(f"   Autenticação ativa: {auth_enabled}")
            print(f"   Keys configuradas: {auth_info.get('api_authentication', {}).get('configured_keys', 0)}")
            
            if auth_enabled:
                print("   ⚠️ Autenticação ainda está ativa - verifique .env")
                return
            else:
                print("   ✅ Autenticação desabilitada - prosseguindo com testes")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return
        
        # 2. Testar health check
        print("\n2️⃣ Testando health check:")
        try:
            health = await client.test_health()
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   MT5: {health.get('mt5_connection', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 3. Testar GetSymbols sem autenticação
        print("\n3️⃣ Testando GetSymbols SEM headers de autenticação:")
        try:
            result = await client.test_get_symbols_no_auth()
            status_code = result['status_code']
            data = result['data']
            
            print(f"   Status Code: {status_code}")
            
            if status_code == 200:
                print("   ✅ SUCESSO - API funcionando sem autenticação!")
                if data.get('OK'):
                    symbols_count = len(data.get('Resposta', {}).get('symbols', []))
                    print(f"   📊 Símbolos obtidos: {symbols_count}")
                else:
                    print(f"   ⚠️ API retornou OK=False: {data}")
            elif status_code == 401:
                print("   ❌ FALHOU - API ainda está exigindo autenticação")
                print("   💡 Verifique se API_KEYS está realmente vazia no .env")
            else:
                print(f"   ❌ Status inesperado: {status_code}")
                print(f"   Resposta: {data}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 4. Testar com chave falsa (deve funcionar mesmo assim)
        print("\n4️⃣ Testando GetSymbols COM chave falsa:")
        try:
            result = await client.test_get_symbols_with_fake_key()
            status_code = result['status_code']
            data = result['data']
            
            print(f"   Status Code: {status_code}")
            
            if status_code == 200:
                print("   ✅ SUCESSO - Chave falsa ignorada (comportamento esperado)")
                if data.get('OK'):
                    symbols_count = len(data.get('Resposta', {}).get('symbols', []))
                    print(f"   📊 Símbolos obtidos: {symbols_count}")
            elif status_code == 401:
                print("   ❌ FALHOU - API rejeitou chave falsa (não deveria quando auth desabilitada)")
            else:
                print(f"   ❌ Status inesperado: {status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DO TESTE")
    print("=" * 60)
    print("✅ Comportamento esperado quando API_KEYS está vazia:")
    print("   • Endpoints da API funcionam SEM header AcessKey")
    print("   • Headers de API key são ignorados se fornecidos")
    print("   • Apenas documentação (/docs) ainda requer BasicAuth")
    print("   • Health e auth-info sempre públicos")


def mostrar_configuracao():
    """Mostrar como configurar para teste"""
    print("⚙️ CONFIGURAÇÃO PARA TESTE")
    print("=" * 60)
    
    print("\n📝 Para desabilitar autenticação da API:")
    print("   1. Abrir: server/.env")
    print("   2. Localizar linha: API_KEYS=...")
    print("   3. Comentar ou deixar vazia:")
    print("      # API_KEYS=")
    print("      ou")
    print("      API_KEYS=")
    
    print("\n📝 Para reabilitar autenticação:")
    print("   1. Descomentar e adicionar chaves:")
    print("      API_KEYS=cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4")
    
    print("\n🔄 Sempre reinicie o servidor após alterar .env:")
    print("   python server/app.py")


if __name__ == "__main__":
    print("🧪 MT5 Trading API - Teste de Autenticação Desabilitada")
    print("=" * 70)
    
    mostrar_configuracao()
    
    print("\nDeseja executar o teste? (s/n): ", end="")
    try:
        resposta = input().strip().lower()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            asyncio.run(testar_api_sem_autenticacao())
        else:
            print("👋 Teste cancelado")
            
    except KeyboardInterrupt:
        print("\n👋 Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Certifique-se de que o servidor está rodando em http://localhost:8000")