"""
Exemplo: GetSymbolInfo - Obter informações de um símbolo específico
Demonstra o uso do endpoint /GetSymbolInfo/
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import BaseExample, ApiKeyRequiredMixin, ApiClient, ApiConfig
from config import API_BASE_URL, API_KEY, DEFAULT_SYMBOL, TEST_SYMBOLS

class GetSymbolInfoExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo do endpoint GetSymbolInfo
    
    Princípios SOLID aplicados:
    - Single Responsibility: Foca apenas em demonstrar GetSymbolInfo
    - Open/Closed: Pode ser estendido para múltiplos símbolos sem modificação
    - Liskov Substitution: Substitui BaseExample perfeitamente
    - Interface Segregation: Usa apenas métodos necessários
    - Dependency Inversion: Depende de abstrações (ApiClient)
    """
    
    def __init__(self, client: ApiClient, symbol: str = DEFAULT_SYMBOL):
        super().__init__(client)
        self.symbol = symbol
    
    def execute(self) -> dict:
        """Executar chamada para GetSymbolInfo"""
        payload = {
            "symbol": self.symbol
        }
        return self.client.post("/GetSymbolInfo/", payload)
    
    def get_description(self) -> str:
        return f"GetSymbolInfo - Informações detalhadas do símbolo {self.symbol}"
    
    def format_response(self, response: dict) -> str:
        """Override para formato customizado de informações do símbolo"""
        if not response.get("OK"):
            return super().format_response(response)
        
        symbol_info = response.get("Resposta", {})
        
        if not symbol_info:
            return "📭 Informações do símbolo não encontradas"
        
        result = f"✅ Informações do símbolo {self.symbol}:\n\n"
        result += f"📛 Nome: {symbol_info.get('name', 'N/A')}\n"
        result += f"📝 Descrição: {symbol_info.get('description', 'N/A')}\n"
        result += f"🔢 Dígitos: {symbol_info.get('digits', 'N/A')}\n"
        result += f"📍 Ponto: {symbol_info.get('point', 'N/A')}\n"
        result += f"💱 Moeda Base: {symbol_info.get('currency_base', 'N/A')}\n"
        result += f"💰 Moeda Lucro: {symbol_info.get('currency_profit', 'N/A')}\n"
        result += f"🏦 Moeda Margem: {symbol_info.get('currency_margin', 'N/A')}\n"
        result += f"📊 Volume Mínimo: {symbol_info.get('volume_min', 'N/A')}\n"
        result += f"📈 Volume Máximo: {symbol_info.get('volume_max', 'N/A')}\n"
        result += f"⚙️ Modo de Negociação: {symbol_info.get('trade_mode', 'N/A')}\n"
        
        return result

class MultiSymbolInfoExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo estendido para consultar múltiplos símbolos
    Demonstra o princípio Open/Closed (extensão sem modificação)
    """
    
    def __init__(self, client: ApiClient, symbols: list = None):
        super().__init__(client)
        self.symbols = symbols or TEST_SYMBOLS[:3]  # Primeiros 3 símbolos
    
    def execute(self) -> dict:
        """Executar chamadas para múltiplos símbolos"""
        results = {}
        
        for symbol in self.symbols:
            payload = {"symbol": symbol}
            response = self.client.post("/GetSymbolInfo/", payload)
            results[symbol] = response
        
        return {"OK": True, "Resposta": results}
    
    def get_description(self) -> str:
        return f"GetSymbolInfo (Múltiplos) - Informações de {len(self.symbols)} símbolos"
    
    def format_response(self, response: dict) -> str:
        """Formato customizado para múltiplos símbolos"""
        if not response.get("OK"):
            return super().format_response(response)
        
        results = response.get("Resposta", {})
        output = f"✅ Consultando {len(self.symbols)} símbolos:\n\n"
        
        for symbol, symbol_response in results.items():
            if symbol_response.get("OK"):
                info = symbol_response.get("Resposta", {})
                output += f"🔸 {symbol}: {info.get('description', 'N/A')}\n"
                output += f"   💱 {info.get('currency_base', 'N/A')}/{info.get('currency_profit', 'N/A')}\n"
                output += f"   📊 Dígitos: {info.get('digits', 'N/A')}, Ponto: {info.get('point', 'N/A')}\n\n"
            else:
                output += f"❌ {symbol}: {symbol_response.get('Error', 'Erro desconhecido')}\n\n"
        
        return output

def main():
    """Executar exemplos GetSymbolInfo"""
    # Configurar cliente
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    print("🎯 Exemplos GetSymbolInfo")
    print("=" * 50)
    
    # Exemplo 1: Símbolo único
    print("\n1️⃣ Consultando símbolo único:")
    single_example = GetSymbolInfoExample(client, "EURUSD")
    single_example.run()
    
    # Exemplo 2: Múltiplos símbolos
    print("\n2️⃣ Consultando múltiplos símbolos:")
    multi_example = MultiSymbolInfoExample(client, ["EURUSD", "USDJPY", "GBPUSD"])
    multi_example.run()

if __name__ == "__main__":
    main()