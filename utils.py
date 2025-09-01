"""
Erweiterte Utility-Funktionen für zusätzliche Analysen
"""

import numpy as np
import pandas as pd
from scipy import signal
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import yfinance as yf
from datetime import datetime, timedelta

class AdvancedAnalysis:
    """
    Erweiterte Analysefunktionen für professionelle Trader
    """
    
    @staticmethod
    def calculate_market_breadth(tickers, period="1mo"):
        """
        Berechnet die Marktbreite basierend auf mehreren Indizes
        """
        advancing = 0
        declining = 0
        
        for ticker in tickers:
            try:
                data = yf.Ticker(ticker).history(period=period)
                if not data.empty:
                    change = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
                    if change > 0:
                        advancing += 1
                    else:
                        declining += 1
            except:
                continue
        
        if advancing + declining > 0:
            breadth = advancing / (advancing + declining) * 100
        else:
            breadth = 50
            
        return {
            'breadth_percentage': breadth,
            'advancing': advancing,
            'declining': declining,
            'signal': 'Bullisch' if breadth > 60 else 'Bearisch' if breadth < 40 else 'Neutral'
        }
    
    @staticmethod
    def detect_elliott_waves(data, min_wave_size=0.02):
        """
        Vereinfachte Elliott-Wellen Erkennung
        """
        prices = data['Close'].values
        
        # Finde lokale Extrema
        peaks, _ = signal.find_peaks(prices, distance=5)
        troughs, _ = signal.find_peaks(-prices, distance=5)
        
        # Kombiniere und sortiere
        extrema = sorted([(i, 'peak') for i in peaks] + [(i, 'trough') for i in troughs])
        
        waves = []
        if len(extrema) >= 5:
            for i in range(len(extrema) - 4):
                # Prüfe auf 5-Wellen-Muster
                wave_pattern = [extrema[i+j][1] for j in range(5)]
                
                # Impuls-Welle: trough-peak-trough-peak-trough oder umgekehrt
                if wave_pattern in [['trough', 'peak', 'trough', 'peak', 'trough'],
                                   ['peak', 'trough', 'peak', 'trough', 'peak']]:
                    
                    wave_start = extrema[i][0]
                    wave_end = extrema[i+4][0]
                    wave_change = abs(prices[wave_end] - prices[wave_start]) / prices[wave_start]
                    
                    if wave_change > min_wave_size:
                        waves.append({
                            'type': 'Impulse',
                            'start_idx': wave_start,
                            'end_idx': wave_end,
                            'start_price': prices[wave_start],
                            'end_price': prices[wave_end],
                            'change': wave_change * 100
                        })
        
        return waves
    
    @staticmethod
    def calculate_market_regime(data, lookback=50):
        """
        Bestimmt das aktuelle Marktregime (Trending, Range-bound, Volatile)
        """
        returns = data['Close'].pct_change().dropna()
        
        # Berechne verschiedene Metriken
        volatility = returns.rolling(window=lookback).std().iloc[-1]
        trend_strength = abs(returns.rolling(window=lookback).mean().iloc[-1])
        
        # ADX für Trendstärke (vereinfacht)
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1]
        
        # Klassifizierung
        if trend_strength > volatility * 0.5:
            regime = "Trending"
            if returns.rolling(window=lookback).mean().iloc[-1] > 0:
                direction = "Aufwärts"
            else:
                direction = "Abwärts"
        elif volatility > returns.rolling(window=252).std().mean() * 1.5:
            regime = "Hochvolatil"
            direction = "Unbeständig"
        else:
            regime = "Seitwärts"
            direction = "Range-bound"
        
        return {
            'regime': regime,
            'direction': direction,
            'volatility': volatility * 100,
            'trend_strength': trend_strength * 100,
            'atr': atr
        }
    
    @staticmethod
    def calculate_correlation_matrix(tickers, period="3mo"):
        """
        Berechnet die Korrelationsmatrix zwischen verschiedenen Indizes
        """
        data = {}
        
        for ticker in tickers:
            try:
                df = yf.Ticker(ticker).history(period=period)
                if not df.empty:
                    data[ticker] = df['Close']
            except:
                continue
        
        if len(data) > 1:
            df = pd.DataFrame(data)
            correlation_matrix = df.pct_change().corr()
            
            # Finde höchste und niedrigste Korrelationen
            correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    correlations.append({
                        'pair': f"{correlation_matrix.columns[i]}-{correlation_matrix.columns[j]}",
                        'correlation': correlation_matrix.iloc[i, j]
                    })
            
            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            return {
                'matrix': correlation_matrix.to_dict(),
                'highest_correlation': correlations[0] if correlations else None,
                'lowest_correlation': correlations[-1] if correlations else None,
                'average_correlation': correlation_matrix.values[~np.eye(len(correlation_matrix), dtype=bool)].mean()
            }
        
        return None
    
    @staticmethod
    def calculate_seasonality(ticker, years=5):
        """
        Analysiert saisonale Muster
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            data = yf.Ticker(ticker).history(start=start_date, end=end_date)
            
            if data.empty:
                return None
            
            # Monatliche Returns
            data['Month'] = data.index.month
            data['Year'] = data.index.year
            data['Returns'] = data['Close'].pct_change()
            
            # Durchschnittliche monatliche Performance
            monthly_avg = data.groupby('Month')['Returns'].mean() * 100
            monthly_std = data.groupby('Month')['Returns'].std() * 100
            
            # Beste und schlechteste Monate
            best_month = monthly_avg.idxmax()
            worst_month = monthly_avg.idxmin()
            
            # Quartalsperformance
            data['Quarter'] = data.index.quarter
            quarterly_avg = data.groupby('Quarter')['Returns'].mean() * 100
            
            return {
                'monthly_average': monthly_avg.to_dict(),
                'monthly_volatility': monthly_std.to_dict(),
                'best_month': {
                    'month': best_month,
                    'average_return': monthly_avg[best_month]
                },
                'worst_month': {
                    'month': worst_month,
                    'average_return': monthly_avg[worst_month]
                },
                'quarterly_average': quarterly_avg.to_dict(),
                'current_month_historical': monthly_avg[datetime.now().month]
            }
        except Exception as e:
            print(f"Fehler bei Saisonalitätsanalyse: {e}")
            return None
    
    @staticmethod
    def identify_divergences(data):
        """
        Identifiziert Divergenzen zwischen Preis und Indikatoren
        """
        divergences = []
        
        # RSI Divergenz
        if 'RSI' in data.columns:
            # Finde Preis-Hochs und RSI-Werte
            price_peaks, _ = signal.find_peaks(data['Close'].values, distance=10)
            
            for i in range(1, len(price_peaks)):
                prev_peak = price_peaks[i-1]
                curr_peak = price_peaks[i]
                
                # Bearische Divergenz: Höheres Hoch im Preis, niedrigeres Hoch im RSI
                if (data['Close'].iloc[curr_peak] > data['Close'].iloc[prev_peak] and
                    data['RSI'].iloc[curr_peak] < data['RSI'].iloc[prev_peak]):
                    divergences.append({
                        'type': 'Bearische RSI Divergenz',
                        'date': data.index[curr_peak],
                        'price': data['Close'].iloc[curr_peak],
                        'indicator': data['RSI'].iloc[curr_peak],
                        'strength': 'Stark' if abs(data['RSI'].iloc[curr_peak] - data['RSI'].iloc[prev_peak]) > 10 else 'Schwach'
                    })
            
            # Bullische Divergenz
            price_troughs, _ = signal.find_peaks(-data['Close'].values, distance=10)
            
            for i in range(1, len(price_troughs)):
                prev_trough = price_troughs[i-1]
                curr_trough = price_troughs[i]
                
                # Bullische Divergenz: Niedrigeres Tief im Preis, höheres Tief im RSI
                if (data['Close'].iloc[curr_trough] < data['Close'].iloc[prev_trough] and
                    data['RSI'].iloc[curr_trough] > data['RSI'].iloc[prev_trough]):
                    divergences.append({
                        'type': 'Bullische RSI Divergenz',
                        'date': data.index[curr_trough],
                        'price': data['Close'].iloc[curr_trough],
                        'indicator': data['RSI'].iloc[curr_trough],
                        'strength': 'Stark' if abs(data['RSI'].iloc[curr_trough] - data['RSI'].iloc[prev_trough]) > 10 else 'Schwach'
                    })
        
        # MACD Divergenz
        if 'MACD' in data.columns:
            # Ähnliche Logik für MACD
            pass
        
        return divergences
    
    @staticmethod
    def calculate_risk_metrics(data, risk_free_rate=0.02):
        """
        Berechnet verschiedene Risikometriken
        """
        returns = data['Close'].pct_change().dropna()
        
        # Annualisierte Metriken (252 Handelstage)
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility != 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% Konfidenz)
        var_95 = returns.quantile(0.05)
        
        # Conditional Value at Risk
        cvar_95 = returns[returns <= var_95].mean()
        
        # Sortino Ratio (nur negative Volatilität)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252)
        sortino_ratio = (annual_return - risk_free_rate) / downside_deviation if downside_deviation != 0 else 0
        
        # Calmar Ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'annual_return': annual_return * 100,
            'annual_volatility': annual_volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown * 100,
            'var_95': var_95 * 100,
            'cvar_95': cvar_95 * 100,
            'risk_score': 'Niedrig' if annual_volatility < 0.15 else 'Mittel' if annual_volatility < 0.25 else 'Hoch'
        }
    
    @staticmethod
    def monte_carlo_simulation(data, days=30, simulations=1000):
        """
        Monte Carlo Simulation für Kursprognose
        """
        returns = data['Close'].pct_change().dropna()
        last_price = data['Close'].iloc[-1]
        
        # Parameter für die Simulation
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Simulation
        simulation_results = []
        
        for _ in range(simulations):
            price_path = [last_price]
            
            for _ in range(days):
                # Geometrische Brownsche Bewegung
                daily_return = np.random.normal(mean_return, std_return)
                price_path.append(price_path[-1] * (1 + daily_return))
            
            simulation_results.append(price_path[-1])
        
        simulation_results = np.array(simulation_results)
        
        return {
            'mean_price': np.mean(simulation_results),
            'median_price': np.median(simulation_results),
            'std_dev': np.std(simulation_results),
            'percentile_5': np.percentile(simulation_results, 5),
            'percentile_25': np.percentile(simulation_results, 25),
            'percentile_75': np.percentile(simulation_results, 75),
            'percentile_95': np.percentile(simulation_results, 95),
            'probability_above_current': (simulation_results > last_price).mean() * 100,
            'max_simulated': np.max(simulation_results),
            'min_simulated': np.min(simulation_results)
        }
    
    @staticmethod
    def pattern_recognition(data):
        """
        Erkennt klassische Chart-Muster
        """
        patterns = []
        close_prices = data['Close'].values
        
        # Head and Shoulders (vereinfacht)
        if len(close_prices) >= 5:
            for i in range(2, len(close_prices) - 2):
                # Prüfe auf Kopf-Schulter-Formation
                left_shoulder = close_prices[i-2]
                left_valley = close_prices[i-1]
                head = close_prices[i]
                right_valley = close_prices[i+1]
                right_shoulder = close_prices[i+2]
                
                # Head and Shoulders Top
                if (head > left_shoulder and head > right_shoulder and
                    abs(left_shoulder - right_shoulder) / left_shoulder < 0.03 and
                    left_valley < left_shoulder and right_valley < right_shoulder):
                    patterns.append({
                        'pattern': 'Head and Shoulders Top',
                        'position': i,
                        'date': data.index[i],
                        'signal': 'Bearisch',
                        'neckline': (left_valley + right_valley) / 2
                    })
        
        # Double Top/Bottom (vereinfacht)
        peaks, _ = signal.find_peaks(close_prices, distance=10)
        troughs, _ = signal.find_peaks(-close_prices, distance=10)
        
        # Double Top
        for i in range(1, len(peaks)):
            if abs(close_prices[peaks[i]] - close_prices[peaks[i-1]]) / close_prices[peaks[i-1]] < 0.03:
                patterns.append({
                    'pattern': 'Double Top',
                    'position': peaks[i],
                    'date': data.index[peaks[i]],
                    'signal': 'Bearisch',
                    'resistance': close_prices[peaks[i]]
                })
        
        # Double Bottom
        for i in range(1, len(troughs)):
            if abs(close_prices[troughs[i]] - close_prices[troughs[i-1]]) / close_prices[troughs[i-1]] < 0.03:
                patterns.append({
                    'pattern': 'Double Bottom',
                    'position': troughs[i],
                    'date': data.index[troughs[i]],
                    'signal': 'Bullisch',
                    'support': close_prices[troughs[i]]
                })
        
        # Triangle Patterns (vereinfacht)
        if len(close_prices) >= 20:
            recent_highs = []
            recent_lows = []
            
            for i in range(len(close_prices) - 20, len(close_prices)):
                window = close_prices[i:i+5]
                recent_highs.append(np.max(window))
                recent_lows.append(np.min(window))
            
            # Prüfe auf konvergierende Linien
            high_slope = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
            low_slope = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
            
            if high_slope < 0 and low_slope > 0:
                patterns.append({
                    'pattern': 'Symmetrical Triangle',
                    'position': len(close_prices) - 1,
                    'date': data.index[-1],
                    'signal': 'Neutral - Breakout erwartet',
                    'apex': (recent_highs[-1] + recent_lows[-1]) / 2
                })
            elif high_slope < 0 and abs(low_slope) < abs(high_slope) * 0.1:
                patterns.append({
                    'pattern': 'Descending Triangle',
                    'position': len(close_prices) - 1,
                    'date': data.index[-1],
                    'signal': 'Bearisch',
                    'support': np.mean(recent_lows)
                })
            elif low_slope > 0 and abs(high_slope) < abs(low_slope) * 0.1:
                patterns.append({
                    'pattern': 'Ascending Triangle',
                    'position': len(close_prices) - 1,
                    'date': data.index[-1],
                    'signal': 'Bullisch',
                    'resistance': np.mean(recent_highs)
                })
        
        return patterns