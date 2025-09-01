"""
Language translations for the Index Analyser
"""

TRANSLATIONS = {
    'de': {
        # Main UI
        'app_title': '🚀 Advanced Index Analyser mit KI',
        'settings': '⚙️ Einstellungen',
        'select_index': 'Index auswählen',
        'custom_symbol': 'Eigenes Symbol verwenden',
        'ticker_symbol': 'Ticker Symbol',
        'period': 'Zeitraum',
        'interval': 'Intervall',
        'ai_settings': '🤖 KI-Einstellungen',
        'enable_ai': 'KI-Analyse aktivieren',
        'creativity': 'Kreativität',
        'max_tokens': 'Max. Tokens',
        'token_warning': '⚠️ Hohe Token-Anzahl kann die Generierung verlangsamen',
        'token_warning_llm': 'Stellen Sie sicher, dass Ihr LLM diese Menge unterstützt',
        'advanced_settings': '🔧 Erweiterte Einstellungen',
        'section_tokens': 'Token-Limits pro Abschnitt',
        'tokens_indicators': 'Tokens für Indikatoren-Analyse',
        'tokens_probabilities': 'Tokens für Wahrscheinlichkeits-Analyse',
        'tokens_fibonacci': 'Tokens für Fibonacci/Support/Resistance',
        'tokens_questions': 'Tokens für Frage-Antworten',
        'tokens_help': 'Höhere Werte = detailliertere Analysen, aber längere Generierungszeit',
        'start_analysis': '🔍 Analyse starten',
        'language': '🌐 Sprache',
        'save_settings': '💾 Einstellungen speichern',
        'reset_settings': '🔄 Einstellungen zurücksetzen',
        'settings_saved': '✓ Einstellungen gespeichert!',
        'settings_reset': '✓ Einstellungen zurückgesetzt!',
        'settings_save_failed': 'Fehler beim Speichern der Einstellungen',
        'settings_reset_failed': 'Fehler beim Zurücksetzen der Einstellungen',
        
        # Status Messages
        'loading_data': '🔄 Lade Daten und führe Analyse durch...',
        'error_loading': '❌ Fehler beim Laden der Daten. Bitte überprüfen Sie das Symbol.',
        'analysis_complete': '✅ Analyse abgeschlossen!',
        'ai_disabled': '🤖 KI-Analyse ist deaktiviert. Aktivieren Sie sie in den Einstellungen.',
        'generating_report': '📝 Generiere professionellen Marktbericht...',
        
        # Tabs
        'tab_overview': '📊 Übersicht',
        'tab_charts': '📈 Charts',
        'tab_indicators': '🔍 Indikatoren',
        'tab_patterns': '🕯️ Candlestick Muster',
        'tab_ai_analysis': '🤖 KI-Analyse',
        'tab_report': '📋 Bericht',
        
        # Metrics
        'current_price': 'Aktueller Kurs',
        'market_sentiment': 'Marktstimmung',
        'volatility': 'Volatilität (ATR)',
        'strength': 'Stärke',
        'overbought': 'Überkauft',
        'oversold': 'Überverkauft',
        'normal': 'Normal',
        'high': 'Hoch',
        
        # Probabilities
        'scenario_probabilities': '📊 Szenario-Wahrscheinlichkeiten',
        'bullish': 'Bullisch',
        'bearish': 'Bearisch',
        'probability': 'Wahrscheinlichkeit',
        'signal_analysis': 'Signal-Analyse',
        'bullish_signals': '🟢 Bullische Signale',
        'bearish_signals': '🔴 Bearische Signale',
        
        # Targets
        'price_targets': '🎯 Kursziele',
        'bullish_targets': '📈 Bullische Ziele',
        'bearish_targets': '📉 Bearische Ziele',
        
        # Indicators
        'trend_indicators': '📊 Trend-Indikatoren',
        'momentum_indicators': '🎯 Momentum-Indikatoren',
        'volume_indicators': '💰 Volumen-Indikatoren',
        'pivot_points': '📍 Pivot Points',
        'resistance': 'Widerstand',
        'support': 'Unterstützung',
        
        # Candlestick Patterns
        'candlestick_analysis': '🕯️ Candlestick-Muster Analyse',
        'patterns_found': 'Muster gefunden',
        'pattern_statistics': '📊 Muster-Statistik',
        'total_patterns': 'Gesamt Muster',
        'recent_patterns': 'Aktuelle Muster',
        'pattern': 'Muster',
        'signal': 'Signal',
        'reliability': 'Zuverlässigkeit',
        'date': 'Datum',
        'price': 'Kurs',
        
        # Charts
        'technical_analysis': 'Technische Analyse',
        'correlation_matrix': '🔥 Indikator-Korrelationen',
        'volume_analysis': '📊 Volumen-Analyse',
        'volume_trend': 'Volumen-Trend',
        '20_day_average': '20-Tage Durchschnitt',
        'volume': 'Volumen',
        
        # AI Analysis
        'ai_analysis': '🤖 KI-gestützte Analyse',
        'technical_analysis_ai': '📊 Technische Analyse',
        'scenario_analysis': '🎲 Szenario-Analyse',
        'fibonacci_sr_analysis': '📐 Fibonacci & Support/Resistance Analyse',
        'ask_ai': '💬 Frage an die KI',
        'ask_question': '🤔 Frage stellen',
        'ai_thinking': '🧠 KI analysiert die Daten...',
        'answer': '💡 Antwort',
        'question_placeholder': 'z.B. Welche Trading-Strategie würdest du empfehlen?',
        
        # Report
        'market_report': '📋 Umfassender Marktbericht',
        'generate_report': '📄 Bericht generieren',
        'download_report': '📥 Bericht herunterladen',
        
        # Footer
        'footer_version': '🚀 Advanced Index Analyser v1.0 | Powered by yfinance & Local LLM',
        'footer_disclaimer': '⚠️ Hinweis: Diese Analyse dient nur zu Informationszwecken und stellt keine Anlageberatung dar.',
        
        # Welcome Messages
        'welcome_title': 'Willkommen beim Advanced Index Analyser!',
        'welcome_step1': '1. Wählen Sie einen Index oder geben Sie ein eigenes Symbol ein',
        'welcome_step2': '2. Stellen Sie Zeitraum und Intervall ein',
        'welcome_step3': '3. Klicken Sie auf',
        'welcome_features': 'Die Analyse umfasst:',
        'welcome_feature1': '📊 Über 30 technische Indikatoren',
        'welcome_feature2': '🕯️ 45+ Candlestick-Muster Erkennung',
        'welcome_feature3': '📈 Fibonacci Levels und Support/Resistance',
        'welcome_feature4': '🤖 KI-gestützte Marktanalyse (optional)',
        'welcome_feature5': '📋 Professionelle Berichte',
        'analysis_error': 'Fehler bei der Analyse',
        'try_different': 'Bitte versuchen Sie es mit einem anderen Symbol oder Zeitraum',
        'reasoning': 'Begründung',
        'sentiment_explanation': 'Das Sentiment basiert auf mehreren Faktoren',
        
        # Pattern Signals
        'bullish_reversal': 'Bullische Umkehr',
        'bearish_reversal': 'Bearische Umkehr',
        'bullish_continuation': 'Bullische Fortsetzung',
        'bearish_continuation': 'Bearische Fortsetzung',
        'strong_bullish': 'Stark Bullisch',
        'strong_bearish': 'Stark Bearisch',
        'neutral': 'Neutral',
        'indecision': 'Unentschlossenheit',
        
        # Reliability Levels
        'very_high': 'Sehr Hoch',
        'medium': 'Mittel',
        'low': 'Niedrig',
    },
    
    'en': {
        # Main UI
        'app_title': '🚀 Advanced Index Analyzer with AI',
        'settings': '⚙️ Settings',
        'select_index': 'Select Index',
        'custom_symbol': 'Use Custom Symbol',
        'ticker_symbol': 'Ticker Symbol',
        'period': 'Period',
        'interval': 'Interval',
        'ai_settings': '🤖 AI Settings',
        'enable_ai': 'Enable AI Analysis',
        'creativity': 'Creativity',
        'max_tokens': 'Max Tokens',
        'token_warning': '⚠️ High token count may slow down generation',
        'token_warning_llm': 'Make sure your LLM supports this amount',
        'advanced_settings': '🔧 Advanced Settings',
        'section_tokens': 'Token Limits per Section',
        'tokens_indicators': 'Tokens for Indicator Analysis',
        'tokens_probabilities': 'Tokens for Probability Analysis',
        'tokens_fibonacci': 'Tokens for Fibonacci/Support/Resistance',
        'tokens_questions': 'Tokens for Q&A',
        'tokens_help': 'Higher values = more detailed analysis, but longer generation time',
        'start_analysis': '🔍 Start Analysis',
        'language': '🌐 Language',
        'save_settings': '💾 Save Settings',
        'reset_settings': '🔄 Reset Settings',
        'settings_saved': '✓ Settings saved!',
        'settings_reset': '✓ Settings reset!',
        'settings_save_failed': 'Failed to save settings',
        'settings_reset_failed': 'Failed to reset settings',
        
        # Status Messages
        'loading_data': '🔄 Loading data and performing analysis...',
        'error_loading': '❌ Error loading data. Please check the symbol.',
        'analysis_complete': '✅ Analysis complete!',
        'ai_disabled': '🤖 AI analysis is disabled. Enable it in settings.',
        'generating_report': '📝 Generating professional market report...',
        
        # Tabs
        'tab_overview': '📊 Overview',
        'tab_charts': '📈 Charts',
        'tab_indicators': '🔍 Indicators',
        'tab_patterns': '🕯️ Candlestick Patterns',
        'tab_ai_analysis': '🤖 AI Analysis',
        'tab_report': '📋 Report',
        
        # Metrics
        'current_price': 'Current Price',
        'market_sentiment': 'Market Sentiment',
        'volatility': 'Volatility (ATR)',
        'strength': 'Strength',
        'overbought': 'Overbought',
        'oversold': 'Oversold',
        'normal': 'Normal',
        'high': 'High',
        
        # Probabilities
        'scenario_probabilities': '📊 Scenario Probabilities',
        'bullish': 'Bullish',
        'bearish': 'Bearish',
        'probability': 'Probability',
        'signal_analysis': 'Signal Analysis',
        'bullish_signals': '🟢 Bullish Signals',
        'bearish_signals': '🔴 Bearish Signals',
        
        # Targets
        'price_targets': '🎯 Price Targets',
        'bullish_targets': '📈 Bullish Targets',
        'bearish_targets': '📉 Bearish Targets',
        
        # Indicators
        'trend_indicators': '📊 Trend Indicators',
        'momentum_indicators': '🎯 Momentum Indicators',
        'volume_indicators': '💰 Volume Indicators',
        'pivot_points': '📍 Pivot Points',
        'resistance': 'Resistance',
        'support': 'Support',
        
        # Candlestick Patterns
        'candlestick_analysis': '🕯️ Candlestick Pattern Analysis',
        'patterns_found': 'Patterns found',
        'pattern_statistics': '📊 Pattern Statistics',
        'total_patterns': 'Total Patterns',
        'recent_patterns': 'Recent Patterns',
        'pattern': 'Pattern',
        'signal': 'Signal',
        'reliability': 'Reliability',
        'date': 'Date',
        'price': 'Price',
        
        # Charts
        'technical_analysis': 'Technical Analysis',
        'correlation_matrix': '🔥 Indicator Correlations',
        'volume_analysis': '📊 Volume Analysis',
        'volume_trend': 'Volume Trend',
        '20_day_average': '20-Day Average',
        'volume': 'Volume',
        
        # AI Analysis
        'ai_analysis': '🤖 AI-Powered Analysis',
        'technical_analysis_ai': '📊 Technical Analysis',
        'scenario_analysis': '🎲 Scenario Analysis',
        'fibonacci_sr_analysis': '📐 Fibonacci & Support/Resistance Analysis',
        'ask_ai': '💬 Ask the AI',
        'ask_question': '🤔 Ask Question',
        'ai_thinking': '🧠 AI is analyzing the data...',
        'answer': '💡 Answer',
        'question_placeholder': 'e.g., What trading strategy would you recommend?',
        
        # Report
        'market_report': '📋 Comprehensive Market Report',
        'generate_report': '📄 Generate Report',
        'download_report': '📥 Download Report',
        
        # Footer
        'footer_version': '🚀 Advanced Index Analyzer v1.0 | Powered by yfinance & Local LLM',
        'footer_disclaimer': '⚠️ Note: This analysis is for informational purposes only and does not constitute investment advice.',
        
        # Welcome Messages
        'welcome_title': 'Welcome to Advanced Index Analyzer!',
        'welcome_step1': '1. Select an index or enter your own symbol',
        'welcome_step2': '2. Set period and interval',
        'welcome_step3': '3. Click on',
        'welcome_features': 'The analysis includes:',
        'welcome_feature1': '📊 Over 30 technical indicators',
        'welcome_feature2': '🕯️ 45+ Candlestick pattern recognition',
        'welcome_feature3': '📈 Fibonacci levels and Support/Resistance',
        'welcome_feature4': '🤖 AI-powered market analysis (optional)',
        'welcome_feature5': '📋 Professional reports',
        'analysis_error': 'Error during analysis',
        'try_different': 'Please try a different symbol or time period',
        'reasoning': 'Reasoning',
        'sentiment_explanation': 'The sentiment is based on multiple factors',
        
        # Pattern Signals
        'bullish_reversal': 'Bullish Reversal',
        'bearish_reversal': 'Bearish Reversal',
        'bullish_continuation': 'Bullish Continuation',
        'bearish_continuation': 'Bearish Continuation',
        'strong_bullish': 'Strong Bullish',
        'strong_bearish': 'Strong Bearish',
        'neutral': 'Neutral',
        'indecision': 'Indecision',
        
        # Reliability Levels
        'very_high': 'Very High',
        'medium': 'Medium',
        'low': 'Low',
    }
}

def get_text(key: str, lang: str = 'de') -> str:
    """
    Gibt den übersetzten Text für einen Schlüssel zurück
    
    Args:
        key: Der Übersetzungsschlüssel
        lang: Die Sprache ('de' oder 'en')
    
    Returns:
        Der übersetzte Text oder der Schlüssel wenn nicht gefunden
    """
    if lang not in TRANSLATIONS:
        lang = 'de'
    
    return TRANSLATIONS[lang].get(key, key)