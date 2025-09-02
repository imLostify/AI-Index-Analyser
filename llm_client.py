"""
Enhanced LLM Client für strukturierte und konsistente Berichtsgenerierung
"""

import json
import warnings
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from openai import OpenAI
    OPENAI_V1 = True
except ImportError:
    import openai
    OPENAI_V1 = False

from config import LLM_API_BASE, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

class LLMClient:
    def __init__(self):
        """Initialisiert den OpenAI Client"""
        try:
            if OPENAI_V1:
                timeout_settings = httpx.Timeout(600.0)
                self.client = OpenAI(
                    base_url=LLM_API_BASE,
                    api_key="not-needed",
                    http_client=httpx.Client(timeout=timeout_settings),
                    timeout=600.0
                )
            else:
                import openai
                openai.api_base = LLM_API_BASE
                openai.api_key = "not-needed"
                self.client = None
                
            self.model = LLM_MODEL
            self.is_available = True
            
        except Exception as e:
            print(f"⚠️ LLM Client Fehler: {str(e)}")
            self.client = None
            self.model = LLM_MODEL
            self.is_available = False

    def _make_request(self, messages: list, temperature: float = None, max_tokens: int = None) -> str:
        """Führt eine Anfrage an das LLM aus"""
        if not self.is_available:
            return self._generate_fallback_report()

        temperature = temperature or LLM_TEMPERATURE
        max_tokens = min(max_tokens or LLM_MAX_TOKENS, 25000)

        try:
            if OPENAI_V1 and self.client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=600.0
                )
                return response.choices[0].message.content
            else:
                import openai
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=600
                )
                return response['choices'][0]['message']['content']
        except Exception as e:
            return self._generate_fallback_report()

    def _prepare_data_for_json(self, data: Any) -> Any:
        """Bereitet Daten für JSON vor und entfernt NaN/Inf Werte"""
        import numpy as np
        import pandas as pd
        
        if isinstance(data, (np.integer, np.floating)):
            if np.isnan(data) or np.isinf(data):
                return None
            return float(data)
        elif isinstance(data, np.ndarray):
            return [self._prepare_data_for_json(x) for x in data if not (isinstance(x, float) and (np.isnan(x) or np.isinf(x)))]
        elif isinstance(data, pd.Series):
            return {k: self._prepare_data_for_json(v) for k, v in data.to_dict().items() if v is not None}
        elif isinstance(data, pd.DataFrame):
            return data.replace([np.inf, -np.inf], np.nan).dropna().to_dict('records')
        elif isinstance(data, dict):
            return {k: self._prepare_data_for_json(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._prepare_data_for_json(item) for item in data if item is not None]
        elif isinstance(data, (pd.Timestamp, datetime)):
            return str(data)
        elif pd.isna(data):
            return None
        else:
            return data

    def _validate_indicators(self, indicators: Dict) -> Dict:
        """Validiert und bereinigt Indikator-Werte"""
        validated = {}
        
        # RSI - sollte zwischen 0 und 100 sein
        if 'RSI' in indicators:
            rsi = indicators.get('RSI')
            if rsi is not None and 0 <= rsi <= 100:
                validated['RSI'] = round(rsi, 2)
        
        # MACD
        if 'MACD' in indicators:
            macd = indicators.get('MACD', {})
            if isinstance(macd, dict):
                validated['MACD'] = {
                    'macd': round(macd.get('macd', 0), 4) if macd.get('macd') is not None else None,
                    'signal': round(macd.get('signal', 0), 4) if macd.get('signal') is not None else None,
                    'histogram': round(macd.get('histogram', 0), 4) if macd.get('histogram') is not None else None
                }
        
        # ATR - sollte positiv sein
        if 'ATR' in indicators:
            atr = indicators.get('ATR')
            if atr is not None and atr > 0:
                validated['ATR'] = round(atr, 2)
        
        # Moving Averages
        if 'moving_averages' in indicators:
            ma = indicators.get('moving_averages', {})
            validated['moving_averages'] = {
                'ema': {k: round(v, 2) for k, v in ma.get('ema', {}).items() if v is not None},
                'sma': {k: round(v, 2) for k, v in ma.get('sma', {}).items() if v is not None}
            }
        
        # Stochastic
        if 'Stochastic' in indicators:
            stoch = indicators.get('Stochastic', {})
            if isinstance(stoch, dict):
                validated['Stochastic'] = {
                    'K': round(stoch.get('K', 0), 2) if stoch.get('K') is not None else None,
                    'D': round(stoch.get('D', 0), 2) if stoch.get('D') is not None else None
                }
        
        # Weitere Indikatoren
        for key in ['ADX', 'CCI', 'MFI', 'OBV', 'VWAP', 'Williams_R', 'CMF', 'ROC']:
            if key in indicators and indicators[key] is not None:
                if isinstance(indicators[key], dict):
                    validated[key] = {k: round(v, 2) if v is not None else None 
                                    for k, v in indicators[key].items()}
                else:
                    validated[key] = round(indicators[key], 2)
        
        # Bollinger Bands
        if 'Bollinger' in indicators:
            bb = indicators.get('Bollinger', {})
            if isinstance(bb, dict):
                validated['Bollinger'] = {
                    'upper': round(bb.get('upper', 0), 2) if bb.get('upper') is not None else None,
                    'middle': round(bb.get('middle', 0), 2) if bb.get('middle') is not None else None,
                    'lower': round(bb.get('lower', 0), 2) if bb.get('lower') is not None else None,
                    'width': round(bb.get('width', 0), 2) if bb.get('width') is not None else None
                }
        
        # Pivots
        if 'Pivots' in indicators:
            pivots = indicators.get('Pivots', {})
            if isinstance(pivots, dict):
                validated['Pivots'] = {k: round(v, 2) if v is not None else None 
                                     for k, v in pivots.items()}
        
        return validated

    def generate_comprehensive_report(self, full_analysis: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """
        Generiert einen umfassenden, strukturierten Marktbericht mit LLM
        
        Args:
            full_analysis: Vollständige Analysedaten
            max_tokens: Maximale Token-Anzahl
            language: Sprache des Berichts ('de' oder 'en')
        """
        try:
            # Bereite und validiere Daten vor
            clean_analysis = self._prepare_data_for_json(full_analysis)
            ticker = clean_analysis.get('ticker', 'INDEX')
            current_price = clean_analysis.get('current_price', 0)
            
            # Validiere Indikatoren für konsistente Werte
            indicators = self._validate_indicators(clean_analysis.get('indicators', {}))
            
            # Bestimme konsistente Marktrichtung für den Bericht
            market_direction = self._determine_market_direction(
                indicators, 
                clean_analysis.get('probabilities', {}),
                language
            )
            
            # Erstelle strukturierten Prompt für das LLM basierend auf Sprache
            if language == 'en':
                prompt = f"""
            Create a professional, technical analysis report for {ticker}.
            
            IMPORTANT - Use ONLY these validated data:
            
            Ticker: {ticker}
            Current Price: ${current_price:.2f}
            
            VALIDATED INDICATORS (use exactly these values):
            {json.dumps(indicators, indent=2, default=str)}
            
            PROBABILITIES:
            {json.dumps(clean_analysis.get('probabilities', {}), indent=2)}
            
            PRICE TARGETS:
            {json.dumps(clean_analysis.get('price_targets', {}), indent=2, default=str)[:1000]}
            
            SUPPORT/RESISTANCE:
            {json.dumps(clean_analysis.get('support_resistance', {}), indent=2, default=str)[:1000]}
            
            MARKET DIRECTION (use consistently):
            - Primary Direction: {market_direction['primary']}
            - Recommendation: {market_direction['recommendation']}
            - Strength: {market_direction['strength']}/10
            
            REQUIREMENTS:
            1. Use EXACTLY the indicator values mentioned above - no custom calculations
            2. Be CONSISTENT - if market direction is {market_direction['primary']}, 
               all sections must support this assessment
            3. No contradictions between different sections
            4. Format numbers correctly: $23,415.42 (with comma as thousands separator)
            5. Use ATR for Stop-Loss: {indicators.get('ATR', 'N/A')}
            6. Use actual Support/Resistance levels from the data
            7. Structure the report with clear headings
            8. Provide specific, actionable trading recommendations
            9. Avoid speculation - base everything on given data
            10. Explicitly mention that all values come from technical analysis
            
            STRUCTURE:
            1. Executive Summary (Market overview, consistent assessment)
            2. Technical Indicators (with exact values)
            3. Trading Setup (Entry, Stop-Loss with ATR, Targets)
            4. Risk Management
            5. Action Items
            6. Summary
            
            Create a professional report in English.
            """
            else:
                prompt = f"""
            Erstelle einen professionellen, technischen Analysebericht für {ticker}.
            
            WICHTIG - Verwende NUR diese validierten Daten:
            
            Ticker: {ticker}
            Aktueller Kurs: ${current_price:.2f}
            
            VALIDIERTE INDIKATOREN (nutze exakt diese Werte):
            {json.dumps(indicators, indent=2, default=str)}
            
            WAHRSCHEINLICHKEITEN:
            {json.dumps(clean_analysis.get('probabilities', {}), indent=2)}
            
            KURSZIELE:
            {json.dumps(clean_analysis.get('price_targets', {}), indent=2, default=str)[:1000]}
            
            SUPPORT/RESISTANCE:
            {json.dumps(clean_analysis.get('support_resistance', {}), indent=2, default=str)[:1000]}
            
            MARKTRICHTUNG (konsistent verwenden):
            - Primäre Richtung: {market_direction['primary']}
            - Empfehlung: {market_direction['recommendation']}
            - Stärke: {market_direction['strength']}/10
            
            ANFORDERUNGEN:
            1. Verwende EXAKT die oben genannten Indikatorwerte - keine eigenen Berechnungen
            2. Sei KONSISTENT - wenn die Marktrichtung {market_direction['primary']} ist, 
               müssen alle Abschnitte diese Einschätzung unterstützen
            3. Keine Widersprüche zwischen verschiedenen Abschnitten
            4. Formatiere Zahlen korrekt: $23,415.42 (mit Komma als Tausendertrennzeichen)
            5. ATR für Stop-Loss verwenden: {indicators.get('ATR', 'N/A')}
            6. Nutze die tatsächlichen Support/Resistance Levels aus den Daten
            7. Strukturiere den Bericht mit klaren Überschriften
            8. Gib konkrete, umsetzbare Trading-Empfehlungen
            9. Vermeide Spekulationen - basiere alles auf den gegebenen Daten
            10. Erwähne explizit, dass alle Werte aus der technischen Analyse stammen
            
            STRUKTUR:
            1. Executive Summary (Marktübersicht, konsistente Einschätzung)
            2. Technische Indikatoren (mit den exakten Werten)
            3. Trading-Setup (Entry, Stop-Loss mit ATR, Targets)
            4. Risikomanagement 
            5. Handlungsempfehlungen
            6. Zusammenfassung
            
            Erstelle einen professionellen Bericht in deutscher Sprache.
            """
            
            messages = [
                {"role": "system", "content": "You are a professional financial analyst. Create consistent, data-driven reports without contradictions. ALWAYS use the provided data." if language == 'en' else "Du bist ein professioneller Finanzanalyst. Erstelle konsistente, datenbasierte Berichte ohne Widersprüche. Verwende IMMER die bereitgestellten Daten."},
                {"role": "user", "content": prompt}
            ]
            
            # Generiere Bericht mit LLM
            report = self._make_request(messages, temperature=0.3, max_tokens=max_tokens)
            
            # Füge Metadaten hinzu
            report = self._add_report_metadata(report, ticker, current_price, market_direction, language)
            
            return report
            
        except Exception as e:
            print(f"⚠️ Fehler bei Berichtsgenerierung: {str(e)}")
            return self._generate_fallback_report(language)

    def _add_report_metadata(self, report: str, ticker: str, price: float, market_direction: Dict, language: str = 'de') -> str:
        """
        Fügt Metadaten zum Bericht hinzu
        """
        if not report:
            return self._generate_fallback_report(language)
        
        # Füge Header hinzu wenn nicht vorhanden
        if not report.startswith('#'):
            if language == 'en':
                header = f"""
# 📊 TECHNICAL ANALYSIS - {ticker}

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Current Price:** ${price:,.2f}  
**Market Direction:** {market_direction['primary']}  
**Recommendation:** {market_direction['recommendation']}

---

"""
            else:
                header = f"""
# 📊 TECHNISCHE ANALYSE - {ticker}

**Analysedatum:** {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr  
**Aktueller Kurs:** ${price:,.2f}  
**Marktrichtung:** {market_direction['primary']}  
**Empfehlung:** {market_direction['recommendation']}

---

"""
            report = header + report
        
        # Füge Footer hinzu wenn nicht vorhanden
        if 'Disclaimer' not in report and 'Anlageberatung' not in report:
            if language == 'en':
                footer = f"""

---

*Analysis created on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*  
*All values are from technical analysis via yfinance.*  
*Disclaimer: This analysis is for informational purposes only and does not constitute investment advice.*
"""
            else:
                footer = f"""

---

*Analyse erstellt am {datetime.now().strftime('%d.%m.%Y um %H:%M:%S Uhr')}*  
*Alle Werte stammen aus der technischen Analyse von yfinance.*  
*Disclaimer: Diese Analyse dient nur zu Informationszwecken und stellt keine Anlageberatung dar.*
"""
            report += footer
        
        return report

    def _generate_consistent_report(self, data: Dict, language: str = 'de') -> str:
        """Generiert einen konsistenten Fallback-Bericht ohne LLM"""
        
        ticker = data['ticker']
        price = data['current_price']
        indicators = data['indicators']
        probabilities = data['probabilities']
        targets = data['targets']
        
        # Bestimme konsistente Marktrichtung basierend auf tatsächlichen Daten
        market_direction = self._determine_market_direction(indicators, probabilities, language)
        
        report = f"""
# 📊 TECHNISCHE ANALYSE - {ticker}

**Analysedatum:** {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr  
**Aktueller Kurs:** ${price:,.2f}

---

## 🎯 EXECUTIVE SUMMARY

### Marktübersicht
Der {ticker} notiert bei **${price:,.2f}**. {self._get_trend_description(indicators, market_direction)}

### Konsistente Markteinschätzung
**Primäre Richtung:** {market_direction['primary']}  
**Trend-Stärke:** {market_direction['strength']}/10  
**Empfehlung:** {market_direction['recommendation']}

---

## 📈 TECHNISCHE INDIKATOREN

### Trend-Indikatoren
{self._format_trend_indicators(indicators)}

### Momentum-Indikatoren
{self._format_momentum_indicators(indicators)}

### Volatilität
{self._format_volatility_indicators(indicators)}

---

## 💼 TRADING-SETUP

{self._generate_trading_setup(data, market_direction)}

---

## ⚖️ RISIKOMANAGEMENT

{self._generate_risk_management(data, indicators)}

---

## 🎯 HANDLUNGSEMPFEHLUNGEN

{self._generate_action_items(data, market_direction)}

---

## 📊 ZUSAMMENFASSUNG

{self._generate_summary(data, market_direction)}

---
*Dieser Bericht basiert auf den tatsächlichen Marktdaten und technischen Indikatoren.*  
*Alle Werte wurden direkt aus der yfinance-Analyse übernommen.*
"""
        return report

    def _determine_market_direction(self, indicators: Dict, probabilities: Dict, language: str = 'de') -> Dict:
        """Bestimmt konsistent die Marktrichtung basierend auf echten Daten"""
        
        score = 0
        factors = []
        
        # RSI Bewertung
        rsi = indicators.get('RSI')
        if rsi:
            if rsi > 70:
                score -= 2
                factors.append(f"RSI überkauft ({rsi:.2f})")
            elif rsi > 50:
                score += 1
                factors.append(f"RSI bullisch ({rsi:.2f})")
            elif rsi < 30:
                score += 2
                factors.append(f"RSI überverkauft ({rsi:.2f})")
            else:
                score -= 1
                factors.append(f"RSI bearisch ({rsi:.2f})")
        
        # MACD Bewertung
        macd = indicators.get('MACD', {})
        if macd and macd.get('histogram') is not None:
            hist = macd['histogram']
            if hist > 0:
                score += 2
                factors.append(f"MACD positiv ({hist:.4f})")
            else:
                score -= 2
                factors.append(f"MACD negativ ({hist:.4f})")
        
        # Wahrscheinlichkeiten
        bullish_prob = probabilities.get('bullish_probability', 33)
        bearish_prob = probabilities.get('bearish_probability', 33)
        
        if bullish_prob > bearish_prob * 1.5:
            score += 2
            factors.append(f"Bullische Signale dominieren ({bullish_prob:.1f}%)")
        elif bearish_prob > bullish_prob * 1.5:
            score -= 2
            factors.append(f"Bearische Signale dominieren ({bearish_prob:.1f}%)")
        
        # Bestimme finale Richtung basierend auf Sprache
        if language == 'en':
            if score >= 3:
                primary = "STRONG BULLISH 🚀"
                recommendation = "BUY - Strong upward signals"
                strength = min(10, 7 + score // 2)
            elif score >= 1:
                primary = "BULLISH 📈"
                recommendation = "CAUTIOUS BUY - Positive signals prevail"
                strength = 6
            elif score >= -1:
                primary = "NEUTRAL ➡️"
                recommendation = "WAIT - No clear direction"
                strength = 5
            elif score >= -3:
                primary = "BEARISH 📉"
                recommendation = "CAUTIOUS SELL - Negative signals prevail"
                strength = 4
            else:
                primary = "STRONG BEARISH 🔻"
                recommendation = "SELL - Strong downward signals"
                strength = max(1, 3 + score // 2)
        else:
            if score >= 3:
                primary = "STARK BULLISCH 🚀"
                recommendation = "KAUFEN - Starke Aufwärtssignale"
                strength = min(10, 7 + score // 2)
            elif score >= 1:
                primary = "BULLISCH 📈"
                recommendation = "VORSICHTIG KAUFEN - Positive Signale überwiegen"
                strength = 6
            elif score >= -1:
                primary = "NEUTRAL ➡️"
                recommendation = "ABWARTEN - Keine klare Richtung"
                strength = 5
            elif score >= -3:
                primary = "BEARISCH 📉"
                recommendation = "VORSICHTIG VERKAUFEN - Negative Signale überwiegen"
                strength = 4
            else:
                primary = "STARK BEARISCH 🔻"
                recommendation = "VERKAUFEN - Starke Abwärtssignale"
                strength = max(1, 3 + score // 2)
        
        return {
            'primary': primary,
            'recommendation': recommendation,
            'strength': strength,
            'score': score,
            'factors': factors
        }

    def _get_trend_description(self, indicators: Dict, market_direction: Dict) -> str:
        """Generiert konsistente Trendbeschreibung"""
        
        direction = market_direction['primary']
        factors = market_direction['factors']
        
        if 'BULLISCH' in direction:
            base = "Die technischen Indikatoren zeigen eine bullische Tendenz."
        elif 'BEARISCH' in direction:
            base = "Die technischen Indikatoren zeigen eine bearische Tendenz."
        else:
            base = "Der Markt befindet sich in einer neutralen Phase ohne klare Richtung."
        
        # Füge wichtigste Faktoren hinzu
        if factors:
            base += f" Hauptfaktoren: {', '.join(factors[:2])}."
        
        return base

    def _format_trend_indicators(self, indicators: Dict) -> str:
        """Formatiert Trend-Indikatoren"""
        lines = []
        
        # Moving Averages
        if 'moving_averages' in indicators:
            ma = indicators['moving_averages']
            if 'ema' in ma:
                for period, value in sorted(ma['ema'].items()):
                    if value:
                        lines.append(f"• **EMA {period}:** ${value:,.2f}")
        
        # ADX
        if 'ADX' in indicators:
            adx = indicators['ADX']
            if isinstance(adx, dict) and adx.get('adx'):
                trend_strength = "Starker Trend" if adx['adx'] > 25 else "Schwacher Trend"
                lines.append(f"• **ADX:** {adx['adx']:.2f} ({trend_strength})")
        
        # VWAP (nur wenn vorhanden)
        if 'VWAP' in indicators and indicators['VWAP']:
            lines.append(f"• **VWAP:** ${indicators['VWAP']:,.2f}")
        
        return '\n'.join(lines) if lines else "Keine Trend-Indikatoren verfügbar"

    def _format_momentum_indicators(self, indicators: Dict) -> str:
        """Formatiert Momentum-Indikatoren"""
        lines = []
        
        # RSI
        if 'RSI' in indicators and indicators['RSI']:
            rsi = indicators['RSI']
            status = "Überkauft" if rsi > 70 else "Überverkauft" if rsi < 30 else "Neutral"
            lines.append(f"• **RSI (14):** {rsi:.2f} ({status})")
        
        # MACD
        if 'MACD' in indicators:
            macd = indicators['MACD']
            if isinstance(macd, dict):
                if macd.get('histogram') is not None:
                    signal = "Bullisch" if macd['histogram'] > 0 else "Bearisch"
                    lines.append(f"• **MACD Histogram:** {macd['histogram']:.4f} ({signal})")
                if macd.get('macd') is not None and macd.get('signal') is not None:
                    lines.append(f"  - MACD: {macd['macd']:.4f}")
                    lines.append(f"  - Signal: {macd['signal']:.4f}")
        
        # Stochastic
        if 'Stochastic' in indicators:
            stoch = indicators['Stochastic']
            if isinstance(stoch, dict):
                if stoch.get('K') is not None and stoch.get('D') is not None:
                    lines.append(f"• **Stochastic K/D:** {stoch['K']:.2f} / {stoch['D']:.2f}")
        
        return '\n'.join(lines) if lines else "Keine Momentum-Indikatoren verfügbar"

    def _format_volatility_indicators(self, indicators: Dict) -> str:
        """Formatiert Volatilitäts-Indikatoren"""
        lines = []
        
        # ATR
        if 'ATR' in indicators and indicators['ATR']:
            atr = indicators['ATR']
            lines.append(f"• **ATR (14):** ${atr:.2f}")
        
        # Bollinger Bands
        if 'Bollinger' in indicators:
            bb = indicators['Bollinger']
            if isinstance(bb, dict):
                if bb.get('upper') and bb.get('lower'):
                    lines.append(f"• **Bollinger Bands:**")
                    lines.append(f"  - Upper: ${bb['upper']:,.2f}")
                    lines.append(f"  - Middle: ${bb.get('middle', 0):,.2f}")
                    lines.append(f"  - Lower: ${bb['lower']:,.2f}")
                    if bb.get('width'):
                        lines.append(f"  - Width: {bb['width']:.2f}")
        
        return '\n'.join(lines) if lines else "Keine Volatilitäts-Indikatoren verfügbar"

    def _generate_trading_setup(self, data: Dict, market_direction: Dict) -> str:
        """Generiert konsistentes Trading-Setup"""
        
        price = data['current_price']
        indicators = data['indicators']
        targets = data['targets']
        
        # Bestimme Entry basierend auf Marktrichtung
        if 'BULLISCH' in market_direction['primary']:
            # Long Setup
            atr = indicators.get('ATR', price * 0.01)
            entry = price
            stop_loss = price - (atr * 1.5)
            
            # Verwende tatsächliche Targets aus Daten
            bullish_targets = targets.get('bullish', [])
            if bullish_targets:
                target1 = bullish_targets[0]['price'] if len(bullish_targets) > 0 else price * 1.02
                target2 = bullish_targets[1]['price'] if len(bullish_targets) > 1 else price * 1.04
            else:
                target1 = price * 1.02
                target2 = price * 1.04
            
            setup = f"""### LONG Setup 📈
• **Entry:** ${entry:,.2f} (aktueller Kurs)
• **Stop-Loss:** ${stop_loss:,.2f} (1.5x ATR)
• **Target 1:** ${target1:,.2f} (50% Position)
• **Target 2:** ${target2:,.2f} (50% Position)
• **Risk/Reward:** 1:{((target1 - entry) / (entry - stop_loss)):.1f}"""
            
        elif 'BEARISCH' in market_direction['primary']:
            # Short Setup
            atr = indicators.get('ATR', price * 0.01)
            entry = price
            stop_loss = price + (atr * 1.5)
            
            # Verwende tatsächliche Targets aus Daten
            bearish_targets = targets.get('bearish', [])
            if bearish_targets:
                target1 = bearish_targets[0]['price'] if len(bearish_targets) > 0 else price * 0.98
                target2 = bearish_targets[1]['price'] if len(bearish_targets) > 1 else price * 0.96
            else:
                target1 = price * 0.98
                target2 = price * 0.96
            
            setup = f"""### SHORT Setup 📉
• **Entry:** ${entry:,.2f} (aktueller Kurs)
• **Stop-Loss:** ${stop_loss:,.2f} (1.5x ATR)
• **Target 1:** ${target1:,.2f} (50% Position)
• **Target 2:** ${target2:,.2f} (50% Position)
• **Risk/Reward:** 1:{abs((entry - target1) / (stop_loss - entry)):.1f}"""
            
        else:
            # Neutral - kein Trade
            setup = """### KEIN TRADE ⏸️
• **Grund:** Keine klare Marktrichtung
• **Empfehlung:** Warten auf eindeutige Signale
• **Beobachten:** RSI-Divergenzen, MACD-Kreuzungen, Volumen-Spikes"""
        
        return setup

    def _generate_risk_management(self, data: Dict, indicators: Dict) -> str:
        """Generiert Risikomanagement-Empfehlungen"""
        
        atr = indicators.get('ATR', data['current_price'] * 0.01)
        
        return f"""### Position Sizing
• **Risiko pro Trade:** Max. 2% des Portfolios
• **ATR-basierter Stop:** ${atr:.2f} (1x ATR)
• **Erweiteter Stop:** ${atr * 1.5:.2f} (1.5x ATR)
• **Max. Positionsgröße:** Bei $100,000 Kapital = $2,000 Risiko

### Stop-Loss Regeln
• **Initial Stop:** 1.5x ATR vom Entry
• **Trailing Stop:** Aktivieren bei +1R Gewinn
• **Break-Even:** Nachziehen bei +2R Gewinn

### Warnsignale für Exit
• RSI-Divergenz zum Preis
• MACD-Kreuzung gegen Position
• Volumen-Spike gegen Trend
• Durchbruch wichtiger Support/Resistance"""

    def _generate_action_items(self, data: Dict, market_direction: Dict) -> str:
        """Generiert konkrete Handlungsempfehlungen"""
        
        if 'BULLISCH' in market_direction['primary']:
            actions = """### ✅ Sofort-Aktionen
1. **Long-Position vorbereiten** (noch nicht ausführen)
2. **Stop-Loss berechnen** (1.5x ATR)
3. **Position Size festlegen** (2% Risiko)

### 📊 Monitoring
• RSI auf Überkauf achten (>70)
• MACD-Momentum beobachten
• Volumen bei Ausbrüchen prüfen

### ⚠️ Exit-Signale
• RSI > 80 (Teilgewinn)
• MACD dreht negativ (Vollständiger Exit)
• Durchbruch unter wichtigen Support"""
            
        elif 'BEARISCH' in market_direction['primary']:
            actions = """### ✅ Sofort-Aktionen
1. **Long-Positionen reduzieren**
2. **Short-Setup vorbereiten**
3. **Defensive Stops setzen**

### 📊 Monitoring
• RSI auf Überverkauf achten (<30)
• MACD-Divergenzen suchen
• Support-Level beobachten

### ⚠️ Exit-Signale
• RSI < 20 (Teilgewinn bei Shorts)
• MACD dreht positiv
• Durchbruch über Resistance"""
            
        else:
            actions = """### ✅ Sofort-Aktionen
1. **Keine neuen Positionen**
2. **Bestehende Positionen halten**
3. **Auf klare Signale warten**

### 📊 Monitoring
• Ausbruch aus Range beobachten
• Volumen-Anstieg abwarten
• Trend-Bestätigung suchen

### ⚠️ Trigger für Action
• RSI verlässt 40-60 Range
• MACD-Kreuzung
• Ausbruch mit Volumen"""
        
        return actions

    def _generate_summary(self, data: Dict, market_direction: Dict) -> str:
        """Generiert konsistente Zusammenfassung"""
        
        return f"""**Marktrichtung:** {market_direction['primary']}  
**Trend-Stärke:** {market_direction['strength']}/10  
**Primäre Empfehlung:** {market_direction['recommendation']}

**Wichtigste Faktoren:**
{chr(10).join(f"• {factor}" for factor in market_direction['factors'][:3])}

**Risk/Reward Einschätzung:**
Der aktuelle Setup bietet ein {'günstiges' if market_direction['strength'] >= 6 else 'ungünstiges' if market_direction['strength'] <= 4 else 'neutrales'} Risk/Reward Verhältnis.

⚠️ **Disclaimer:** Diese Analyse basiert auf technischen Indikatoren und stellt keine Anlageberatung dar."""

    def _generate_fallback_report(self, language: str = 'de') -> str:
        """Generiert einen Fallback-Bericht wenn LLM nicht verfügbar"""
        if language == 'en':
            return """
# 📊 MARKET ANALYSIS REPORT
## Status: Basic Analysis (LLM not available)

Technical indicators have been successfully calculated.
Please check the Charts and Indicators tabs for details.

⚠️ For advanced AI analysis, make sure the LLM server is running.
"""
        else:
            return """
# 📊 MARKTANALYSE-BERICHT
## Status: Basis-Analyse (LLM nicht verfügbar)

Die technischen Indikatoren wurden erfolgreich berechnet.
Bitte prüfen Sie die Charts und Indikatoren-Tabs für Details.

⚠️ Für erweiterte AI-Analyse stellen Sie sicher, dass der LLM-Server läuft.
"""

    # Kompatibilitäts-Methoden
    def analyze_indicators(self, indicators: Dict, data_summary: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """Analysiert technische Indikatoren mit LLM"""
        try:
            validated_indicators = self._validate_indicators(indicators)
            current_price = data_summary.get('current_price', 0)
            
            if language == 'en':
                prompt = f"""
            Analyze these technical indicators for a professional trading decision.
            
            Current Price: ${current_price:.2f}
            
            VALIDATED INDICATORS (use EXACTLY these values):
            {json.dumps(validated_indicators, indent=2, default=str)[:2000]}
            
            Create a structured analysis with:
            1. Market direction and trend (based on the data)
            2. Specific entry/exit points with prices
            3. Stop-loss recommendation with ATR reasoning (ATR: {validated_indicators.get('ATR', 'N/A')})
            4. Risk/Reward ratio
            
            IMPORTANT:
            - Use ONLY the given indicator values
            - Be consistent in your assessment
            - No invented numbers
            - Format prices as $X,XXX.XX
            """
            else:
                prompt = f"""
            Analysiere diese technischen Indikatoren für eine professionelle Trading-Entscheidung.
            
            Aktueller Kurs: ${current_price:.2f}
            
            VALIDIERTE INDIKATOREN (verwende EXAKT diese Werte):
            {json.dumps(validated_indicators, indent=2, default=str)[:2000]}
            
            Erstelle eine strukturierte Analyse mit:
            1. Marktrichtung und Trend (basierend auf den Daten)
            2. Konkrete Entry/Exit Punkte mit Preisen
            3. Stop-Loss Empfehlung mit ATR-Begründung (ATR: {validated_indicators.get('ATR', 'N/A')})
            4. Risk/Reward Verhältnis
            
            WICHTIG:
            - Verwende NUR die gegebenen Indikatorwerte
            - Sei konsistent in deiner Einschätzung
            - Keine erfundenen Zahlen
            - Formatiere Preise als $X,XXX.XX
            """
            
            messages = [
                {"role": "system", "content": "You are a technical analyst. ALWAYS use the exact values from the data." if language == 'en' else "Du bist ein technischer Analyst. Verwende IMMER die exakten Werte aus den Daten."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_request(messages, temperature=0.3, max_tokens=max_tokens or 1500)
            
        except Exception as e:
            return f"⚠️ Indikator-Analyse-Fehler: {str(e)}"

    def analyze_probabilities(self, probabilities: Dict, targets: Dict, sentiment: str, max_tokens: int = None, language: str = 'de') -> str:
        """Analysiert Wahrscheinlichkeiten und Kursziele mit LLM"""
        try:
            if language == 'en':
                prompt = f"""
            Analyze these probabilities for a trading strategy.
            
            PROBABILITIES:
            - Bullish: {probabilities.get('bullish_probability', 0):.1f}% ({probabilities.get('bullish_signals', 0)} signals)
            - Bearish: {probabilities.get('bearish_probability', 0):.1f}% ({probabilities.get('bearish_signals', 0)} signals)
            - Neutral: {probabilities.get('neutral_probability', 0):.1f}% ({probabilities.get('neutral_signals', 0)} signals)
            - Sentiment: {sentiment}
            
            PRICE TARGETS:
            {json.dumps(targets, indent=2, default=str)[:1000]}
            
            Provide specific trading recommendations with:
            1. Positioning (Long/Short/Neutral) based on probabilities
            2. Entry strategy
            3. Profit-taking plan with the given price targets
            4. Risk management
            
            IMPORTANT:
            - Interpret probabilities correctly
            - Use actual price targets from the data
            - Be consistent with the sentiment
            """
            else:
                prompt = f"""
            Analysiere diese Wahrscheinlichkeiten für eine Trading-Strategie.
            
            WAHRSCHEINLICHKEITEN:
            - Bullisch: {probabilities.get('bullish_probability', 0):.1f}% ({probabilities.get('bullish_signals', 0)} Signale)
            - Bearisch: {probabilities.get('bearish_probability', 0):.1f}% ({probabilities.get('bearish_signals', 0)} Signale)
            - Neutral: {probabilities.get('neutral_probability', 0):.1f}% ({probabilities.get('neutral_signals', 0)} Signale)
            - Sentiment: {sentiment}
            
            KURSZIELE:
            {json.dumps(targets, indent=2, default=str)[:1000]}
            
            Gib konkrete Handelsempfehlungen mit:
            1. Positionierung (Long/Short/Neutral) basierend auf den Wahrscheinlichkeiten
            2. Einstiegsstrategie
            3. Gewinnmitnahme-Plan mit den gegebenen Kurszielen
            4. Risikomanagement
            
            WICHTIG:
            - Interpretiere die Wahrscheinlichkeiten korrekt
            - Nutze die tatsächlichen Kursziele aus den Daten
            - Sei konsistent mit dem Sentiment
            """
            
            messages = [
                {"role": "system", "content": "You are a risk analyst. Base your recommendations on the given probabilities." if language == 'en' else "Du bist ein Risikoanalyst. Basiere deine Empfehlungen auf den gegebenen Wahrscheinlichkeiten."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_request(messages, temperature=0.3, max_tokens=max_tokens or 1200)
            
        except Exception as e:
            return f"⚠️ Wahrscheinlichkeits-Analyse-Fehler: {str(e)}"

    def _interpret_probabilities(self, bullish: float, bearish: float, neutral: float) -> str:
        """Interpretiert Wahrscheinlichkeiten"""
        if neutral > 50:
            return "Die hohe Neutralität deutet auf eine Konsolidierungsphase hin. Der Markt zeigt keine klare Richtung."
        elif bullish > bearish * 1.5:
            return "Bullische Signale dominieren deutlich. Der Markt zeigt Aufwärtspotential."
        elif bearish > bullish * 1.5:
            return "Bearische Signale dominieren. Vorsicht ist geboten."
        else:
            return "Die Signale sind ausgewogen. Keine klare Tendenz erkennbar."

    def _get_probability_recommendation(self, bullish: float, bearish: float, neutral: float) -> str:
        """Gibt Empfehlung basierend auf Wahrscheinlichkeiten"""
        if neutral > 50:
            return "**ABWARTEN** und beobachten"
        elif bullish > 60:
            return "**KAUFEN** - Bullische Signale überwiegen"
        elif bearish > 60:
            return "**VERKAUFEN** - Bearische Signale überwiegen"
        else:
            return "**VORSICHTIG AGIEREN** - Keine eindeutige Richtung"

    def analyze_fibonacci_support_resistance(self, fibonacci_levels: Dict, support_resistance: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """Analysiert Fibonacci Levels und Support/Resistance mit LLM"""
        try:
            current_price = support_resistance.get('current_price', 0)
            
            if language == 'en':
                prompt = f"""
            Analyze these technical levels for precise trading.
            
            Current Price: ${current_price:.2f}
            
            FIBONACCI LEVELS:
            {json.dumps(fibonacci_levels, indent=2, default=str)[:800]}
            
            SUPPORT & RESISTANCE:
            Support: {support_resistance.get('support', [])[:5]}
            Resistance: {support_resistance.get('resistance', [])[:5]}
            
            Identify:
            1. Critical Support/Resistance zones with exact prices from the data
            2. Confluence areas (where multiple levels converge)
            3. Trading strategies for each zone
            4. Entry/Exit/Stop-Loss points with specific prices
            5. Breakout/Breakdown scenarios
            
            IMPORTANT:
            - Use ONLY the given levels
            - No invented prices
            - Format as $X,XXX.XX
            - Reference actual Support/Resistance from the data
            """
            else:
                prompt = f"""
            Analysiere diese technischen Level für präzises Trading.
            
            Aktueller Kurs: ${current_price:.2f}
            
            FIBONACCI LEVELS:
            {json.dumps(fibonacci_levels, indent=2, default=str)[:800]}
            
            SUPPORT & RESISTANCE:
            Support: {support_resistance.get('support', [])[:5]}
            Resistance: {support_resistance.get('resistance', [])[:5]}
            
            Identifiziere:
            1. Kritische Support/Resistance Zonen mit exakten Preisen aus den Daten
            2. Confluence-Bereiche (wo mehrere Level zusammentreffen)
            3. Trading-Strategien für jede Zone
            4. Entry/Exit/Stop-Loss Punkte mit konkreten Preisen
            5. Breakout/Breakdown Szenarien
            
            WICHTIG:
            - Verwende NUR die gegebenen Level
            - Keine erfundenen Preise
            - Formatiere als $X,XXX.XX
            - Beziehe dich auf die tatsächlichen Support/Resistance aus den Daten
            """
            
            messages = [
                {"role": "system", "content": "You are a technical analyst specialized in Fibonacci and Support/Resistance. ALWAYS use the exact levels from the data." if language == 'en' else "Du bist ein technischer Analyst spezialisiert auf Fibonacci und Support/Resistance. Verwende IMMER die exakten Level aus den Daten."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_request(messages, temperature=0.3, max_tokens=max_tokens or 1800)
            
        except Exception as e:
            return f"⚠️ Fibonacci/SR-Analyse-Fehler: {str(e)}"

    def generate_market_report(self, full_analysis: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """Wrapper für Kompatibilität"""
        return self.generate_comprehensive_report(full_analysis, max_tokens, language)
    
    def generate_complete_report(self, full_analysis: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """Wrapper für Kompatibilität"""
        return self.generate_comprehensive_report(full_analysis, max_tokens, language)
    
    def answer_question(self, question: str, context: Dict, max_tokens: int = None, language: str = 'de') -> str:
        """Beantwortet Fragen basierend auf Analyse-Kontext mit LLM"""
        try:
            validated_context = self._prepare_data_for_json(context)
            validated_indicators = self._validate_indicators(validated_context.get('indicators', {}))
            
            if language == 'en':
                prompt = f"""
            Answer this question based on the technical analysis:
            
            QUESTION: {question}
            
            ANALYSIS CONTEXT:
            
            Indicators:
            {json.dumps(validated_indicators, indent=2, default=str)[:1000]}
            
            Probabilities:
            {json.dumps(validated_context.get('probabilities', {}), indent=2)}
            
            Sentiment:
            {validated_context.get('sentiment', 'Neutral')}
            
            Patterns (if available):
            {json.dumps(validated_context.get('patterns', {}).get('statistics', {}), indent=2) if validated_context.get('patterns') else 'None'}
            
            INSTRUCTIONS:
            - Give a brief, precise answer based on the data
            - Use actual values from the analysis
            - Be honest if the data doesn't allow a clear answer
            - Format prices as $X,XXX.XX
            """
            else:
                prompt = f"""
            Beantworte diese Frage basierend auf der technischen Analyse:
            
            FRAGE: {question}
            
            KONTEXT DER ANALYSE:
            
            Indikatoren:
            {json.dumps(validated_indicators, indent=2, default=str)[:1000]}
            
            Wahrscheinlichkeiten:
            {json.dumps(validated_context.get('probabilities', {}), indent=2)}
            
            Sentiment:
            {validated_context.get('sentiment', 'Neutral')}
            
            Patterns (falls vorhanden):
            {json.dumps(validated_context.get('patterns', {}).get('statistics', {}), indent=2) if validated_context.get('patterns') else 'Keine'}
            
            ANWEISUNGEN:
            - Gib eine kurze, präzise Antwort basierend auf den Daten
            - Verwende die tatsächlichen Werte aus der Analyse
            - Sei ehrlich wenn die Daten keine klare Antwort erlauben
            - Formatiere Preise als $X,XXX.XX
            """
            
            messages = [
                {"role": "system", "content": "You are a helpful trading assistant. Answer questions based on the technical data." if language == 'en' else "Du bist ein hilfreicher Trading-Assistent. Beantworte Fragen basierend auf den technischen Daten."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_request(messages, temperature=0.5, max_tokens=max_tokens or 800)
            
        except Exception as e:
            return f"Fehler bei der Antwort: {str(e)}"
