"""
Exemplo: GetSymbolsPctChange - Calcular variação percentual de múltiplos símbolos
Demonstra o uso do endpoint /GetSymbolsPctChange/
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from base import BaseExample, ApiKeyRequiredMixin, ApiClient, ApiConfig
from config import API_BASE_URL, API_KEY, TEST_SYMBOLS, TIMEFRAMES

class GetSymbolsPctChangeExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo do endpoint GetSymbolsPctChange
    
    Princípios SOLID aplicados:
    - Single Responsibility: Calcula apenas variação percentual de símbolos
    - Open/Closed: Extensível para diferentes análises sem modificação
    - Liskov Substitution: Substitui BaseExample transparentemente
    - Interface Segregation: Interface focada em variação percentual
    - Dependency Inversion: Usa abstração ApiClient
    """
    
    def __init__(self, client: ApiClient, symbols: list = None, timeframe: int = 1):
        super().__init__(client)
        self.symbols = symbols or TEST_SYMBOLS[:5]  # Primeiros 5 símbolos
        self.timeframe = timeframe
    
    def execute(self) -> dict:
        """Executar chamada para GetSymbolsPctChange"""
        payload = {
            "actives": self.symbols,
            "timeframe": self.timeframe
        }
        return self.client.post("/GetSymbolsPctChange/", payload)
    
    def get_description(self) -> str:
        timeframe_name = self._get_timeframe_name()
        return f"GetSymbolsPctChange - Variação percentual de {len(self.symbols)} símbolos ({timeframe_name})"
    
    def _get_timeframe_name(self) -> str:
        """Obter nome do timeframe"""
        for name, value in TIMEFRAMES.items():
            if value == self.timeframe:
                return name
        return f"TF{self.timeframe}"
    
    def format_response(self, response: dict) -> str:
        """Override para formato customizado de variações percentuais"""
        if not response.get("OK"):
            return super().format_response(response)
        
        symbols_data = response.get("Resposta", {})
        symbols_list = symbols_data.get("symbols", [])
        count = symbols_data.get("count", 0)
        
        if not symbols_list:
            return "📭 Nenhuma variação encontrada"
        
        result = f"✅ Variação percentual de {count} símbolos:\n\n"
        
        # Ordenar por variação percentual (do maior para o menor)
        sorted_symbols = sorted(
            symbols_list, 
            key=lambda x: float(x.get('pct_change', 0)), 
            reverse=True
        )
        
        for symbol_data in sorted_symbols:
            symbol = symbol_data.get("symbol", "N/A")
            pct_change = symbol_data.get("pct_change", 0)
            error = symbol_data.get("error")
            
            if error:
                result += f"❌ {symbol}: Erro - {error}\n"
            else:
                # Emoji baseado na variação
                if pct_change > 0:
                    emoji = "📈"
                    color = "+"
                elif pct_change < 0:
                    emoji = "📉" 
                    color = ""
                else:
                    emoji = "➡️"
                    color = " "
                
                result += f"{emoji} {symbol}: {color}{pct_change:.4f}%\n"
        
        # Estatísticas resumidas
        valid_changes = [
            float(s.get('pct_change', 0)) 
            for s in symbols_list 
            if not s.get('error') and s.get('pct_change') is not None
        ]
        
        if valid_changes:
            result += f"\n📊 Resumo estatístico:\n"
            result += f"   📈 Maior alta: +{max(valid_changes):.4f}%\n"
            result += f"   📉 Maior baixa: {min(valid_changes):.4f}%\n"
            result += f"   📊 Média: {sum(valid_changes)/len(valid_changes):.4f}%\n"
            
            positive_count = sum(1 for x in valid_changes if x > 0)
            negative_count = sum(1 for x in valid_changes if x < 0)
            neutral_count = len(valid_changes) - positive_count - negative_count
            
            result += f"   📈 Em alta: {positive_count}\n"
            result += f"   📉 Em baixa: {negative_count}\n"
            result += f"   ➡️ Neutros: {neutral_count}\n"
        
        return result

