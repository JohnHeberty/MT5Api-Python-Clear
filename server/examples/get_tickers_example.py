"""
Exemplo: GetTickers - Obter cotações por período
Demonstra o uso do endpoint /GetTickers/
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from base import BaseExample, ApiKeyRequiredMixin, ApiClient, ApiConfig
from config import API_BASE_URL, API_KEY, DEFAULT_SYMBOL, TIMEFRAMES

class GetTickersExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo do endpoint GetTickers
    
    Princípios SOLID aplicados:
    - Single Responsibility: Demonstra apenas GetTickers
    - Open/Closed: Extensível para diferentes períodos sem modificação
    - Liskov Substitution: Substitui BaseExample transparentemente
    - Interface Segregation: Interface focada em cotações por período
    - Dependency Inversion: Usa abstração ApiClient
    """
    
    def __init__(self, client: ApiClient, symbol: str = DEFAULT_SYMBOL, 
                 timeframe: int = 1, date_from: str = None, date_to: str = None):
        super().__init__(client)
        self.symbol = symbol
        self.timeframe = timeframe
        
        # Usar datas padrão se não fornecidas (último dia)
        if not date_from or not date_to:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            self.date_from = start_date.strftime("%Y-%m-%d %H:%M:%S")
            self.date_to = end_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.date_from = date_from
            self.date_to = date_to
    
    def execute(self) -> dict:
        """Executar chamada para GetTickers"""
        payload = {
            "active": self.symbol,
            "dateFrom": self.date_from,
            "dateTo": self.date_to,
            "timeframe": self.timeframe
        }
        return self.client.post("/GetTickers/", payload)
    
    def get_description(self) -> str:
        timeframe_name = self._get_timeframe_name()
        return f"GetTickers - Cotações {self.symbol} ({timeframe_name}) de {self.date_from} até {self.date_to}"
    
    def _get_timeframe_name(self) -> str:
        """Obter nome do timeframe"""
        for name, value in TIMEFRAMES.items():
            if value == self.timeframe:
                return name
        return f"TF{self.timeframe}"
    
    def format_response(self, response: dict) -> str:
        """Override para formato customizado de cotações"""
        if not response.get("OK"):
            return super().format_response(response)
        
        tickers_data = response.get("Resposta", {})
        tickers = tickers_data.get("tickers", [])
        count = tickers_data.get("count", 0)
        symbol = tickers_data.get("symbol", self.symbol)
        timeframe = tickers_data.get("timeframe", self.timeframe)
        
        if not tickers:
            return f"📭 Nenhuma cotação encontrada para {symbol}"
        
        result = f"✅ {count} cotações de {symbol} (TF: {timeframe}):\n\n"
        
        # Mostrar primeiras 5 e últimas 5 cotações
        display_tickers = tickers[:5] + (tickers[-5:] if len(tickers) > 10 else [])
        
        for i, ticker in enumerate(display_tickers):
            if i == 5 and len(tickers) > 10:
                result += f"   ... {len(tickers) - 10} cotações omitidas ...\n\n"
            
            result += f"🕐 {ticker.get('time', 'N/A')}\n"
            result += f"   📈 O: {ticker.get('open', 'N/A')} | "
            result += f"H: {ticker.get('high', 'N/A')} | "
            result += f"L: {ticker.get('low', 'N/A')} | "
            result += f"C: {ticker.get('close', 'N/A')}\n"
            result += f"   📊 Volume: {ticker.get('volume', 'N/A')}\n\n"
        
        # Estatísticas básicas
        if tickers:
            opens = [float(t.get('open', 0)) for t in tickers if t.get('open')]
            closes = [float(t.get('close', 0)) for t in tickers if t.get('close')]
            
            if opens and closes:
                price_change = closes[-1] - opens[0]
                price_change_pct = (price_change / opens[0]) * 100 if opens[0] > 0 else 0
                
                result += f"📊 Estatísticas do período:\n"
                result += f"   🎯 Primeiro: {opens[0]:.5f} → Último: {closes[-1]:.5f}\n"
                result += f"   📈 Variação: {price_change:+.5f} ({price_change_pct:+.2f}%)\n"
        
        return result

class TimeframeComparisonExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo comparando diferentes timeframes
    Demonstra extensibilidade (Open/Closed Principle)
    """
    
    def __init__(self, client: ApiClient, symbol: str = DEFAULT_SYMBOL):
        super().__init__(client)
        self.symbol = symbol
        self.timeframes_to_compare = [1, 5, 15, 60]  # M1, M5, M15, H1
        
        # Período de 6 horas
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=6)
        self.date_from = start_date.strftime("%Y-%m-%d %H:%M:%S")
        self.date_to = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    def execute(self) -> dict:
        """Executar comparação de timeframes"""
        results = {}
        
        for tf in self.timeframes_to_compare:
            payload = {
                "active": self.symbol,
                "dateFrom": self.date_from,
                "dateTo": self.date_to,
                "timeframe": tf
            }
            response = self.client.post("/GetTickers/", payload)
            results[f"TF_{tf}"] = response
        
        return {"OK": True, "Resposta": results}
    
    def get_description(self) -> str:
        return f"GetTickers (Comparação) - {self.symbol} em múltiplos timeframes"
    
    def format_response(self, response: dict) -> str:
        """Formato para comparação de timeframes"""
        if not response.get("OK"):
            return super().format_response(response)
        
        results = response.get("Resposta", {})
        output = f"✅ Comparação de timeframes para {self.symbol}:\n\n"
        
        for tf_key, tf_response in results.items():
            if tf_response.get("OK"):
                data = tf_response.get("Resposta", {})
                tickers = data.get("tickers", [])
                count = len(tickers)
                tf_value = data.get("timeframe", "N/A")
                
                output += f"🔸 Timeframe {tf_value}: {count} cotações\n"
                
                if tickers:
                    first_close = tickers[0].get("close", 0)
                    last_close = tickers[-1].get("close", 0)
                    if first_close and last_close:
                        change_pct = ((float(last_close) - float(first_close)) / float(first_close)) * 100
                        output += f"   📈 Variação: {change_pct:+.2f}%\n"
                
                output += "\n"
            else:
                output += f"❌ {tf_key}: {tf_response.get('Error', 'Erro')}\n\n"
        
        return output

def main():
    """Executar exemplos GetTickers"""
    # Configurar cliente
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    print("🎯 Exemplos GetTickers")
    print("=" * 50)
    
    # Exemplo 1: Cotações simples
    print("\n1️⃣ Cotações do último dia (M1):")
    simple_example = GetTickersExample(client, "EURUSD", 1)
    simple_example.run()
    
    # Exemplo 2: Comparação de timeframes
    print("\n2️⃣ Comparação de timeframes:")
    comparison_example = TimeframeComparisonExample(client, "EURUSD")
    comparison_example.run()

if __name__ == "__main__":
    main()