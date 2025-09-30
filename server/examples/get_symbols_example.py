"""
Exemplo: GetSymbols - Obter todos os símbolos disponíveis
Demonstra o uso do endpoint /GetSymbols/
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import BaseExample, ApiKeyRequiredMixin, ApiClient, ApiConfig
from config import API_BASE_URL, API_KEY

class GetSymbolsExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo do endpoint GetSymbols
    
    Single Responsibility: Demonstra apenas o uso de GetSymbols
    Open/Closed: Extensível para novos formatos de saída
    Liskov Substitution: Pode ser usado no lugar de BaseExample
    Interface Segregation: Usa apenas interfaces necessárias
    Dependency Inversion: Depende da abstração ApiClient
    """
    
    def execute(self) -> dict:
        """Executar chamada para GetSymbols"""
        return self.client.post("/GetSymbols/", {})
    
    def get_description(self) -> str:
        return "GetSymbols - Listar todos os símbolos disponíveis no MT5"
    
    def format_response(self, response: dict) -> str:
        """Override para formato customizado de símbolos"""
        if not response.get("OK"):
            return super().format_response(response)
        
        symbols_data = response.get("Resposta", {})
        symbols = symbols_data.get("symbols", [])
        count = symbols_data.get("count", 0)
        
        if not symbols:
            return "📭 Nenhum símbolo encontrado"
        
        result = f"✅ Encontrados {count} símbolos:\n\n"
        
        # Mostrar primeiros 10 símbolos com detalhes
        for i, symbol in enumerate(symbols[:10]):
            result += f"🔸 {symbol.get('name', 'N/A')}\n"
            result += f"   📝 Descrição: {symbol.get('description', 'N/A')}\n"
            result += f"   💱 Base/Lucro: {symbol.get('currency_base', 'N/A')}/{symbol.get('currency_profit', 'N/A')}\n"
            result += f"   📊 Dígitos: {symbol.get('digits', 'N/A')}\n"
            result += f"   📈 Vol. Min/Max: {symbol.get('volume_min', 'N/A')}/{symbol.get('volume_max', 'N/A')}\n\n"
        
        if len(symbols) > 10:
            result += f"... e mais {len(symbols) - 10} símbolos\n"
        
        return result

def main():
    """Executar exemplo GetSymbols"""
    # Configurar cliente
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    # Criar e executar exemplo
    example = GetSymbolsExample(client)
    example.run()

if __name__ == "__main__":
    main()