"""
Debug-Utility für den Index Analyser
Zeigt den aktuellen Session State und hilft bei der Fehlersuche
"""

import streamlit as st
import json
import pandas as pd

def show_debug_info():
    """
    Zeigt Debug-Informationen im Sidebar
    """
    with st.sidebar:
        with st.expander("🐛 Debug Info"):
            st.markdown("### Session State")
            
            # Zeige ob Daten vorhanden sind
            if st.session_state.get('analysis_data'):
                st.success("✅ Analysis Data vorhanden")
                
                # Zeige verfügbare Keys
                data_keys = st.session_state.analysis_data.keys()
                st.markdown("**Verfügbare Daten:**")
                for key in data_keys:
                    if key == 'data':
                        df = pd.DataFrame(st.session_state.analysis_data['data'])
                        st.markdown(f"- {key}: {len(df)} Datenpunkte")
                    elif key == 'indicators':
                        ind_count = len(st.session_state.analysis_data['indicators'])
                        st.markdown(f"- {key}: {ind_count} Indikatoren")
                    elif key == 'probabilities':
                        st.markdown(f"- {key}: ✓")
                    elif key == 'targets':
                        targets = st.session_state.analysis_data['targets']
                        bullish_count = len(targets.get('bullish', []))
                        bearish_count = len(targets.get('bearish', []))
                        st.markdown(f"- {key}: {bullish_count} bullisch, {bearish_count} bearisch")
                    else:
                        st.markdown(f"- {key}: ✓")
            else:
                st.warning("⚠️ Keine Analysis Data")
            
            # Zeige Candlestick Patterns
            if st.session_state.get('candlestick_patterns'):
                patterns = st.session_state.candlestick_patterns
                if patterns.get('statistics'):
                    stats = patterns['statistics']
                    st.success(f"✅ {stats.get('total_patterns', 0)} Patterns gefunden")
                else:
                    st.warning("⚠️ Keine Pattern-Statistiken")
            else:
                st.warning("⚠️ Keine Candlestick Patterns")
            
            # Zeige andere Session State Variablen
            st.markdown("**Weitere Einstellungen:**")
            st.markdown(f"- Language: {st.session_state.get('language', 'nicht gesetzt')}")
            st.markdown(f"- Use LLM: {st.session_state.get('use_llm', 'nicht gesetzt')}")
            
            # Test-Button zum Laden von Beispieldaten
            if st.button("🧪 Lade Test-Daten"):
                load_test_data()

def load_test_data():
    """
    Lädt Test-Daten für Debugging-Zwecke
    """
    import yfinance as yf
    from analysis import TechnicalAnalysis
    from candlestick_patterns import CandlestickPatterns
    
    with st.spinner("Lade Test-Daten..."):
        # Lade S&P 500 Daten
        analysis = TechnicalAnalysis("^GSPC", "1mo", "1d")
        
        if analysis.fetch_data():
            analysis.calculate_all_indicators()
            analysis.calculate_fibonacci_levels()
            analysis.identify_support_resistance()
            
            # Erkenne Patterns
            pattern_detector = CandlestickPatterns(analysis.data)
            patterns = pattern_detector.detect_all_patterns()
            pattern_stats = pattern_detector.get_pattern_statistics()
            
            # Berechne Wahrscheinlichkeiten
            probabilities = analysis.calculate_probabilities()
            targets = analysis.calculate_price_targets()
            
            # Speichere in Session State
            st.session_state.analysis_data = {
                'ticker': "^GSPC",
                'data': analysis.data.to_dict(),
                'indicators': analysis.indicators,
                'fibonacci': analysis.fibonacci_levels,
                'support_resistance': analysis.support_resistance,
                'probabilities': probabilities,
                'targets': targets,
                'sentiment': analysis.get_market_sentiment()
            }
            
            st.session_state.candlestick_patterns = {
                'patterns': patterns,
                'statistics': pattern_stats
            }
            
            st.success("✅ Test-Daten geladen!")
            st.rerun()
        else:
            st.error("❌ Fehler beim Laden der Test-Daten")

def check_data_integrity():
    """
    Überprüft die Integrität der gespeicherten Daten
    """
    issues = []
    
    if not st.session_state.get('analysis_data'):
        issues.append("Keine Analyse-Daten vorhanden")
    else:
        data = st.session_state.analysis_data
        
        # Prüfe erforderliche Keys
        required_keys = ['ticker', 'data', 'indicators', 'probabilities', 'targets']
        for key in required_keys:
            if key not in data:
                issues.append(f"Fehlender Key: {key}")
        
        # Prüfe Datenqualität
        if 'data' in data:
            df_data = data['data']
            if not df_data:
                issues.append("Leere Kursdaten")
            else:
                # Prüfe ob es ein Dictionary ist
                if not isinstance(df_data, dict):
                    issues.append(f"Kursdaten haben falschen Typ: {type(df_data)}")
        
        if 'indicators' in data:
            if not data['indicators']:
                issues.append("Keine Indikatoren berechnet")
    
    return issues

def display_data_issues():
    """
    Zeigt Datenprobleme an, wenn welche gefunden werden
    """
    issues = check_data_integrity()
    
    if issues:
        with st.sidebar:
            with st.expander("⚠️ Datenprobleme", expanded=True):
                st.markdown("Folgende Probleme wurden gefunden:")
                for issue in issues:
                    st.markdown(f"- {issue}")
                
                st.markdown("**Lösungsvorschläge:**")
                st.markdown("1. Klicken Sie auf 'Analyse starten'")
                st.markdown("2. Oder laden Sie Test-Daten (siehe Debug Info)")

if __name__ == "__main__":
    # Teste die Debug-Funktionen
    st.title("Debug Utility Test")
    
    show_debug_info()
    display_data_issues()
    
    # Zeige rohe Session State Daten
    st.markdown("### Rohe Session State Daten")
    st.json({
        key: str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        for key, value in st.session_state.items()
    })