"""
Technische Analyse-Funktionen für den Index Analyser
"""

import pandas as pd
import numpy as np
import ta
# from ta import add_all_ta_features  # Deaktiviert wegen Performance
from ta.utils import dropna
from scipy import stats
from sklearn.linear_model import LinearRegression
import yfinance as yf
from datetime import datetime, timedelta
from config import *
import warnings

class TechnicalAnalysis:
    def __init__(self, ticker_symbol, period="1y", interval="1d", start_date=None, end_date=None):
        """
        Initialisiert die technische Analyse für einen Index
        """
        self.ticker_symbol = ticker_symbol
        self.period = period
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.indicators = {}
        self.fibonacci_levels = {}
        self.support_resistance = {}
        
    def fetch_data(self):
        """
        Lädt Daten von yfinance
        """
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            
            # Verwende Start- und Enddatum wenn verfügbar
            if self.start_date and self.end_date:
                self.data = ticker.history(start=self.start_date, end=self.end_date, interval=self.interval)
            else:
                # Fallback auf period wenn keine Datumswerte angegeben
                self.data = ticker.history(period=self.period, interval=self.interval)
                
            if self.data.empty:
                raise ValueError(f"Keine Daten für {self.ticker_symbol} gefunden")
            return True
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")
            return False
    
    def calculate_all_indicators(self, include_vwap=False):
        """
        Berechnet alle technischen Indikatoren (optimiert)
        """
        if self.data is None or self.data.empty:
            return None
            
        # Erstelle eine Kopie für die Berechnungen
        df = self.data.copy()
        
        # Unterdrücke Warnungen während der Berechnung
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Grundlegende Indikatoren
            self._calculate_moving_averages(df)
            self._calculate_rsi(df)
            self._calculate_macd(df)
            self._calculate_bollinger_bands(df)
            self._calculate_stochastic(df)
            self._calculate_adx(df)
            self._calculate_atr(df)
            self._calculate_cci(df)
            self._calculate_obv(df)
            
            # VWAP nur berechnen wenn explizit angefordert
            if include_vwap:
                self._calculate_vwap(df)
            
            self._calculate_williams_r(df)
            self._calculate_mfi(df)
            self._calculate_cmf(df)
            self._calculate_roc(df)
            self._calculate_pivots(df)
            
            # Erweiterte Indikatoren mit ta library - nur wenn nötig
            # Deaktiviert wegen Performance-Problemen
            # try:
            #     df = add_all_ta_features(
            #         df, open="Open", high="High", low="Low", close="Close", volume="Volume"
            #     )
            # except:
            #     pass
        
        self.data = df
        return df
    
    def _calculate_moving_averages(self, df):
        """Berechnet Simple und Exponential Moving Averages"""
        for period in INDICATOR_PARAMS["sma_periods"]:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
            
        for period in INDICATOR_PARAMS["ema_periods"]:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
            
        self.indicators['moving_averages'] = {
            'sma': {p: df[f'SMA_{p}'].iloc[-1] for p in INDICATOR_PARAMS["sma_periods"] if f'SMA_{p}' in df},
            'ema': {p: df[f'EMA_{p}'].iloc[-1] for p in INDICATOR_PARAMS["ema_periods"] if f'EMA_{p}' in df}
        }
    
    def _calculate_rsi(self, df):
        """Berechnet den Relative Strength Index"""
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=INDICATOR_PARAMS["rsi_period"]).rsi()
        self.indicators['RSI'] = df['RSI'].iloc[-1] if 'RSI' in df else None
    
    def _calculate_macd(self, df):
        """Berechnet MACD"""
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        
        self.indicators['MACD'] = {
            'macd': df['MACD'].iloc[-1] if 'MACD' in df else None,
            'signal': df['MACD_signal'].iloc[-1] if 'MACD_signal' in df else None,
            'histogram': df['MACD_diff'].iloc[-1] if 'MACD_diff' in df else None
        }
    
    def _calculate_bollinger_bands(self, df):
        """Berechnet Bollinger Bands"""
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_middle'] = bb.bollinger_mavg()
        df['BB_lower'] = bb.bollinger_lband()
        df['BB_width'] = bb.bollinger_wband()
        df['BB_percent'] = bb.bollinger_pband()
        
        self.indicators['Bollinger'] = {
            'upper': df['BB_upper'].iloc[-1] if 'BB_upper' in df else None,
            'middle': df['BB_middle'].iloc[-1] if 'BB_middle' in df else None,
            'lower': df['BB_lower'].iloc[-1] if 'BB_lower' in df else None,
            'width': df['BB_width'].iloc[-1] if 'BB_width' in df else None,
            'percent': df['BB_percent'].iloc[-1] if 'BB_percent' in df else None
        }
    
    def _calculate_stochastic(self, df):
        """Berechnet Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        self.indicators['Stochastic'] = {
            'K': df['Stoch_K'].iloc[-1] if 'Stoch_K' in df else None,
            'D': df['Stoch_D'].iloc[-1] if 'Stoch_D' in df else None
        }
    
    def _calculate_adx(self, df):
        """Berechnet Average Directional Index"""
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'])
        df['ADX'] = adx.adx()
        df['ADX_pos'] = adx.adx_pos()
        df['ADX_neg'] = adx.adx_neg()
        
        self.indicators['ADX'] = {
            'adx': df['ADX'].iloc[-1] if 'ADX' in df else None,
            'di_plus': df['ADX_pos'].iloc[-1] if 'ADX_pos' in df else None,
            'di_minus': df['ADX_neg'].iloc[-1] if 'ADX_neg' in df else None
        }
    
    def _calculate_atr(self, df):
        """Berechnet Average True Range"""
        df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        self.indicators['ATR'] = df['ATR'].iloc[-1] if 'ATR' in df else None
    
    def _calculate_cci(self, df):
        """Berechnet Commodity Channel Index"""
        df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close']).cci()
        self.indicators['CCI'] = df['CCI'].iloc[-1] if 'CCI' in df else None
    
    def _calculate_obv(self, df):
        """Berechnet On Balance Volume"""
        df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
        self.indicators['OBV'] = df['OBV'].iloc[-1] if 'OBV' in df else None
    
    def _calculate_vwap(self, df):
        """Berechnet Volume Weighted Average Price"""
        df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(
            df['High'], df['Low'], df['Close'], df['Volume']
        ).volume_weighted_average_price()
        self.indicators['VWAP'] = df['VWAP'].iloc[-1] if 'VWAP' in df else None
    
    def _calculate_williams_r(self, df):
        """Berechnet Williams %R"""
        df['Williams_R'] = ta.momentum.WilliamsRIndicator(df['High'], df['Low'], df['Close']).williams_r()
        self.indicators['Williams_R'] = df['Williams_R'].iloc[-1] if 'Williams_R' in df else None
    
    def _calculate_mfi(self, df):
        """Berechnet Money Flow Index"""
        df['MFI'] = ta.volume.MFIIndicator(df['High'], df['Low'], df['Close'], df['Volume']).money_flow_index()
        self.indicators['MFI'] = df['MFI'].iloc[-1] if 'MFI' in df else None
    
    def _calculate_cmf(self, df):
        """Berechnet Chaikin Money Flow"""
        df['CMF'] = ta.volume.ChaikinMoneyFlowIndicator(df['High'], df['Low'], df['Close'], df['Volume']).chaikin_money_flow()
        self.indicators['CMF'] = df['CMF'].iloc[-1] if 'CMF' in df else None
    
    def _calculate_roc(self, df):
        """Berechnet Rate of Change"""
        df['ROC'] = ta.momentum.ROCIndicator(df['Close']).roc()
        self.indicators['ROC'] = df['ROC'].iloc[-1] if 'ROC' in df else None
    
    def _calculate_pivots(self, df):
        """Berechnet Pivot Points"""
        last_high = df['High'].iloc[-1]
        last_low = df['Low'].iloc[-1]
        last_close = df['Close'].iloc[-1]
        
        pivot = (last_high + last_low + last_close) / 3
        r1 = 2 * pivot - last_low
        r2 = pivot + (last_high - last_low)
        r3 = last_high + 2 * (pivot - last_low)
        s1 = 2 * pivot - last_high
        s2 = pivot - (last_high - last_low)
        s3 = last_low - 2 * (last_high - pivot)
        
        self.indicators['Pivots'] = {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }
    
    def calculate_fibonacci_levels(self):
        """
        Berechnet Fibonacci Retracement und Extension Levels
        """
        if self.data is None or self.data.empty:
            return None
            
        # Finde das Hoch und Tief der letzten Periode
        high = self.data['High'].max()
        low = self.data['Low'].min()
        diff = high - low
        
        # Retracement Levels (vom Hoch aus)
        retracement_levels = {}
        for level in FIBONACCI_LEVELS:
            retracement_levels[f'{level:.1%}'] = high - (diff * level)
        
        # Extension Levels
        extension_levels = {}
        for level in [1.272, 1.414, 1.618, 2.0, 2.618]:
            extension_levels[f'{level:.1%}'] = high + (diff * (level - 1))
        
        self.fibonacci_levels = {
            'high': high,
            'low': low,
            'retracement': retracement_levels,
            'extension': extension_levels
        }
        
        return self.fibonacci_levels
    
    def identify_support_resistance(self, window=20, num_levels=5):
        """
        Identifiziert Support und Resistance Levels
        Stellt sicher, dass Support unter und Resistance über dem aktuellen Kurs liegt
        """
        if self.data is None or self.data.empty:
            return None
            
        current_price = self.data['Close'].iloc[-1]
        
        # Finde lokale Minima und Maxima
        df = self.data.copy()
        df['min'] = df['Low'].rolling(window=window, center=True).min()
        df['max'] = df['High'].rolling(window=window, center=True).max()
        
        # Support Levels (lokale Minima) - NUR unter aktuellem Kurs
        all_support = df[df['Low'] == df['min']]['Low'].unique()
        support_levels = [level for level in all_support if level < current_price]
        support_levels = sorted(support_levels)[-num_levels:] if len(support_levels) > num_levels else support_levels
        
        # Resistance Levels (lokale Maxima) - NUR über aktuellem Kurs
        all_resistance = df[df['High'] == df['max']]['High'].unique()
        resistance_levels = [level for level in all_resistance if level > current_price]
        resistance_levels = sorted(resistance_levels)[:num_levels] if len(resistance_levels) > num_levels else resistance_levels
        
        self.support_resistance = {
            'support': list(support_levels),
            'resistance': list(resistance_levels),
            'current_price': float(current_price)
        }
        
        return self.support_resistance
    
    def calculate_trend_strength(self):
        """
        Berechnet die Trendstärke basierend auf verschiedenen Indikatoren mit Begründung
        """
        if not self.indicators:
            return 0, "Keine Indikatoren verfügbar"
            
        trend_score = 0
        total_weight = 0
        reasons = []  # Sammle Begründungen
        
        # RSI Bewertung
        if self.indicators.get('RSI'):
            rsi = self.indicators['RSI']
            if rsi > 70:
                trend_score += 2  # Überkauft (bullisch kurzfristig)
                total_weight += 2
                reasons.append(f"RSI überkauft ({rsi:.1f})")
            elif rsi > 50:
                trend_score += 1  # Bullisch
                total_weight += 1
                reasons.append(f"RSI bullisch ({rsi:.1f})")
            elif rsi < 30:
                trend_score -= 2  # Überverkauft (bearisch kurzfristig)
                total_weight += 2
                reasons.append(f"RSI überverkauft ({rsi:.1f})")
            else:
                trend_score -= 1  # Bearisch
                total_weight += 1
                reasons.append(f"RSI bearisch ({rsi:.1f})")
        
        # MACD Bewertung
        if self.indicators.get('MACD'):
            macd = self.indicators['MACD']
            if macd.get('histogram') is not None:
                if macd['histogram'] > 0:
                    trend_score += 1.5
                    total_weight += 1.5
                    reasons.append(f"MACD positiv ({macd['histogram']:.4f})")
                else:
                    trend_score -= 1.5
                    total_weight += 1.5
                    reasons.append(f"MACD negativ ({macd['histogram']:.4f})")
        
        # ADX Bewertung (Trendstärke)
        if self.indicators.get('ADX'):
            adx = self.indicators['ADX']
            if adx.get('adx') and adx['adx'] > 25:
                # Starker Trend
                if adx.get('di_plus') and adx.get('di_minus'):
                    if adx['di_plus'] > adx['di_minus']:
                        trend_score += 2
                        reasons.append(f"ADX bullisch (DI+ > DI-)")
                    else:
                        trend_score -= 2
                        reasons.append(f"ADX bearisch (DI- > DI+)")
                    total_weight += 2
            elif adx.get('adx'):
                reasons.append(f"ADX schwach ({adx['adx']:.1f})")
        
        # Moving Average Bewertung (jetzt mit EMAs)
        if self.data is not None and not self.data.empty:
            current_price = self.data['Close'].iloc[-1]
            ma_score = 0
            ma_weight = 0
            ma_above = 0
            ma_below = 0
            
            # Verwende EMA statt SMA
            for period in [9, 21, 50, 200]:
                ma_col = f'EMA_{period}'
                if ma_col in self.data.columns:
                    ma_value = self.data[ma_col].iloc[-1]
                    if pd.notna(ma_value):
                        if current_price > ma_value:
                            ma_score += 1
                            ma_above += 1
                        else:
                            ma_score -= 1
                            ma_below += 1
                        ma_weight += 1
            
            if ma_weight > 0:
                trend_score += ma_score
                total_weight += ma_weight
                reasons.append(f"EMAs: {ma_above}↑/{ma_below}↓")
        
        # Bollinger Bands Position
        if self.indicators.get('Bollinger'):
            bb = self.indicators['Bollinger']
            if bb.get('percent') is not None:
                if bb['percent'] > 0.8:
                    trend_score -= 0.5  # Oben am Band, mögliche Umkehr
                    reasons.append("BB oben (Umkehr?)")
                elif bb['percent'] < 0.2:
                    trend_score += 0.5  # Unten am Band, mögliche Umkehr
                    reasons.append("BB unten (Umkehr?)")
                total_weight += 0.5
        
        # Volumen-Trend
        if self.indicators.get('OBV') and self.data is not None and 'OBV' in self.data.columns:
            obv_current = self.data['OBV'].iloc[-1]
            obv_prev = self.data['OBV'].iloc[-5] if len(self.data) > 5 else obv_current
            if obv_current > obv_prev * 1.02:
                trend_score += 1
                reasons.append("OBV steigend")
            elif obv_current < obv_prev * 0.98:
                trend_score -= 1
                reasons.append("OBV fallend")
            total_weight += 1
        
        # Normalisierung auf Skala von -100 bis +100
        if total_weight > 0:
            normalized_score = (trend_score / total_weight) * 50
            final_score = min(100, max(-100, normalized_score))
        else:
            final_score = 0
        
        # Erstelle finale Begründung
        reasoning = ", ".join(reasons[:4]) if reasons else "Keine klaren Signale"  # Zeige max 4 Hauptgründe
        
        return final_score, reasoning
    
    def calculate_probabilities(self):
        """
        Berechnet Wahrscheinlichkeiten für bullische, bearische und neutrale Szenarien
        """
        if self.data is None or self.data.empty or not self.indicators:
            return None
            
        bullish_signals = 0
        bearish_signals = 0
        neutral_signals = 0
        total_signals = 0
        
        # RSI Signale
        if self.indicators.get('RSI'):
            rsi = self.indicators['RSI']
            if rsi > 60:
                bullish_signals += 1
            elif rsi < 40:
                bearish_signals += 1
            else:
                neutral_signals += 1
            total_signals += 1
        
        # MACD Signale
        if self.indicators.get('MACD'):
            macd = self.indicators['MACD']
            if macd['histogram']:
                if abs(macd['histogram']) < 0.001:  # Sehr kleiner Wert = neutral
                    neutral_signals += 1
                elif macd['histogram'] > 0:
                    bullish_signals += 1
                else:
                    bearish_signals += 1
            total_signals += 1
        
        # Stochastic Signale
        if self.indicators.get('Stochastic'):
            stoch = self.indicators['Stochastic']
            if stoch['K']:
                if stoch['K'] > 70:
                    bullish_signals += 1
                elif stoch['K'] < 30:
                    bearish_signals += 1
                else:
                    neutral_signals += 1
            total_signals += 1
        
        # Bollinger Bands Position
        if self.indicators.get('Bollinger'):
            bb = self.indicators['Bollinger']
            if bb['percent']:
                if bb['percent'] > 0.8:
                    bullish_signals += 1
                elif bb['percent'] < 0.2:
                    bearish_signals += 1
                else:
                    neutral_signals += 1
            total_signals += 1
        
        # MFI Signale
        if self.indicators.get('MFI'):
            mfi = self.indicators['MFI']
            if mfi > 60:
                bullish_signals += 1
            elif mfi < 40:
                bearish_signals += 1
            else:
                neutral_signals += 1
            total_signals += 1
        
        # Moving Average Trend (mit EMAs)
        if self.data is not None and not self.data.empty:
            current_price = self.data['Close'].iloc[-1]
            
            # Prüfe ob Preis über wichtigen EMAs liegt
            for ma in ['EMA_50', 'EMA_200']:
                if ma in self.data.columns:
                    ma_value = self.data[ma].iloc[-1]
                    if pd.notna(ma_value):
                        diff_percent = ((current_price - ma_value) / ma_value) * 100
                        if diff_percent > 1:  # Mehr als 1% über MA
                            bullish_signals += 1
                        elif diff_percent < -1:  # Mehr als 1% unter MA
                            bearish_signals += 1
                        else:
                            neutral_signals += 1
                        total_signals += 1
        
        # Volumen Trend (OBV)
        if 'OBV' in self.data.columns:
            obv_current = self.data['OBV'].iloc[-1]
            obv_avg = self.data['OBV'].iloc[-20:].mean()
            obv_diff = ((obv_current - obv_avg) / obv_avg) * 100 if obv_avg != 0 else 0
            
            if obv_diff > 5:
                bullish_signals += 1
            elif obv_diff < -5:
                bearish_signals += 1
            else:
                neutral_signals += 1
            total_signals += 1
        
        # ADX für Trendstärke (neutral wenn kein klarer Trend)
        if self.indicators.get('ADX'):
            adx = self.indicators['ADX']
            if adx.get('adx') and adx['adx'] < 20:
                neutral_signals += 2  # Doppelte Gewichtung für klare Seitwärtsphasen
                total_signals += 2
        
        if total_signals > 0:
            # Berechne Prozentsätze
            bullish_prob = (bullish_signals / total_signals) * 100
            bearish_prob = (bearish_signals / total_signals) * 100
            neutral_prob = (neutral_signals / total_signals) * 100
            
            # Normalisiere auf 100%
            total_prob = bullish_prob + bearish_prob + neutral_prob
            if total_prob != 100:
                bullish_prob = (bullish_prob / total_prob) * 100
                bearish_prob = (bearish_prob / total_prob) * 100
                neutral_prob = (neutral_prob / total_prob) * 100
        else:
            bullish_prob = 33.33
            bearish_prob = 33.33
            neutral_prob = 33.34
        
        return {
            'bullish_probability': round(bullish_prob, 2),
            'bearish_probability': round(bearish_prob, 2),
            'neutral_probability': round(neutral_prob, 2),
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'neutral_signals': neutral_signals,
            'total_signals': total_signals
        }
    
    def calculate_price_targets(self):
        """
        Berechnet mögliche Kursziele basierend auf technischer Analyse
        """
        if self.data is None or self.data.empty:
            return None
            
        current_price = self.data['Close'].iloc[-1]
        targets = {'bullish': [], 'bearish': []}
        
        # Fibonacci basierte Ziele
        if self.fibonacci_levels:
            fib_retracement = self.fibonacci_levels['retracement']
            fib_extension = self.fibonacci_levels['extension']
            
            # Bullische Ziele (über aktuellem Kurs)
            for level, price in fib_retracement.items():
                if price > current_price:
                    targets['bullish'].append({
                        'level': f'Fib Retracement {level}',
                        'price': round(price, 2),
                        'distance': round(((price - current_price) / current_price) * 100, 2)
                    })
            
            for level, price in fib_extension.items():
                if price > current_price:
                    targets['bullish'].append({
                        'level': f'Fib Extension {level}',
                        'price': round(price, 2),
                        'distance': round(((price - current_price) / current_price) * 100, 2)
                    })
            
            # Bearische Ziele (unter aktuellem Kurs)
            for level, price in fib_retracement.items():
                if price < current_price:
                    targets['bearish'].append({
                        'level': f'Fib Retracement {level}',
                        'price': round(price, 2),
                        'distance': round(((price - current_price) / current_price) * 100, 2)
                    })
        
        # Pivot basierte Ziele
        if self.indicators.get('Pivots'):
            pivots = self.indicators['Pivots']
            
            # Resistance Levels als bullische Ziele
            for i in range(1, 4):
                r_level = pivots.get(f'r{i}')
                if r_level and r_level > current_price:
                    targets['bullish'].append({
                        'level': f'Resistance R{i}',
                        'price': round(r_level, 2),
                        'distance': round(((r_level - current_price) / current_price) * 100, 2)
                    })
            
            # Support Levels als bearische Ziele
            for i in range(1, 4):
                s_level = pivots.get(f's{i}')
                if s_level and s_level < current_price:
                    targets['bearish'].append({
                        'level': f'Support S{i}',
                        'price': round(s_level, 2),
                        'distance': round(((s_level - current_price) / current_price) * 100, 2)
                    })
        
        # Support/Resistance basierte Ziele
        if self.support_resistance:
            for resistance in self.support_resistance.get('resistance', []):
                if resistance > current_price:
                    targets['bullish'].append({
                        'level': 'Key Resistance',
                        'price': round(resistance, 2),
                        'distance': round(((resistance - current_price) / current_price) * 100, 2)
                    })
            
            for support in self.support_resistance.get('support', []):
                if support < current_price:
                    targets['bearish'].append({
                        'level': 'Key Support',
                        'price': round(support, 2),
                        'distance': round(((support - current_price) / current_price) * 100, 2)
                    })
        
        # Sortiere Ziele nach Entfernung
        targets['bullish'] = sorted(targets['bullish'], key=lambda x: x['distance'])[:5]
        targets['bearish'] = sorted(targets['bearish'], key=lambda x: abs(x['distance']))[:5]
        
        return targets
    
    def get_market_sentiment(self):
        """
        Bestimmt die Marktstimmung basierend auf allen Indikatoren mit Begründung
        """
        trend_strength, reasoning = self.calculate_trend_strength()
        
        # Zusätzlich die Signal-Verteilung berücksichtigen
        probabilities = self.calculate_probabilities()
        if probabilities:
            bullish_signals = probabilities.get('bullish_signals', 0)
            bearish_signals = probabilities.get('bearish_signals', 0)
            neutral_signals = probabilities.get('neutral_signals', 0)
            total_signals = probabilities.get('total_signals', 0)
            
            # Justiere Sentiment basierend auf Signal-Verteilung
            if total_signals > 0:
                signal_bias = (bullish_signals - bearish_signals) / total_signals * 20
                trend_strength += signal_bias
                
                # Füge Signal-Info zur Begründung hinzu
                signal_info = f"Signale: {bullish_signals}↑/{neutral_signals}→/{bearish_signals}↓"
                reasoning = f"{reasoning} | {signal_info}"
        
        # Bestimme finales Sentiment mit angepassten Schwellenwerten
        # Berücksichtige auch die Signal-Verteilung für die Begründung
        if neutral_signals > total_signals * 0.6 and abs(trend_strength) < 15:
            # Viele neutrale Signale und schwacher Trend = Neutral
            sentiment = "Neutral ➡️"
            main_reason = "Hohe Neutralität, Konsolidierung"
        elif trend_strength >= 25:
            sentiment = "Sehr Bullisch 🚀"
            main_reason = "Starke Aufwärtssignale"
        elif trend_strength >= 10:
            sentiment = "Bullisch 📈"
            main_reason = "Positive Tendenz"
        elif trend_strength >= -10:
            sentiment = "Neutral ➡️"
            main_reason = "Ausgeglichener Markt"
        elif trend_strength >= -25:
            sentiment = "Bearisch 📉"
            main_reason = "Negative Tendenz"
        else:
            sentiment = "Sehr Bearisch 🔻"
            main_reason = "Starke Abwärtssignale"
        
        # Kombiniere Hauptgrund mit detaillierter Begründung
        full_reasoning = f"{main_reason}: {reasoning}"
        
        return sentiment, trend_strength, full_reasoning
    
    def get_market_sentiment_simple(self):
        """
        Kompatibilitäts-Methode für alten Code (gibt nur 2 Werte zurück)
        """
        result = self.get_market_sentiment()
        if len(result) == 3:
            return result[0], result[1]  # Sentiment und Stärke
        return result