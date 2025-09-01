"""
Candlestick Pattern Recognition Module
Erkennt klassische Candlestick-Muster in Kursdaten
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional

class CandlestickPatterns:
    """
    Klasse zur Erkennung von Candlestick-Mustern
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialisiert den Pattern Detector
        
        Args:
            data: DataFrame mit OHLC Daten
        """
        self.data = data
        self.patterns = []
        
    def detect_all_patterns(self) -> List[Dict]:
        """
        Erkennt alle implementierten Candlestick-Muster
        """
        self.patterns = []
        
        # Single Candle Patterns
        self._detect_doji()
        self._detect_hammer()
        self._detect_hanging_man()
        self._detect_shooting_star()
        self._detect_inverted_hammer()
        self._detect_spinning_top()
        self._detect_marubozu()
        self._detect_long_legged_doji()
        self._detect_dragonfly_doji()
        self._detect_gravestone_doji()
        
        # Two Candle Patterns
        self._detect_engulfing()
        self._detect_harami()
        self._detect_piercing_line()
        self._detect_dark_cloud_cover()
        self._detect_tweezer_tops_bottoms()
        
        # Three Candle Patterns
        self._detect_morning_star()
        self._detect_evening_star()
        self._detect_three_white_soldiers()
        self._detect_three_black_crows()
        self._detect_three_inside_up_down()
        self._detect_three_outside_up_down()
        
        # Multi-Candle Patterns
        self._detect_rising_falling_three_methods()
        
        return self.patterns
    
    def _calculate_body_height(self, idx: int) -> float:
        """Berechnet die Höhe des Kerzenkörpers"""
        return abs(self.data['Close'].iloc[idx] - self.data['Open'].iloc[idx])
    
    def _calculate_upper_shadow(self, idx: int) -> float:
        """Berechnet den oberen Schatten"""
        return self.data['High'].iloc[idx] - max(self.data['Close'].iloc[idx], self.data['Open'].iloc[idx])
    
    def _calculate_lower_shadow(self, idx: int) -> float:
        """Berechnet den unteren Schatten"""
        return min(self.data['Close'].iloc[idx], self.data['Open'].iloc[idx]) - self.data['Low'].iloc[idx]
    
    def _is_bullish_candle(self, idx: int) -> bool:
        """Prüft ob die Kerze bullisch ist"""
        return self.data['Close'].iloc[idx] > self.data['Open'].iloc[idx]
    
    def _is_bearish_candle(self, idx: int) -> bool:
        """Prüft ob die Kerze bearisch ist"""
        return self.data['Close'].iloc[idx] < self.data['Open'].iloc[idx]
    
    def _get_trend(self, idx: int, lookback: int = 5) -> str:
        """Bestimmt den vorherigen Trend"""
        if idx < lookback:
            return "unknown"
        
        start_price = self.data['Close'].iloc[idx - lookback]
        end_price = self.data['Close'].iloc[idx - 1]
        
        if end_price > start_price * 1.02:
            return "uptrend"
        elif end_price < start_price * 0.98:
            return "downtrend"
        else:
            return "sideways"
    
    def _add_pattern(self, idx: int, name: str, signal: str, reliability: str, description: str):
        """Fügt ein erkanntes Muster zur Liste hinzu"""
        self.patterns.append({
            'date': self.data.index[idx],
            'pattern': name,
            'signal': signal,
            'reliability': reliability,
            'description': description,
            'price': self.data['Close'].iloc[idx],
            'index': idx
        })
    
    # Single Candle Patterns
    
    def _detect_doji(self):
        """Erkennt Doji Muster"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if high_low > 0 and body / high_low < 0.1:
                trend = self._get_trend(i)
                if trend == "uptrend":
                    signal = "Bearish Reversal"
                elif trend == "downtrend":
                    signal = "Bullish Reversal"
                else:
                    signal = "Indecision"
                
                self._add_pattern(i, "Doji", signal, "Medium", 
                                "Unentschlossenheit im Markt, mögliche Trendwende")
    
    def _detect_hammer(self):
        """Erkennt Hammer Muster"""
        for i in range(1, len(self.data)):
            body = self._calculate_body_height(i)
            lower_shadow = self._calculate_lower_shadow(i)
            upper_shadow = self._calculate_upper_shadow(i)
            
            if (lower_shadow > body * 2 and 
                upper_shadow < body * 0.3 and
                self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Hammer", "Bullish Reversal", "High",
                                "Starkes bullisches Umkehrsignal nach Abwärtstrend")
    
    def _detect_hanging_man(self):
        """Erkennt Hanging Man Muster"""
        for i in range(1, len(self.data)):
            body = self._calculate_body_height(i)
            lower_shadow = self._calculate_lower_shadow(i)
            upper_shadow = self._calculate_upper_shadow(i)
            
            if (lower_shadow > body * 2 and 
                upper_shadow < body * 0.3 and
                self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Hanging Man", "Bearish Reversal", "Medium",
                                "Mögliches bearisches Umkehrsignal nach Aufwärtstrend")
    
    def _detect_shooting_star(self):
        """Erkennt Shooting Star Muster"""
        for i in range(1, len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            
            if (upper_shadow > body * 2 and 
                lower_shadow < body * 0.3 and
                self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Shooting Star", "Bearish Reversal", "High",
                                "Starkes bearisches Umkehrsignal nach Aufwärtstrend")
    
    def _detect_inverted_hammer(self):
        """Erkennt Inverted Hammer Muster"""
        for i in range(1, len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            
            if (upper_shadow > body * 2 and 
                lower_shadow < body * 0.3 and
                self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Inverted Hammer", "Bullish Reversal", "Medium",
                                "Mögliches bullisches Umkehrsignal nach Abwärtstrend")
    
    def _detect_spinning_top(self):
        """Erkennt Spinning Top Muster"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if (high_low > 0 and 
                body / high_low < 0.3 and
                upper_shadow > body and 
                lower_shadow > body):
                
                self._add_pattern(i, "Spinning Top", "Neutral", "Low",
                                "Unentschlossenheit, mögliche Konsolidierung")
    
    def _detect_marubozu(self):
        """Erkennt Marubozu Muster"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if high_low > 0 and body / high_low > 0.95:
                if self._is_bullish_candle(i):
                    self._add_pattern(i, "Bullish Marubozu", "Strong Bullish", "High",
                                    "Sehr starkes bullisches Signal, Käufer kontrollieren")
                else:
                    self._add_pattern(i, "Bearish Marubozu", "Strong Bearish", "High",
                                    "Sehr starkes bearisches Signal, Verkäufer kontrollieren")
    
    def _detect_long_legged_doji(self):
        """Erkennt Long-Legged Doji"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if (high_low > 0 and 
                body / high_low < 0.05 and
                upper_shadow > body * 5 and 
                lower_shadow > body * 5):
                
                self._add_pattern(i, "Long-Legged Doji", "High Indecision", "Medium",
                                "Extreme Unentschlossenheit, wichtiger Wendepunkt möglich")
    
    def _detect_dragonfly_doji(self):
        """Erkennt Dragonfly Doji"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if (high_low > 0 and 
                body / high_low < 0.05 and
                lower_shadow > high_low * 0.7 and
                upper_shadow < high_low * 0.1):
                
                trend = self._get_trend(i)
                if trend == "downtrend":
                    self._add_pattern(i, "Dragonfly Doji", "Bullish Reversal", "High",
                                    "Starkes bullisches Umkehrsignal am Boden")
                else:
                    self._add_pattern(i, "Dragonfly Doji", "Support Found", "Medium",
                                    "Unterstützung gefunden")
    
    def _detect_gravestone_doji(self):
        """Erkennt Gravestone Doji"""
        for i in range(len(self.data)):
            body = self._calculate_body_height(i)
            upper_shadow = self._calculate_upper_shadow(i)
            lower_shadow = self._calculate_lower_shadow(i)
            high_low = self.data['High'].iloc[i] - self.data['Low'].iloc[i]
            
            if (high_low > 0 and 
                body / high_low < 0.05 and
                upper_shadow > high_low * 0.7 and
                lower_shadow < high_low * 0.1):
                
                trend = self._get_trend(i)
                if trend == "uptrend":
                    self._add_pattern(i, "Gravestone Doji", "Bearish Reversal", "High",
                                    "Starkes bearisches Umkehrsignal am Top")
                else:
                    self._add_pattern(i, "Gravestone Doji", "Resistance Found", "Medium",
                                    "Widerstand gefunden")
    
    # Two Candle Patterns
    
    def _detect_engulfing(self):
        """Erkennt Bullish und Bearish Engulfing Patterns"""
        for i in range(1, len(self.data)):
            prev_body = self._calculate_body_height(i-1)
            curr_body = self._calculate_body_height(i)
            
            # Bullish Engulfing
            if (self._is_bearish_candle(i-1) and 
                self._is_bullish_candle(i) and
                self.data['Open'].iloc[i] < self.data['Close'].iloc[i-1] and
                self.data['Close'].iloc[i] > self.data['Open'].iloc[i-1] and
                self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Bullish Engulfing", "Bullish Reversal", "High",
                                "Starkes bullisches Umkehrmuster")
            
            # Bearish Engulfing
            elif (self._is_bullish_candle(i-1) and 
                  self._is_bearish_candle(i) and
                  self.data['Open'].iloc[i] > self.data['Close'].iloc[i-1] and
                  self.data['Close'].iloc[i] < self.data['Open'].iloc[i-1] and
                  self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Bearish Engulfing", "Bearish Reversal", "High",
                                "Starkes bearisches Umkehrmuster")
    
    def _detect_harami(self):
        """Erkennt Bullish und Bearish Harami Patterns"""
        for i in range(1, len(self.data)):
            # Bullish Harami
            if (self._is_bearish_candle(i-1) and 
                self._is_bullish_candle(i) and
                self.data['Open'].iloc[i] > self.data['Close'].iloc[i-1] and
                self.data['Close'].iloc[i] < self.data['Open'].iloc[i-1] and
                self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Bullish Harami", "Bullish Reversal", "Medium",
                                "Mögliche bullische Umkehr")
            
            # Bearish Harami
            elif (self._is_bullish_candle(i-1) and 
                  self._is_bearish_candle(i) and
                  self.data['Open'].iloc[i] < self.data['Close'].iloc[i-1] and
                  self.data['Close'].iloc[i] > self.data['Open'].iloc[i-1] and
                  self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Bearish Harami", "Bearish Reversal", "Medium",
                                "Mögliche bearische Umkehr")
    
    def _detect_piercing_line(self):
        """Erkennt Piercing Line Pattern"""
        for i in range(1, len(self.data)):
            if (self._is_bearish_candle(i-1) and 
                self._is_bullish_candle(i) and
                self.data['Open'].iloc[i] < self.data['Low'].iloc[i-1] and
                self.data['Close'].iloc[i] > (self.data['Open'].iloc[i-1] + self.data['Close'].iloc[i-1]) / 2 and
                self.data['Close'].iloc[i] < self.data['Open'].iloc[i-1] and
                self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Piercing Line", "Bullish Reversal", "High",
                                "Starkes bullisches Umkehrsignal")
    
    def _detect_dark_cloud_cover(self):
        """Erkennt Dark Cloud Cover Pattern"""
        for i in range(1, len(self.data)):
            if (self._is_bullish_candle(i-1) and 
                self._is_bearish_candle(i) and
                self.data['Open'].iloc[i] > self.data['High'].iloc[i-1] and
                self.data['Close'].iloc[i] < (self.data['Open'].iloc[i-1] + self.data['Close'].iloc[i-1]) / 2 and
                self.data['Close'].iloc[i] > self.data['Open'].iloc[i-1] and
                self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Dark Cloud Cover", "Bearish Reversal", "High",
                                "Starkes bearisches Umkehrsignal")
    
    def _detect_tweezer_tops_bottoms(self):
        """Erkennt Tweezer Tops und Bottoms"""
        for i in range(1, len(self.data)):
            # Tweezer Top
            if (abs(self.data['High'].iloc[i] - self.data['High'].iloc[i-1]) < self.data['High'].iloc[i] * 0.001 and
                self._get_trend(i) == "uptrend"):
                
                self._add_pattern(i, "Tweezer Top", "Bearish Reversal", "Medium",
                                "Doppelter Widerstand, mögliche Umkehr")
            
            # Tweezer Bottom
            elif (abs(self.data['Low'].iloc[i] - self.data['Low'].iloc[i-1]) < self.data['Low'].iloc[i] * 0.001 and
                  self._get_trend(i) == "downtrend"):
                
                self._add_pattern(i, "Tweezer Bottom", "Bullish Reversal", "Medium",
                                "Doppelte Unterstützung, mögliche Umkehr")
    
    # Three Candle Patterns
    
    def _detect_morning_star(self):
        """Erkennt Morning Star Pattern"""
        for i in range(2, len(self.data)):
            if (self._is_bearish_candle(i-2) and
                self._calculate_body_height(i-1) < self._calculate_body_height(i-2) * 0.3 and
                self._is_bullish_candle(i) and
                self.data['Close'].iloc[i] > (self.data['Open'].iloc[i-2] + self.data['Close'].iloc[i-2]) / 2 and
                self._get_trend(i-2) == "downtrend"):
                
                self._add_pattern(i, "Morning Star", "Bullish Reversal", "Very High",
                                "Sehr starkes bullisches Umkehrmuster")
    
    def _detect_evening_star(self):
        """Erkennt Evening Star Pattern"""
        for i in range(2, len(self.data)):
            if (self._is_bullish_candle(i-2) and
                self._calculate_body_height(i-1) < self._calculate_body_height(i-2) * 0.3 and
                self._is_bearish_candle(i) and
                self.data['Close'].iloc[i] < (self.data['Open'].iloc[i-2] + self.data['Close'].iloc[i-2]) / 2 and
                self._get_trend(i-2) == "uptrend"):
                
                self._add_pattern(i, "Evening Star", "Bearish Reversal", "Very High",
                                "Sehr starkes bearisches Umkehrmuster")
    
    def _detect_three_white_soldiers(self):
        """Erkennt Three White Soldiers Pattern"""
        for i in range(2, len(self.data)):
            if (self._is_bullish_candle(i-2) and
                self._is_bullish_candle(i-1) and
                self._is_bullish_candle(i) and
                self.data['Close'].iloc[i-1] > self.data['Close'].iloc[i-2] and
                self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1] and
                self.data['Open'].iloc[i-1] > self.data['Open'].iloc[i-2] and
                self.data['Open'].iloc[i] > self.data['Open'].iloc[i-1]):
                
                self._add_pattern(i, "Three White Soldiers", "Strong Bullish", "Very High",
                                "Sehr starker Aufwärtstrend")
    
    def _detect_three_black_crows(self):
        """Erkennt Three Black Crows Pattern"""
        for i in range(2, len(self.data)):
            if (self._is_bearish_candle(i-2) and
                self._is_bearish_candle(i-1) and
                self._is_bearish_candle(i) and
                self.data['Close'].iloc[i-1] < self.data['Close'].iloc[i-2] and
                self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1] and
                self.data['Open'].iloc[i-1] < self.data['Open'].iloc[i-2] and
                self.data['Open'].iloc[i] < self.data['Open'].iloc[i-1]):
                
                self._add_pattern(i, "Three Black Crows", "Strong Bearish", "Very High",
                                "Sehr starker Abwärtstrend")
    
    def _detect_three_inside_up_down(self):
        """Erkennt Three Inside Up/Down Patterns"""
        for i in range(2, len(self.data)):
            # Three Inside Up (Bullish)
            if (self._is_bearish_candle(i-2) and
                self._is_bullish_candle(i-1) and
                self.data['Close'].iloc[i-1] < self.data['Open'].iloc[i-2] and
                self.data['Open'].iloc[i-1] > self.data['Close'].iloc[i-2] and
                self._is_bullish_candle(i) and
                self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1]):
                
                self._add_pattern(i, "Three Inside Up", "Bullish Reversal", "High",
                                "Bestätigte bullische Umkehr")
            
            # Three Inside Down (Bearish)
            elif (self._is_bullish_candle(i-2) and
                  self._is_bearish_candle(i-1) and
                  self.data['Close'].iloc[i-1] > self.data['Open'].iloc[i-2] and
                  self.data['Open'].iloc[i-1] < self.data['Close'].iloc[i-2] and
                  self._is_bearish_candle(i) and
                  self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1]):
                
                self._add_pattern(i, "Three Inside Down", "Bearish Reversal", "High",
                                "Bestätigte bearische Umkehr")
    
    def _detect_three_outside_up_down(self):
        """Erkennt Three Outside Up/Down Patterns"""
        for i in range(2, len(self.data)):
            # Three Outside Up (Bullish)
            if (self._is_bearish_candle(i-2) and
                self._is_bullish_candle(i-1) and
                self.data['Open'].iloc[i-1] < self.data['Close'].iloc[i-2] and
                self.data['Close'].iloc[i-1] > self.data['Open'].iloc[i-2] and
                self._is_bullish_candle(i) and
                self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1]):
                
                self._add_pattern(i, "Three Outside Up", "Bullish Reversal", "High",
                                "Starke bullische Umkehr mit Engulfing")
            
            # Three Outside Down (Bearish)
            elif (self._is_bullish_candle(i-2) and
                  self._is_bearish_candle(i-1) and
                  self.data['Open'].iloc[i-1] > self.data['Close'].iloc[i-2] and
                  self.data['Close'].iloc[i-1] < self.data['Open'].iloc[i-2] and
                  self._is_bearish_candle(i) and
                  self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1]):
                
                self._add_pattern(i, "Three Outside Down", "Bearish Reversal", "High",
                                "Starke bearische Umkehr mit Engulfing")
    
    def _detect_rising_falling_three_methods(self):
        """Erkennt Rising und Falling Three Methods"""
        for i in range(4, len(self.data)):
            # Rising Three Methods (Continuation)
            if (self._is_bullish_candle(i-4) and
                self._calculate_body_height(i-4) > self._calculate_body_height(i-3) and
                self._calculate_body_height(i-4) > self._calculate_body_height(i-2) and
                self._calculate_body_height(i-4) > self._calculate_body_height(i-1) and
                all(self.data['Close'].iloc[j] < self.data['High'].iloc[i-4] and 
                    self.data['Close'].iloc[j] > self.data['Low'].iloc[i-4] 
                    for j in range(i-3, i)) and
                self._is_bullish_candle(i) and
                self.data['Close'].iloc[i] > self.data['Close'].iloc[i-4]):
                
                self._add_pattern(i, "Rising Three Methods", "Bullish Continuation", "High",
                                "Bullischer Trend setzt sich fort")
            
            # Falling Three Methods (Continuation)
            elif (self._is_bearish_candle(i-4) and
                  self._calculate_body_height(i-4) > self._calculate_body_height(i-3) and
                  self._calculate_body_height(i-4) > self._calculate_body_height(i-2) and
                  self._calculate_body_height(i-4) > self._calculate_body_height(i-1) and
                  all(self.data['Close'].iloc[j] > self.data['Low'].iloc[i-4] and 
                      self.data['Close'].iloc[j] < self.data['High'].iloc[i-4] 
                      for j in range(i-3, i)) and
                  self._is_bearish_candle(i) and
                  self.data['Close'].iloc[i] < self.data['Close'].iloc[i-4]):
                
                self._add_pattern(i, "Falling Three Methods", "Bearish Continuation", "High",
                                "Bearischer Trend setzt sich fort")
    
    def get_pattern_statistics(self) -> Dict:
        """
        Gibt Statistiken über die erkannten Muster zurück
        """
        if not self.patterns:
            return {}
        
        stats = {
            'total_patterns': len(self.patterns),
            'bullish_patterns': len([p for p in self.patterns if 'Bullish' in p['signal']]),
            'bearish_patterns': len([p for p in self.patterns if 'Bearish' in p['signal']]),
            'neutral_patterns': len([p for p in self.patterns if 'Neutral' in p['signal'] or 'Continuation' in p['signal']]),
            'high_reliability': len([p for p in self.patterns if p['reliability'] in ['High', 'Very High']]),
            'recent_patterns': [p for p in self.patterns[-5:]],  # Letzte 5 Muster
            'pattern_types': {}
        }
        
        # Zähle Pattern-Typen
        for pattern in self.patterns:
            pattern_name = pattern['pattern']
            if pattern_name not in stats['pattern_types']:
                stats['pattern_types'][pattern_name] = 0
            stats['pattern_types'][pattern_name] += 1
        
        return stats