class MarketSentimentExample(BaseExample, ApiKeyRequiredMixin):
    """
    Exemplo estendido para análise de sentimento do mercado
    Demonstra extensibilidade (Open/Closed Principle)
    """
    
    def __init__(self, client: ApiClient, symbols: list = None):
        super().__init__(client)
        self.symbols = symbols or TEST_SYMBOLS
        self.timeframes = [1, 5, 15, 16385]  # M1, M5, M15, H1
    
    def execute(self) -> dict:
        """Executar análise de sentimento em múltiplos timeframes"""
        results = {}
        
        for tf in self.timeframes:
            payload = {
                "actives": self.symbols,
                "timeframe": tf
            }
            response = self.client.post("/GetSymbolsPctChange/", payload)
            results[f"TF_{tf}"] = response
        
        return {"OK": True, "Resposta": results}
    
    def get_description(self) -> str:
        return f"Market Sentiment - Análise de {len(self.symbols)} símbolos em {len(self.timeframes)} timeframes"
    
    def format_response(self, response: dict) -> str:
        """Formato para análise de sentimento"""
        if not response.get("OK"):
            return super().format_response(response)
        
        results = response.get("Resposta", {})
        output = f"✅ Análise de Sentimento do Mercado:\n\n"
        
        # Análise por timeframe
        for tf_key, tf_response in results.items():
            if tf_response.get("OK"):
                tf_name = self._get_tf_name_from_key(tf_key)
                data = tf_response.get("Resposta", {})
                symbols_list = data.get("symbols", [])
                
                valid_changes = [
                    float(s.get('pct_change', 0)) 
                    for s in symbols_list 
                    if not s.get('error')
                ]
                
                if valid_changes:
                    positive = sum(1 for x in valid_changes if x > 0)
                    negative = sum(1 for x in valid_changes if x < 0)
                    total = len(valid_changes)
                    
                    sentiment_pct = (positive / total) * 100 if total > 0 else 0
                    
                    if sentiment_pct > 60:
                        sentiment = "🚀 Bullish"
                    elif sentiment_pct < 40:
                        sentiment = "🐻 Bearish"
                    else:
                        sentiment = "⚖️ Neutro"
                    
                    output += f"📊 {tf_name}: {sentiment} ({sentiment_pct:.1f}% positivos)\n"
                    output += f"   📈 {positive} altas | 📉 {negative} baixas | Total: {total}\n"
                    output += f"   📊 Variação média: {sum(valid_changes)/len(valid_changes):.4f}%\n\n"
        
        # Símbolos consistentes (mesma direção em múltiplos timeframes)
        symbol_scores = {}
        
        for tf_key, tf_response in results.items():
            if tf_response.get("OK"):
                data = tf_response.get("Resposta", {})
                symbols_list = data.get("symbols", [])
                
                for symbol_data in symbols_list:
                    symbol = symbol_data.get("symbol")
                    pct_change = symbol_data.get("pct_change", 0)
                    
                    if symbol and not symbol_data.get("error"):
                        if symbol not in symbol_scores:
                            symbol_scores[symbol] = []
                        symbol_scores[symbol].append(float(pct_change))
        
        # Encontrar símbolos com tendência consistente
        output += "🎯 Tendências Consistentes:\n"
        
        for symbol, changes in symbol_scores.items():
            if len(changes) >= 3:  # Pelo menos 3 timeframes
                all_positive = all(x > 0 for x in changes)
                all_negative = all(x < 0 for x in changes)
                
                if all_positive:
                    avg_change = sum(changes) / len(changes)
                    output += f"   🚀 {symbol}: Alta consistente ({avg_change:.4f}%)\n"
                elif all_negative:
                    avg_change = sum(changes) / len(changes)
                    output += f"   🐻 {symbol}: Baixa consistente ({avg_change:.4f}%)\n"
        
        return output
    
    def _get_tf_name_from_key(self, tf_key: str) -> str:
        """Converter chave do timeframe para nome"""
        tf_value = int(tf_key.split("_")[1])
        for name, value in TIMEFRAMES.items():
            if value == tf_value:
                return name
        return f"TF{tf_value}"

def main():
    """Executar exemplos GetSymbolsPctChange"""
    # Configurar cliente
    config = ApiConfig(API_BASE_URL, API_KEY)
    client = ApiClient(config)
    
    print("🎯 Exemplos GetSymbolsPctChange")
    print("=" * 60)
    
    # Exemplo 1: Variação percentual simples
    print("\n1️⃣ Variação percentual (M1):")
    simple_example = GetSymbolsPctChangeExample(
        client, 
        ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCHF"], 
        1
    )
    simple_example.run()
    
    # Exemplo 2: Análise de sentimento
    print("\n2️⃣ Análise de sentimento do mercado:")
    sentiment_example = MarketSentimentExample(
        client, 
        ["EURUSD", "USDJPY", "GBPUSD"]
    )
    sentiment_example.run()

if __name__ == "__main__":
    main()