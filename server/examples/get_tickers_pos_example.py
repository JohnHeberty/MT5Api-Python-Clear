"""
Exemplo: GetTickersPos - Obter últimas N cotações
Demonstra o uso do endpoint /GetTickersPos/
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import BaseExample, ApiKeyRequiredMixin, ApiClient, ApiConfig
from config import API_BASE_URL, API_KEY, DEFAULT_SYMBOL, DEFAULT_COUNT, TIMEFRAMES

class GetTickersPosExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo do endpoint GetTickersPos
    
    Princípios SOLID aplicados:
    - Single Responsibility: Foca apenas em obter últimas N cotações
    - Open/Closed: Extensível para diferentes análises sem modificação
    - Liskov Substitution: Substitui BaseExample perfeitamente
    - Interface Segregation: Interface específica para cotações recentes
    - Dependency Inversion: Depende da abstração ApiClient
    """
    
    def __init__(self, client: ApiClient, symbol: str = DEFAULT_SYMBOL, 
                 count: int = DEFAULT_COUNT, timeframe: int = 1):
        super().__init__(client)
        self.symbol = symbol
        self.count = count
        self.timeframe = timeframe
    
    def execute(self) -> dict:
        """Executar chamada para GetTickersPos"""
        payload = {
            "active": self.symbol,
            "position": self.count,
            "timeframe": self.timeframe
        }
        return self.client.post("/GetTickersPos/", payload)
    
    def get_description(self) -> str:
        timeframe_name = self._get_timeframe_name()
        return f"GetTickersPos - Últimas {self.count} cotações de {self.symbol} ({timeframe_name})"
    
    def _get_timeframe_name(self) -> str:
        """Obter nome do timeframe"""
        for name, value in TIMEFRAMES.items():
            if value == self.timeframe:
                return name
        return f"TF{self.timeframe}"
    
    def format_response(self, response: dict) -> str:
        """Override para formato customizado das últimas cotações"""
        if not response.get("OK"):
            return super().format_response(response)
        
        tickers_data = response.get("Resposta", {})
        tickers = tickers_data.get("tickers", [])
        count = tickers_data.get("count", 0)
        symbol = tickers_data.get("symbol", self.symbol)
        requested_count = tickers_data.get("requested_count", self.count)
        
        if not tickers:
            return f"📭 Nenhuma cotação encontrada para {symbol}"
        
        result = f"✅ {count}/{requested_count} últimas cotações de {symbol}:\n\n"
        
        # Mostrar todas as cotações (já são poucas)
        for i, ticker in enumerate(reversed(tickers)):  # Mais recente primeiro
            result += f"🕐 #{len(tickers)-i} - {ticker.get('time', 'N/A')}\n"
            result += f"   💰 Open: {ticker.get('open', 'N/A')}\n"
            result += f"   📈 High: {ticker.get('high', 'N/A')}\n"
            result += f"   📉 Low:  {ticker.get('low', 'N/A')}\n"
            result += f"   🎯 Close: {ticker.get('close', 'N/A')}\n"
            result += f"   📊 Volume: {ticker.get('volume', 'N/A')}\n"
            
            # Calcular variação se não for a primeira
            if i > 0:
                prev_close = tickers[-(i)]
                curr_close = ticker.get('close')
                if prev_close and curr_close:
                    try:
                        change = float(curr_close) - float(prev_close.get('close', 0))
                        change_pct = (change / float(prev_close.get('close', 1))) * 100
                        result += f"   📊 Variação: {change:+.5f} ({change_pct:+.2f}%)\n"
                    except (ValueError, ZeroDivisionError):
                        pass
            
            result += "\n"
        
        # Resumo estatístico
        if len(tickers) >= 2:
            first_ticker = tickers[0]
            last_ticker = tickers[-1]
            
            try:
                first_price = float(first_ticker.get('close', 0))
                last_price = float(last_ticker.get('close', 0))
                
                if first_price > 0:
                    total_change = last_price - first_price
                    total_change_pct = (total_change / first_price) * 100
                    
                    result += f"📊 Resumo do período:\n"
                    result += f"   🎯 Primeira cotação: {first_price:.5f}\n"
                    result += f"   🎯 Última cotação: {last_price:.5f}\n"
                    result += f"   📈 Variação total: {total_change:+.5f} ({total_change_pct:+.2f}%)\n"
                    
                    # Encontrar máximo e mínimo
                    highs = [float(t.get('high', 0)) for t in tickers if t.get('high')]
                    lows = [float(t.get('low', 0)) for t in tickers if t.get('low')]
                    
                    if highs and lows:
                        result += f"   📈 Máximo: {max(highs):.5f}\n"
                        result += f"   📉 Mínimo: {min(lows):.5f}\n"
                        result += f"   📊 Range: {max(highs) - min(lows):.5f}\n"
            
            except (ValueError, TypeError):
                result += "\n⚠️  Erro ao calcular estatísticas\n"
        
        return result

class MultiSymbolLatestExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo para obter últimas cotações de múltiplos símbolos
    Demonstra extensibilidade e reutilização (DRY principle)
    """
    
    def __init__(self, client: ApiClient, symbols: list = None, count: int = 5):
        super().__init__(client)
        self.symbols = symbols or ["EURUSD", "USDJPY", "GBPUSD"]
        self.count = count
    
    def execute(self) -> dict:
        """Executar chamadas para múltiplos símbolos"""
        results = {}
        
        for symbol in self.symbols:
            payload = {
                "active": symbol,
                "position": self.count,
                "timeframe": 1  # M1
            }
            response = self.client.post("/GetTickersPos/", payload)
            results[symbol] = response
        
        return {"OK": True, "Resposta": results}
    
    def get_description(self) -> str:
        return f"GetTickersPos (Múltiplos) - Últimas {self.count} cotações de {len(self.symbols)} símbolos"
    
    def format_response(self, response: dict) -> str:
        """Formato compacto para múltiplos símbolos"""
        if not response.get("OK"):
            return super().format_response(response)
        
        results = response.get("Resposta", {})
        output = f"✅ Últimas cotações de {len(self.symbols)} símbolos:\n\n"
        
        for symbol, symbol_response in results.items():
            if symbol_response.get("OK"):
                data = symbol_response.get("Resposta", {})
                tickers = data.get("tickers", [])
                
                if tickers:
                    latest = tickers[-1]  # Mais recente
                    output += f"🔸 {symbol}: {latest.get('close', 'N/A')}\n"
                    output += f"   🕐 {latest.get('time', 'N/A')}\n"
                    output += f"   📊 H:{latest.get('high', 'N/A')} L:{latest.get('low', 'N/A')} V:{latest.get('volume', 'N/A')}\n"
                    
                    # Calcular tendência simples (últimas 3 cotações)
                    if len(tickers) >= 3:
                        closes = [float(t.get('close', 0)) for t in tickers[-3:]]
                        if all(closes):
                            if closes[-1] > closes[0]:
                                trend = "📈 Alta"
                            elif closes[-1] < closes[0]:
                                trend = "📉 Baixa"
                            else:
                                trend = "➡️ Lateral"
                            output += f"   {trend}\n"
                    
                    output += "\n"
                else:
                    output += f"📭 {symbol}: Sem cotações\n\n"
            else:
                output += f"❌ {symbol}: {symbol_response.get('Error', 'Erro')}\n\n"
        
        return output

def main():
    """Executar exemplos GetTickersPos"""
    # Configurar cliente
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    print("🎯 Exemplos GetTickersPos")
    print("=" * 50)
    
    # Exemplo 1: Últimas cotações detalhadas
    print("\n1️⃣ Últimas 5 cotações detalhadas (EURUSD):")
    detailed_example = GetTickersPosExample(client, "EURUSD", 5, 1)
    detailed_example.run()
    
    # Exemplo 2: Múltiplos símbolos resumido
    print("\n2️⃣ Últimas cotações de múltiplos símbolos:")
    multi_example = MultiSymbolLatestExample(client, ["EURUSD", "USDJPY", "GBPUSD"], 3)
    multi_example.run()

if __name__ == "__main__":
    main()