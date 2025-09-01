"""
Konfigurationsdatei für den Index Analyser
"""

# LLM Konfiguration
LLM_API_BASE = "http://127.0.0.1:1234/v1"
LLM_MODEL = "qwen/qwen3-30b-a3b-2507"
LLM_TEMPERATURE = 0.3  # Reduziert für maximale Konsistenz
LLM_MAX_TOKENS = 25000  # Erhöhtes Token-Limit für vollständige Berichte

# Analyse Einstellungen
DEFAULT_PERIOD = "1y"  # Standard Zeitraum für Datenabfrage
DEFAULT_INTERVAL = "1d"  # Standard Intervall

# Populäre Indizes
POPULAR_INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC", 
    "Dow Jones": "^DJI",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225",
    "Euro Stoxx 50": "^STOXX50E",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
    "MSCI World": "URTH"
}

# Technische Indikatoren Einstellungen
INDICATOR_PARAMS = {
    "sma_periods": [],  # Simple MA deaktiviert
    "ema_periods": [9, 21, 50, 200],  # Aktualisierte EMA Perioden
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2,
    "stoch_period": 14,
    "adx_period": 14,
    "atr_period": 14,
    "cci_period": 20,
    "obv_period": 20,
    "vwap_period": 14
}

# Fibonacci Retracement Levels
FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618, 2.618]

# Chart Farbschema
CHART_COLORS = {
    "bullish": "#00CC88",
    "bearish": "#FF4444",
    "neutral": "#888888",
    "background": "#0E1117",
    "grid": "#262730",
    "text": "#FAFAFA"
}

# Sentiment Schwellenwerte
SENTIMENT_THRESHOLDS = {
    "sehr_bullisch": 80,
    "bullisch": 60,
    "neutral": 40,
    "bearisch": 20,
    "sehr_bearisch": 0
}
