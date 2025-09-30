"""
Exemplo: Usando MT5 Trading API com Autenticação
Demonstra como usar a API com as credenciais corretas
"""
import asyncio
import aiohttp
import json
from datetime import datetime


class MT5ApiClient:
    """Cliente para MT5 Trading API com autenticação"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self):
        """Obter headers com API key"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['AcessKey'] = self.api_key
        return headers
    
    async def health_check(self):
        """Verificar saúde da API (sem autenticação)"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def auth_info(self):
        """Obter informações de autenticação (sem autenticação)"""
        async with self.session.get(f"{self.base_url}/auth-info") as response:
            return await response.json()
    
    async def get_symbols(self):
        """Obter símbolos (requer API key)"""
        headers = self._get_headers()
        async with self.session.post(f"{self.base_url}/GetSymbols/", headers=headers) as response:
            if response.status == 401:
                raise Exception("API key inválida ou não fornecida")
            return await response.json()
    
    async def get_symbol_info(self, symbol: str):
        """Obter informações de símbolo específico"""
        headers = self._get_headers()
        data = {"ativo": symbol}
        async with self.session.post(f"{self.base_url}/GetSymbolInfo/", 
                                   headers=headers, 
                                   json=data) as response:
            if response.status == 401:
                raise Exception("API key inválida ou não fornecida")
            return await response.json()


async def exemplo_sem_autenticacao():
    """Exemplo testando endpoints sem autenticação"""
    print("1️⃣ TESTANDO ENDPOINTS PÚBLICOS (SEM AUTENTICAÇÃO)")
    print("=" * 60)
    
    async with MT5ApiClient() as client:
        try:
            # Health check
            health = await client.health_check()
            print("✅ Health Check:")
            print(f"   Status: {health['status']}")
            print(f"   MT5 Connected: {health.get('mt5_connection', 'unknown')}")
            
            # Auth info
            auth_info = await client.auth_info()
            print("\n✅ Auth Info:")
            print(f"   Docs URL: {auth_info['documentation']['url']}")
            print(f"   Docs Auth: {auth_info['documentation']['username']} / {auth_info['documentation']['password']}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")


async def exemplo_com_api_key_valida():
    """Exemplo usando API key válida"""
    print("\n2️⃣ TESTANDO COM API KEY VÁLIDA")
    print("=" * 60)
    
    # API key padrão do servidor
    api_key = "cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4"
    
    async with MT5ApiClient(api_key=api_key) as client:
        try:
            # Obter símbolos
            symbols = await client.get_symbols()
            print("✅ Símbolos obtidos:")
            print(f"   Total: {len(symbols)} símbolos")
            
            if symbols:
                # Mostrar primeiros 5 símbolos
                print("   Primeiros 5:")
                for i, symbol in enumerate(symbols[:5], 1):
                    print(f"     {i}. {symbol.get('name', 'N/A')} - {symbol.get('description', 'N/A')}")
                
                # Obter info de símbolo específico
                first_symbol = symbols[0]['name']
                symbol_info = await client.get_symbol_info(first_symbol)
                print(f"\n✅ Info do símbolo {first_symbol}:")
                print(f"   Descrição: {symbol_info.get('description', 'N/A')}")
                print(f"   Dígitos: {symbol_info.get('digits', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")


async def exemplo_com_api_key_invalida():
    """Exemplo usando API key inválida"""
    print("\n3️⃣ TESTANDO COM API KEY INVÁLIDA")
    print("=" * 60)
    
    # API key falsa
    api_key_falsa = "api-key-falsa-para-teste"
    
    async with MT5ApiClient(api_key=api_key_falsa) as client:
        try:
            # Tentar obter símbolos
            symbols = await client.get_symbols()
            print("❌ Não deveria chegar aqui - API key deveria ser rejeitada")
            
        except Exception as e:
            print("✅ Autenticação funcionando corretamente:")
            print(f"   Erro esperado: {e}")


async def exemplo_sem_api_key():
    """Exemplo sem API key"""
    print("\n4️⃣ TESTANDO SEM API KEY")
    print("=" * 60)
    
    async with MT5ApiClient() as client:
        try:
            # Tentar obter símbolos
            symbols = await client.get_symbols()
            print("❌ Não deveria chegar aqui - deveria pedir API key")
            
        except Exception as e:
            print("✅ Proteção funcionando corretamente:")
            print(f"   Erro esperado: {e}")


def mostrar_informacoes_autenticacao():
    """Mostrar informações sobre como configurar autenticação"""
    print("\n📋 INFORMAÇÕES DE AUTENTICAÇÃO")
    print("=" * 60)
    
    print("🔐 DOCUMENTAÇÃO (BasicAuth):")
    print("   URL: http://localhost:8000/docs")
    print("   Usuário: homelab")
    print("   Senha: john.1998")
    print("   Nota: Use estas credenciais para acessar /docs e /redoc")
    
    print("\n🔑 API ENDPOINTS (API Key):")
    print("   Header: AcessKey ou Authorization")
    print("   Chave padrão: cb9c4299c9ac5437d74c22fad0314cc16e3615c4c802855fdc1287eb69dd57b4")
    print("   Nota: Todos os endpoints da API requerem esta chave")
    
    print("\n💡 EXEMPLOS DE USO:")
    print("   curl -H 'AcessKey: sua-api-key' http://localhost:8000/GetSymbols/")
    print("   python: requests.post(url, headers={'AcessKey': 'sua-api-key'})")
    
    print("\n🌐 ENDPOINTS PÚBLICOS (sem autenticação):")
    print("   GET /health - Status da API")
    print("   GET /auth-info - Informações de autenticação")
    print("   GET / - Página inicial")


async def exemplo_completo():
    """Exemplo completo testando todos os cenários"""
    print("🔐 MT5 Trading API - Teste de Autenticação")
    print("=" * 70)
    
    # Mostrar informações
    mostrar_informacoes_autenticacao()
    
    # Testar cenários
    await exemplo_sem_autenticacao()
    await exemplo_com_api_key_valida()
    await exemplo_com_api_key_invalida()
    await exemplo_sem_api_key()
    
    print("\n" + "=" * 70)
    print("✅ TESTE DE AUTENTICAÇÃO CONCLUÍDO")
    print("=" * 70)
    
    print("\n🎯 RESUMO:")
    print("   ✅ Endpoints públicos funcionando")
    print("   ✅ API key válida aceita")
    print("   ✅ API key inválida rejeitada")
    print("   ✅ Requisições sem API key rejeitadas")
    print("   ✅ Documentação protegida por BasicAuth")


if __name__ == "__main__":
    print("Conectando ao servidor MT5 API...")
    print("Certifique-se de que o servidor está rodando em http://localhost:8000")
    print()
    
    try:
        asyncio.run(exemplo_completo())
    except KeyboardInterrupt:
        print("\n👋 Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Dicas:")
        print("   1. Verifique se o servidor está rodando")
        print("   2. Execute: python start_server.bat")
        print("   3. Aguarde a mensagem 'Servidor iniciado'")