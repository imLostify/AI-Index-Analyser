"""
Hauptanwendung für den Index Analyser mit Streamlit UI
Enhanced with Candlestick Patterns, Gap-free Charts and Multi-language Support
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import json
import time
import numpy as np
import os
from typing import Dict  # ⬅️ NEU HINZUGEFÜGT
from config import *
from translations import get_text
from analysis import TechnicalAnalysis
from candlestick_patterns import CandlestickPatterns
from translations import get_text, TRANSLATIONS
# Import LLM Client - Try multiple versions for compatibility
try:
    from llm_client import LLMClient
except ImportError:
    try:
        from llm_client_v4 import LLMClientV4 as LLMClient
    except ImportError:
        try:
            from llm_client_v5 import LLMClientV5 as LLMClient
        except ImportError:
            print("Warning: No LLM Client found. AI features will be disabled.")
            LLMClient = None

# Session State für Sprache initialisieren
if 'language' not in st.session_state:
    st.session_state.language = 'de'

# Settings-Datei
SETTINGS_FILE = 'user_settings.json'

def load_settings():
    """Lädt gespeicherte Einstellungen"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """Speichert Einstellungen in Datei"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except:
        return False

# Lade gespeicherte Einstellungen beim Start
saved_settings = load_settings()

# Initialisiere Session State mit gespeicherten Werten
if 'settings_loaded' not in st.session_state:
    st.session_state.settings_loaded = True
    if saved_settings:
        st.session_state.saved_index = saved_settings.get('index', 0)
        st.session_state.saved_ticker = saved_settings.get('ticker', '^GSPC')
        st.session_state.saved_use_custom = saved_settings.get('use_custom', False)
        
        # Datumswerte laden
        if 'start_date' in saved_settings:
            try:
                st.session_state.start_date = datetime.fromisoformat(saved_settings['start_date']).date()
            except:
                st.session_state.start_date = datetime.now().date() - timedelta(days=365)
        if 'end_date' in saved_settings:
            try:
                st.session_state.end_date = datetime.fromisoformat(saved_settings['end_date']).date()
            except:
                st.session_state.end_date = datetime.now().date()
                
        st.session_state.saved_interval = saved_settings.get('interval', '1d')
        st.session_state.saved_use_llm = saved_settings.get('use_llm', True)
        st.session_state.saved_llm_temp = saved_settings.get('llm_temp', LLM_TEMPERATURE)
        st.session_state.saved_max_tokens = saved_settings.get('max_tokens', 5000)
        st.session_state.language = saved_settings.get('language', 'de')
        st.session_state.show_vwap = saved_settings.get('show_vwap', False)
        # Lade erweiterte Token-Einstellungen
        st.session_state.saved_tokens_indicators = saved_settings.get('tokens_indicators', 1500)
        st.session_state.saved_tokens_probabilities = saved_settings.get('tokens_probabilities', 1200)
        st.session_state.saved_tokens_fibonacci = saved_settings.get('tokens_fibonacci', 1800)
        st.session_state.saved_tokens_questions = saved_settings.get('tokens_questions', 800)
    else:
        # Standard-Werte wenn keine Einstellungen vorhanden
        st.session_state.saved_index = 0
        st.session_state.saved_ticker = '^GSPC'
        st.session_state.saved_use_custom = False
        st.session_state.start_date = datetime.now().date() - timedelta(days=365)
        st.session_state.end_date = datetime.now().date()
        st.session_state.saved_interval = '1d'
        st.session_state.saved_use_llm = True
        st.session_state.saved_llm_temp = LLM_TEMPERATURE
        st.session_state.saved_max_tokens = 5000
        st.session_state.show_vwap = False

# Seitenkonfiguration
st.set_page_config(
    page_title=get_text('app_title', st.session_state.language),
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für besseres Design
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    .analysis-box {
        background: rgba(30, 30, 46, 0.7);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #444;
        margin: 10px 0;
    }
    h1 {
        background: linear-gradient(90deg, #00DBDE 0%, #FC00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00DBDE 0%, #FC00FF 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        border-radius: 25px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(252, 0, 255, 0.4);
    }
    .pattern-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 2px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
    }
    .pattern-bullish {
        background-color: #00CC88;
        color: white;
    }
    .pattern-bearish {
        background-color: #FF4444;
        color: white;
    }
    .pattern-neutral {
        background-color: #888888;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Session State initialisieren
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'llm_analysis' not in st.session_state:
    st.session_state.llm_analysis = None
if 'candlestick_patterns' not in st.session_state:
    st.session_state.candlestick_patterns = None
if 'use_llm' not in st.session_state:
    st.session_state.use_llm = True
if 'current_interval' not in st.session_state:
    st.session_state.current_interval = '1d'
if 'show_vwap' not in st.session_state:
    st.session_state.show_vwap = False
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date() - timedelta(days=365)
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now().date()
# Token-Limits pro Abschnitt initialisieren
if 'tokens_indicators' not in st.session_state:
    st.session_state.tokens_indicators = 1500
if 'tokens_probabilities' not in st.session_state:
    st.session_state.tokens_probabilities = 1200
if 'tokens_fibonacci' not in st.session_state:
    st.session_state.tokens_fibonacci = 1800
if 'tokens_questions' not in st.session_state:
    st.session_state.tokens_questions = 800

def prepare_data_without_gaps(data, interval='1d'):
    """
    Entfernt Lücken (Wochenenden/Feiertage) aus den Daten für saubere Candlestick-Charts
    """
    # Erstelle einen neuen Index ohne Lücken
    data_copy = data.copy()
    data_copy['Date'] = data_copy.index
    data_copy = data_copy.reset_index(drop=True)
    
    # Erstelle x-Achsen Labels für jeden n-ten Datenpunkt
    num_points = len(data_copy)
    if num_points > 100:
        step = num_points // 20  # Zeige ~20 Labels
    else:
        step = max(1, num_points // 10)
    
    x_labels = []
    x_ticks = []
    
    # Formatierung basierend auf Intervall
    if interval in ['1m', '5m', '15m', '30m', '1h']:
        # Für Minuten/Stunden-Intervalle: Zeige Datum + Uhrzeit
        for i in range(0, num_points, step):
            x_labels.append(data_copy['Date'].iloc[i].strftime('%d.%m %H:%M'))
            x_ticks.append(i)
    else:
        # Für Tages-Intervalle und länger: Zeige nur Datum
        for i in range(0, num_points, step):
            x_labels.append(data_copy['Date'].iloc[i].strftime('%Y-%m-%d'))
            x_ticks.append(i)
    
    return data_copy, x_labels, x_ticks

def create_candlestick_chart(data, fibonacci_levels=None, support_resistance=None, patterns=None, language='de', interval='1d', show_vwap=False):
    """
    Erstellt einen separaten Candlestick-Chart für bessere Bedienung
    Mit professioneller X/Y-Achsen Skalierung wie bei Trading-Plattformen
    """
    # Daten ohne Lücken vorbereiten
    data_clean, x_labels, x_ticks = prepare_data_without_gaps(data, interval)
    x_range = list(range(len(data_clean)))
    
    # Candlestick Chart
    fig = go.Figure()
  
    
    # Erstelle Hover-Text für jede Kerze
    hover_texts = []
    for i in range(len(data_clean)):
        if interval in ['1m', '5m', '15m', '30m', '1h']:
            date_str = data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M')
        else:
            date_str = data_clean['Date'].iloc[i].strftime('%Y-%m-%d')
            
        hover_text = (
            f"Date: {date_str}<br>"
            f"Open: {data_clean['Open'].iloc[i]:.2f}<br>"
            f"High: {data_clean['High'].iloc[i]:.2f}<br>"
            f"Low: {data_clean['Low'].iloc[i]:.2f}<br>"
            f"Close: {data_clean['Close'].iloc[i]:.2f}<br>"
            f"Volume: {data_clean['Volume'].iloc[i]:,.0f}"
        )
        hover_texts.append(hover_text)
    
    fig.add_trace(
        go.Candlestick(
            x=x_range,
            open=data_clean['Open'],
            high=data_clean['High'],
            low=data_clean['Low'],
            close=data_clean['Close'],
            name='OHLC',
            increasing_line_color=CHART_COLORS['bullish'],
            decreasing_line_color=CHART_COLORS['bearish'],
            text=hover_texts,
            hoverinfo='text'
        )
    )
    
    # Exponential Moving Averages (aktualisiert auf 9, 21, 50, 200)
    for period in [9, 21, 50, 200]:
        col_name = f'EMA_{period}'
        if col_name in data.columns:
            ema_values = data[col_name].dropna()
            if len(ema_values) > 0:
                ema_clean = ema_values.iloc[-len(data_clean):].reset_index(drop=True)
                # Farben für verschiedene EMAs
                colors = {9: 'orange', 21: 'yellow', 50: 'cyan', 200: 'magenta'}
                fig.add_trace(
                    go.Scatter(
                        x=x_range[-len(ema_clean):],
                        y=ema_clean,
                        name=col_name,
                        line=dict(width=1.5, color=colors.get(period, 'white')),
                        opacity=0.8
                    )
                )
    
    # VWAP - Volume Weighted Average Price
    if show_vwap and 'VWAP' in data.columns:
        vwap_values = data['VWAP'].dropna()
        if len(vwap_values) > 0:
            vwap_clean = vwap_values.iloc[-len(data_clean):].reset_index(drop=True)
            fig.add_trace(
                go.Scatter(
                    x=x_range[-len(vwap_clean):],
                    y=vwap_clean,
                    name='VWAP',
                    line=dict(width=2, color='purple', dash='dot'),
                    opacity=0.9
                )
            )
    
    # Bollinger Bands
    if 'BB_upper' in data.columns and 'BB_lower' in data.columns:
        bb_upper = data['BB_upper'].iloc[-len(data_clean):].reset_index(drop=True)
        bb_lower = data['BB_lower'].iloc[-len(data_clean):].reset_index(drop=True)
        
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=bb_upper,
                name='BB Upper',
                line=dict(color='rgba(250,250,250,0.3)', width=1),
                opacity=0.5
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=bb_lower,
                name='BB Lower',
                line=dict(color='rgba(250,250,250,0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(200,200,200,0.1)',
                opacity=0.5
            )
        )
    
    # Fibonacci Levels
    if fibonacci_levels:
        for level_name, price in fibonacci_levels.get('retracement', {}).items():
            fig.add_hline(
                y=price,
                line_dash="dash",
                line_color="yellow",
                opacity=0.3,
                annotation_text=f"Fib {level_name}"
            )
    
    # Support & Resistance
    if support_resistance:
        for support in support_resistance.get('support', []):
            fig.add_hline(
                y=support,
                line_dash="dash",
                line_color="green",
                opacity=0.5,
                annotation_text=get_text('support', language)
            )
        for resistance in support_resistance.get('resistance', []):
            fig.add_hline(
                y=resistance,
                line_dash="dash",
                line_color="red",
                opacity=0.5,
                annotation_text=get_text('resistance', language)
            )
    
    # Candlestick Patterns markieren - ERWEITERT
    if patterns:
        # Gruppiere Patterns nach Index um Überlappungen zu vermeiden
        pattern_groups = {}
        for pattern in patterns:
            idx = pattern.get('index', -1)
            if idx >= 0 and idx < len(data_clean):
                if idx not in pattern_groups:
                    pattern_groups[idx] = []
                pattern_groups[idx].append(pattern)
        
        # Zeige die wichtigsten Patterns (max 30 für bessere Übersicht)
        sorted_indices = sorted(pattern_groups.keys())[-30:]
        
        for idx in sorted_indices:
            patterns_at_idx = pattern_groups[idx]
            
            # Wähle das wichtigste Pattern bei mehreren am gleichen Index
            reliability_order = {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1}
            patterns_at_idx.sort(key=lambda p: reliability_order.get(p.get('reliability', 'Low'), 0), reverse=True)
            main_pattern = patterns_at_idx[0]
            
            # Bestimme Farbe und Position
            signal = main_pattern.get('signal', '')
            if 'Bullish' in signal:
                color = CHART_COLORS['bullish']
                y_pos = data_clean['Low'].iloc[idx] * 0.995
                ay = 30
            elif 'Bearish' in signal:
                color = CHART_COLORS['bearish']
                y_pos = data_clean['High'].iloc[idx] * 1.005
                ay = -30
            else:
                color = CHART_COLORS['neutral']
                y_pos = (data_clean['High'].iloc[idx] + data_clean['Low'].iloc[idx]) / 2
                ay = 0
            
            # Pattern Name kürzen
            pattern_name = main_pattern.get('pattern', '')
            short_names = {
                'Three White Soldiers': '3WS',
                'Three Black Crows': '3BC',
                'Bullish Engulfing': 'B.Eng',
                'Bearish Engulfing': 'B.Eng',
                'Morning Star': 'M.Star',
                'Evening Star': 'E.Star',
                'Shooting Star': 'S.Star',
                'Hammer': 'Ham',
                'Inverted Hammer': 'I.Ham',
                'Hanging Man': 'H.Man',
                'Doji': 'Doji',
                'Spinning Top': 'Spin',
                'Marubozu': 'Maru',
                'Harami': 'Har',
                'Piercing Line': 'Pierc.',
                'Dark Cloud Cover': 'D.Cloud',
                'Dragonfly Doji': 'D.Doji',
                'Gravestone Doji': 'G.Doji',
                'Long-Legged Doji': 'LL.Doji',
                'Tweezer Top': 'Tw.Top',
                'Tweezer Bottom': 'Tw.Bot'
            }
            
            # Kürze den Namen wenn er zu lang ist
            for long_name, short_name in short_names.items():
                if long_name in pattern_name:
                    pattern_name = pattern_name.replace(long_name, short_name)
                    break
            if len(pattern_name) > 8:
                pattern_name = pattern_name[:8]
            
            # Füge Zuverlässigkeits-Marker hinzu
            reliability = main_pattern.get('reliability', 'Medium')
            if reliability == 'Very High':
                pattern_name += '***'
            elif reliability == 'High':
                pattern_name += '**'
            elif reliability == 'Medium':
                pattern_name += '*'
            
            # Erstelle Annotation
            fig.add_annotation(
                x=idx,
                y=y_pos,
                text=pattern_name,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                ax=0,
                ay=ay,
                bgcolor=color,
                bordercolor='white',
                borderwidth=1,
                opacity=0.9,
                font=dict(color='white', size=8, family='monospace')
            )
            
            # Zeige Anzahl weiterer Patterns
            if len(patterns_at_idx) > 1:
                fig.add_annotation(
                    x=idx,
                    y=y_pos,
                    text=f"+{len(patterns_at_idx)-1}",
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.3)',
                    font=dict(color='black', size=6),
                    xshift=25,
                    yshift=0
                )
    
    # Layout mit professionellen Trading-Chart Einstellungen
    fig.update_layout(
        title=get_text('technical_analysis', language),
        template='plotly_dark',
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified',
        xaxis=dict(
            autorange=True,
            rangeslider=dict(
                visible=True,
                thickness=0.05,
                bgcolor='rgba(40,40,40,0.5)'
            ),
            type='linear',
            tickmode='array',
            tickvals=x_ticks,
            ticktext=x_labels,
            tickangle=45,
            fixedrange=False,
            range=[max(0, len(x_range)-100), len(x_range)-1] if len(x_range) > 100 else None
        ),
        yaxis=dict(
            title=get_text('price', language) if 'price' in TRANSLATIONS[language] else 'Price',
            side='right',
            autorange=True,
            fixedrange=False,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            zeroline=False
        ),
        # ✅ FIXED: Changed from 'diagonal' to 'd' (valid value)
        dragmode='zoom',
        selectdirection='d',  # <-- This is the fix
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(255,255,255,0.7)',
            activecolor='rgba(255,255,255,1)',
            orientation='v'
        ),
        uirevision='constant',
        clickmode='event+select'
    )
    
    # [Range selector buttons code remains the same...]
    
    return fig

def create_indicator_charts(data, interval='1d', language='de'):
    """
    Erstellt separate Charts für RSI, MACD und Volumen mit korrekten Datumslabels
    """
    # Bereite Daten mit Datum vor
    data_clean, x_labels, x_ticks = prepare_data_without_gaps(data, interval)
    x_range = list(range(len(data_clean)))
    
    # Erstelle Subplots für Indikatoren
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('RSI', 'MACD', get_text('volume', language))
    )
    
    # RSI
    if 'RSI' in data.columns:
        rsi_values = data['RSI'].dropna()
        if len(rsi_values) > 0:
            # Passe RSI an die gleiche Länge an
            rsi_clean = rsi_values.iloc[-len(data_clean):].reset_index(drop=True)
            x_range_rsi = x_range[-len(rsi_clean):]
            
            fig.add_trace(
                go.Scatter(
                    x=x_range_rsi,
                    y=rsi_clean,
                    name='RSI',
                    line=dict(color='orange', width=2),
                    hovertemplate='RSI: %{y:.2f}<br>%{text}',
                    text=[data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M' if interval in ['1m', '5m', '15m', '30m', '1h'] else '%Y-%m-%d') 
                          for i in x_range_rsi]
                ),
                row=1, col=1
            )
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.3, row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.3, row=1, col=1)
    
    # MACD
    if 'MACD' in data.columns:
        macd_values = data['MACD'].dropna()
        if len(macd_values) > 0:
            macd_clean = macd_values.iloc[-len(data_clean):].reset_index(drop=True)
            x_range_macd = x_range[-len(macd_clean):]
            
            fig.add_trace(
                go.Scatter(
                    x=x_range_macd,
                    y=macd_clean,
                    name='MACD',
                    line=dict(color='blue', width=2),
                    hovertemplate='MACD: %{y:.2f}<br>%{text}',
                    text=[data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M' if interval in ['1m', '5m', '15m', '30m', '1h'] else '%Y-%m-%d')
                          for i in x_range_macd]
                ),
                row=2, col=1
            )
            
        if 'MACD_signal' in data.columns:
            signal_values = data['MACD_signal'].dropna()
            if len(signal_values) > 0:
                signal_clean = signal_values.iloc[-len(data_clean):].reset_index(drop=True)
                x_range_signal = x_range[-len(signal_clean):]
                
                fig.add_trace(
                    go.Scatter(
                        x=x_range_signal,
                        y=signal_clean,
                        name='Signal',
                        line=dict(color='red', width=2),
                        hovertemplate='Signal: %{y:.2f}<br>%{text}',
                        text=[data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M' if interval in ['1m', '5m', '15m', '30m', '1h'] else '%Y-%m-%d')
                              for i in x_range_signal]
                    ),
                    row=2, col=1
                )
                
        if 'MACD_diff' in data.columns:
            diff_values = data['MACD_diff'].dropna()
            if len(diff_values) > 0:
                diff_clean = diff_values.iloc[-len(data_clean):].reset_index(drop=True)
                x_range_diff = x_range[-len(diff_clean):]
                
                fig.add_trace(
                    go.Bar(
                        x=x_range_diff,
                        y=diff_clean,
                        name='Histogram',
                        marker_color='gray',
                        opacity=0.3,
                        hovertemplate='Histogram: %{y:.2f}<br>%{text}',
                        text=[data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M' if interval in ['1m', '5m', '15m', '30m', '1h'] else '%Y-%m-%d')
                              for i in x_range_diff]
                    ),
                    row=2, col=1
                )
    
    # Volumen
    if 'Volume' in data_clean.columns and 'Close' in data_clean.columns and 'Open' in data_clean.columns:
        colors = ['red' if data_clean['Close'].iloc[i] < data_clean['Open'].iloc[i] else 'green' 
                  for i in range(len(data_clean))]
        
        hover_texts = []
        for i in range(len(data_clean)):
            if interval in ['1m', '5m', '15m', '30m', '1h']:
                date_str = data_clean['Date'].iloc[i].strftime('%Y-%m-%d %H:%M')
            else:
                date_str = data_clean['Date'].iloc[i].strftime('%Y-%m-%d')
            hover_texts.append(f"Volume: {data_clean['Volume'].iloc[i]:,.0f}<br>{date_str}")
        
        fig.add_trace(
            go.Bar(
                x=x_range,
                y=data_clean['Volume'],
                name=get_text('volume', language),
                marker_color=colors,
                opacity=0.5,
                hovertemplate='%{text}',
                text=hover_texts
            ),
            row=3, col=1
        )
    
    # Update layout
    fig.update_layout(
        template='plotly_dark',
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    # Update x-axes mit Datumslabels
    for i in range(1, 4):
        fig.update_xaxes(
            tickmode='array',
            tickvals=x_ticks,
            ticktext=x_labels if i == 3 else [],  # Nur beim untersten Chart Labels zeigen
            tickangle=45 if i == 3 else 0,
            showticklabels=(i == 3),  # Nur beim untersten Chart
            rangeslider_visible=False,
            row=i, col=1
        )
    
    return fig

def translate_sentiment(sentiment, language='de'):
    """
    Übersetzt Sentiment-Werte in die gewählte Sprache
    """
    # Extrahiere Emoji wenn vorhanden
    emoji_map = {
        '🚀': '🚀',  # Rakete
        '📈': '📈',  # Chart up
        '➡️': '➡️',  # Pfeil rechts
        '📉': '📉',  # Chart down
        '🔻': '🔻'   # Roter Pfeil nach unten
    }
    
    emoji = ''
    for e in emoji_map.keys():
        if e in sentiment:
            emoji = e
            sentiment = sentiment.replace(e, '').strip()
            break
    
    # Normalisiere das Sentiment (uppercase und trimmed)
    sentiment_normalized = sentiment.strip().upper()
    
    # Definiere Übersetzungen (beide Richtungen)
    if language == 'en':
        # Deutsch -> Englisch
        translations = {
            'SEHR BULLISCH': 'VERY BULLISH',
            'BULLISCH': 'BULLISH',
            'NEUTRAL': 'NEUTRAL',
            'BEARISCH': 'BEARISH',
            'SEHR BEARISCH': 'VERY BEARISH',
            'STARK BULLISCH': 'STRONG BULLISH',
            'STARK BEARISCH': 'STRONG BEARISH'
        }
    else:
        # Englisch -> Deutsch (falls nötig)
        translations = {
            'VERY BULLISH': 'SEHR BULLISCH',
            'STRONG BULLISH': 'STARK BULLISCH',
            'BULLISH': 'BULLISCH',
            'NEUTRAL': 'NEUTRAL',
            'BEARISH': 'BEARISCH',
            'STRONG BEARISH': 'STARK BEARISCH',
            'VERY BEARISH': 'SEHR BEARISCH'
        }
    
    # Prüfe zuerst längere Phrasen (z.B. "SEHR BULLISCH" vor "BULLISCH")
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)
    
    translated = sentiment_normalized
    for key in sorted_keys:
        if key in sentiment_normalized:
            translated = sentiment_normalized.replace(key, translations[key])
            break
    
    # Füge Emoji wieder hinzu wenn vorhanden
    if emoji:
        translated = f"{translated} {emoji}"
    
    return translated

def display_metrics(analysis, language='de'):
    """
    Zeigt die wichtigsten Metriken in einer übersichtlichen Form
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_price = analysis.data['Close'].iloc[-1]
        price_change = analysis.data['Close'].pct_change().iloc[-1] * 100
        st.metric(
            get_text('current_price', language),
            f"${current_price:.2f}",
            f"{price_change:+.2f}%"
        )
    
    with col2:
        if analysis.indicators.get('RSI'):
            rsi_value = analysis.indicators['RSI']
            if rsi_value > 70:
                rsi_status = get_text('overbought', language)
            elif rsi_value < 30:
                rsi_status = get_text('oversold', language)
            else:
                rsi_status = get_text('normal', language)
            st.metric(
                "RSI",
                f"{rsi_value:.2f}",
                rsi_status
            )
    
    with col3:
        sentiment_result = analysis.get_market_sentiment()
        # Handle both old format (tuple of 2) and new format (tuple of 3)
        if len(sentiment_result) == 3:
            sentiment, strength, reasoning = sentiment_result
        else:
            sentiment, strength = sentiment_result
            reasoning = "Keine Begründung verfügbar"
        
        # Übersetze Sentiment
        translated_sentiment = translate_sentiment(sentiment, language)
        
        st.metric(
            get_text('market_sentiment', language),
            translated_sentiment,
            f"{get_text('strength', language)}: {strength:.1f}"
        )
        # Zeige Begründung in einem Expander
        with st.expander(f"📊 {get_text('reasoning', language)}", expanded=False):
            st.caption(reasoning)
    
    with col4:
        if analysis.indicators.get('ATR'):
            atr_value = analysis.indicators['ATR']
            volatility = get_text('high', language) if atr_value > analysis.data['Close'].iloc[-1] * 0.02 else get_text('normal', language)
            st.metric(
                get_text('volatility', language),
                f"{atr_value:.2f}",
                volatility
            )

def display_probabilities(probabilities, targets, language='de'):
    """
    Zeigt Wahrscheinlichkeiten und Kursziele an
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {get_text('scenario_probabilities', language)}")
        
        # Wahrscheinlichkeits-Balken mit neutral
        bullish_prob = probabilities.get('bullish_probability', 33.33)
        bearish_prob = probabilities.get('bearish_probability', 33.33)
        neutral_prob = probabilities.get('neutral_probability', 33.34)
        
        fig = go.Figure(data=[
            go.Bar(name=get_text('bullish', language), x=[get_text('probability', language)], y=[bullish_prob], 
                   marker_color=CHART_COLORS['bullish']),
            go.Bar(name=get_text('neutral', language), x=[get_text('probability', language)], y=[neutral_prob],
                   marker_color=CHART_COLORS['neutral']),
            go.Bar(name=get_text('bearish', language), x=[get_text('probability', language)], y=[bearish_prob],
                   marker_color=CHART_COLORS['bearish'])
        ])
        fig.update_layout(
            barmode='stack',
            template='plotly_dark',
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Signal-Übersicht mit neutral und Erklärung
        total = probabilities.get('total_signals', 0)
        bullish = probabilities.get('bullish_signals', 0)
        neutral = probabilities.get('neutral_signals', 0)
        bearish = probabilities.get('bearish_signals', 0)
        
        if total > 0:
            st.markdown(f"""
            **{get_text('signal_analysis', language)}:**
            - {get_text('bullish_signals', language)}: {bullish}/{total} ({bullish/total*100:.1f}%)
            - {get_text('neutral_signals', language)}: {neutral}/{total} ({neutral/total*100:.1f}%)
            - {get_text('bearish_signals', language)}: {bearish}/{total} ({bearish/total*100:.1f}%)
            """)
        else:
            st.markdown(f"""
            **{get_text('signal_analysis', language)}:**
            - {get_text('no_signals_available', language)}
            """)
        
        # Erklärung warum das Sentiment trotz Signal-Verteilung anders sein kann
        if neutral > (bullish + bearish) * 2:  # Wenn sehr viele neutrale Signale
            if language == 'de':
                st.info("💡 **Hinweis:** Viele neutrale Signale deuten auf eine Konsolidierungsphase hin. Das Sentiment basiert zusätzlich auf Trend-Indikatoren wie EMAs, MACD und RSI.")
            else:
                st.info("💡 **Note:** Many neutral signals indicate a consolidation phase. The sentiment is also based on trend indicators like EMAs, MACD and RSI.")
    
    with col2:
        st.markdown(f"### {get_text('price_targets', language)}")
        
        # Bullische Ziele
        if targets['bullish']:
            st.markdown(f"**{get_text('bullish_targets', language)}:**")
            for target in targets['bullish'][:3]:
                st.markdown(f"- {target['level']}: ${target['price']:.2f} ({target['distance']:+.2f}%)")
        
        # Bearische Ziele
        if targets['bearish']:
            st.markdown(f"**{get_text('bearish_targets', language)}:**")
            for target in targets['bearish'][:3]:
                st.markdown(f"- {target['level']}: ${target['price']:.2f} ({target['distance']:.2f}%)")

def display_premium_report(full_analysis: Dict, patterns_data: Dict, language: str = 'de'):
    """Zeigt den verbesserten Premium-Bericht an"""
    
    st.markdown(f"## 📊 {get_text('market_report', language)}")
    
    # LLM Client für Premium-Bericht
    llm_client = LLMClient()
    
    try:
        with st.spinner(get_text('generating_report', language)):
            premium_report = llm_client.generate_premium_report(full_analysis, patterns_data)
            
            # Strukturierte Anzeige
            for section, content in premium_report.items():
                with st.expander(f"**{section}**", expanded=True):
                    if isinstance(content, dict):
                        for key, value in content.items():
                            if isinstance(value, list):
                                for item in value:
                                    st.write(f"• {item}")
                            else:
                                st.write(f"**{key}:** {value}")
                    else:
                        st.write(content)
                        
    except Exception as e:
        st.error(f"Fehler bei der Berichterstellung: {str(e)}")


def display_candlestick_patterns(patterns, statistics, language='de'):
    """
    Zeigt erkannte Candlestick-Muster an
    """
    st.markdown(f"### {get_text('candlestick_analysis', language)}")
    
    if not patterns:
        st.info(f"Keine {get_text('patterns_found', language).lower()}")
        return
    
    # Statistiken
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(get_text('total_patterns', language), statistics['total_patterns'])
    
    with col2:
        st.metric(get_text('bullish', language), statistics['bullish_patterns'])
    
    with col3:
        st.metric(get_text('bearish', language), statistics['bearish_patterns'])
    
    with col4:
        st.metric(get_text('neutral', language), statistics['neutral_patterns'])
    
    # Aktuelle Muster in Tabelle
    st.markdown(f"#### {get_text('recent_patterns', language)}")
    
    pattern_df = pd.DataFrame(statistics['recent_patterns'])
    if not pattern_df.empty:
        # Formatiere die Tabelle
        pattern_df['formatted_date'] = pd.to_datetime(pattern_df['date']).dt.strftime('%Y-%m-%d')
        pattern_df['formatted_price'] = pattern_df['price'].apply(lambda x: f"${x:.2f}")
        
        # Zeige die Tabelle
        display_df = pattern_df[['formatted_date', 'pattern', 'signal', 'reliability', 'formatted_price']]
        display_df.columns = [
            get_text('date', language) if 'date' in TRANSLATIONS[language] else 'Date',
            get_text('pattern', language),
            get_text('signal', language),
            get_text('reliability', language),
            get_text('price', language) if 'price' in TRANSLATIONS[language] else 'Price'
        ]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    # Pattern-Typ Verteilung
    if statistics['pattern_types']:
        st.markdown(f"#### {get_text('pattern_statistics', language)}")
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(statistics['pattern_types'].keys()),
                y=list(statistics['pattern_types'].values()),
                marker_color='rgba(0, 204, 136, 0.6)'
            )
        ])
        fig.update_layout(
            template='plotly_dark',
            height=300,
            xaxis_title=get_text('pattern', language),
            yaxis_title='Count'
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """
    Hauptfunktion der Streamlit App
    """
    lang = st.session_state.language
    
    # Header
    st.markdown(f"<h1>{get_text('app_title', lang)}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## {get_text('settings', lang)}")
        
        # Sprachauswahl
        new_lang = st.selectbox(
            get_text('language', lang),
            options=['de', 'en'],
            index=0 if lang == 'de' else 1,
            format_func=lambda x: '🇩🇪 Deutsch' if x == 'de' else '🇺🇸 English'
        )
        
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()
        
        # Index Auswahl
        index_list = list(POPULAR_INDICES.keys())
        index_choice = st.selectbox(
            get_text('select_index', lang),
            options=index_list,
            index=st.session_state.get('saved_index', 0) if st.session_state.get('saved_index', 0) < len(index_list) else 0
        )
        ticker_symbol = POPULAR_INDICES[index_choice]
        
        # Custom Ticker Option
        use_custom = st.checkbox(
            get_text('custom_symbol', lang),
            value=st.session_state.get('saved_use_custom', False)
        )
        if use_custom:
            ticker_symbol = st.text_input(
                get_text('ticker_symbol', lang), 
                value=st.session_state.get('saved_ticker', '^GSPC')
            )
        
        # Zeitraum mit Kalender-Auswahl
        st.markdown(f"### {get_text('period', lang)}")
        
        # Datum-Auswahl mit Kalender
        col_start, col_end = st.columns(2)
        
        with col_start:
            start_date = st.date_input(
                get_text('from_date', lang),
                value=st.session_state.get('start_date', datetime.now().date() - timedelta(days=365)),
                max_value=datetime.now().date(),
                format="DD.MM.YYYY",
                key="start_date_input"
            )
            st.session_state.start_date = start_date
        
        with col_end:
            end_date = st.date_input(
                get_text('to_date', lang),
                value=st.session_state.get('end_date', datetime.now().date()),
                min_value=start_date,
                max_value=datetime.now().date(),
                format="DD.MM.YYYY",
                key="end_date_input"
            )
            st.session_state.end_date = end_date
        
        # Berechne Periode basierend auf Datumsauswahl
        days_diff = (end_date - start_date).days
        
        # Quick-Select Buttons für häufige Zeiträume
        st.markdown(f"**{get_text('quick_select', lang)}:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(get_text('one_week', lang), use_container_width=True):
                start_date = datetime.now().date() - timedelta(days=7)
                end_date = datetime.now().date()
                st.rerun()
        with col2:
            if st.button(get_text('one_month', lang), use_container_width=True):
                start_date = datetime.now().date() - timedelta(days=30)
                end_date = datetime.now().date()
                st.rerun()
        with col3:
            if st.button(get_text('one_year', lang), use_container_width=True):
                start_date = datetime.now().date() - timedelta(days=365)
                end_date = datetime.now().date()
                st.rerun()
        
        # Intervall
        interval_options = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        interval = st.selectbox(
            get_text('interval', lang),
            options=interval_options,
            index=interval_options.index(st.session_state.get('saved_interval', '1d'))
                  if st.session_state.get('saved_interval', '1d') in interval_options else 5
        )
        st.session_state.current_interval = interval  # Speichere das Intervall
        
        st.markdown("---")
        
        # Chart-Einstellungen
        st.markdown(f"### {get_text('chart_settings', lang)}")
        
        # VWAP Toggle
        show_vwap = st.checkbox(
            get_text('show_vwap', lang),
            value=st.session_state.get('show_vwap', False),
            help=get_text('vwap_help', lang)
        )
        st.session_state.show_vwap = show_vwap
        
        st.markdown("---")
        
        # LLM Einstellungen
        st.markdown(f"## {get_text('ai_settings', lang)}")
        use_llm = st.checkbox(
            get_text('enable_ai', lang), 
            value=st.session_state.get('saved_use_llm', True)
        )
        st.session_state.use_llm = use_llm
        
        llm_temp = LLM_TEMPERATURE
        max_tokens = 5000
        
        if use_llm:
            llm_temp = st.slider(
                get_text('creativity', lang), 
                0.0, 1.0, 
                st.session_state.get('saved_llm_temp', LLM_TEMPERATURE), 
                0.1
            )
            # Erhöhe max_tokens für vollständige Berichte - bis zu 15000
            max_tokens = st.slider(
                get_text('max_tokens', lang), 
                min_value=500, 
                max_value=25000, 
                value=st.session_state.get('saved_max_tokens', 5000), 
                step=500,
                help="Erhöhen Sie diesen Wert für längere, detailliertere Berichte. Hinweis: Sehr hohe Werte (>10000) können die Generierung verlangsamen."
            )
            st.session_state.max_tokens = max_tokens  # Speichere in Session State
            
            # Zeige Warnung bei sehr hohen Token-Werten
            if max_tokens > 10000:
                st.warning(f"{get_text('token_warning', lang)}. {get_text('token_warning_llm', lang)}.")
            
            # Erweiterte Einstellungen für Token-Limits pro Abschnitt
            with st.expander(get_text('advanced_settings', lang), expanded=False):
                st.markdown(f"### {get_text('section_tokens', lang)}")
                st.caption(get_text('tokens_help', lang))
                
                # Token-Limits für verschiedene Abschnitte
                tokens_indicators = st.slider(
                    get_text('tokens_indicators', lang),
                    min_value=200,
                    max_value=5000,
                    value=st.session_state.get('saved_tokens_indicators', 1500),
                    step=100,
                    key='tokens_indicators_slider'
                )
                st.session_state.tokens_indicators = tokens_indicators
                
                tokens_probabilities = st.slider(
                    get_text('tokens_probabilities', lang),
                    min_value=200,
                    max_value=5000,
                    value=st.session_state.get('saved_tokens_probabilities', 1200),
                    step=100,
                    key='tokens_probabilities_slider'
                )
                st.session_state.tokens_probabilities = tokens_probabilities
                
                tokens_fibonacci = st.slider(
                    get_text('tokens_fibonacci', lang),
                    min_value=200,
                    max_value=5000,
                    value=st.session_state.get('saved_tokens_fibonacci', 1800),
                    step=100,
                    key='tokens_fibonacci_slider'
                )
                st.session_state.tokens_fibonacci = tokens_fibonacci
                
                tokens_questions = st.slider(
                    get_text('tokens_questions', lang),
                    min_value=200,
                    max_value=3000,
                    value=st.session_state.get('saved_tokens_questions', 800),
                    step=100,
                    key='tokens_questions_slider'
                )
                st.session_state.tokens_questions = tokens_questions
        
        st.markdown("---")
        
        # Save/Load Settings Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(get_text('save_settings', lang), use_container_width=True):
                # Speichere aktuelle Einstellungen
                settings_to_save = {
                    'language': lang,
                    'index': index_list.index(index_choice) if index_choice in index_list else 0,
                    'ticker': ticker_symbol,
                    'use_custom': use_custom,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'interval': interval,
                    'use_llm': use_llm,
                    'llm_temp': llm_temp,
                    'max_tokens': max_tokens,
                    'show_vwap': st.session_state.get('show_vwap', False),
                    # Erweiterte Token-Einstellungen speichern
                    'tokens_indicators': st.session_state.get('tokens_indicators', 1500),
                    'tokens_probabilities': st.session_state.get('tokens_probabilities', 1200),
                    'tokens_fibonacci': st.session_state.get('tokens_fibonacci', 1800),
                    'tokens_questions': st.session_state.get('tokens_questions', 800)
                }
                
                if save_settings(settings_to_save):
                    # Update Session State
                    st.session_state.saved_index = index_list.index(index_choice)
                    st.session_state.saved_ticker = ticker_symbol
                    st.session_state.saved_use_custom = use_custom
                    st.session_state.start_date = start_date
                    st.session_state.end_date = end_date
                    st.session_state.saved_interval = interval
                    st.session_state.saved_use_llm = use_llm
                    st.session_state.saved_llm_temp = llm_temp
                    st.session_state.saved_max_tokens = max_tokens
                    st.session_state.show_vwap = st.session_state.get('show_vwap', False)
                    # Erweiterte Token-Einstellungen in Session State speichern
                    st.session_state.saved_tokens_indicators = st.session_state.get('tokens_indicators', 1500)
                    st.session_state.saved_tokens_probabilities = st.session_state.get('tokens_probabilities', 1200)
                    st.session_state.saved_tokens_fibonacci = st.session_state.get('tokens_fibonacci', 1800)
                    st.session_state.saved_tokens_questions = st.session_state.get('tokens_questions', 800)
                    
                    st.success(get_text('settings_saved', lang))
                else:
                    st.error(get_text('settings_save_failed', lang))
        
        with col2:
            if st.button(get_text('reset_settings', lang), use_container_width=True):
                # Lösche gespeicherte Einstellungen
                if os.path.exists(SETTINGS_FILE):
                    try:
                        os.remove(SETTINGS_FILE)
                        # Reset Session State
                        st.session_state.saved_index = 0
                        st.session_state.saved_ticker = '^GSPC'
                        st.session_state.saved_use_custom = False
                        st.session_state.start_date = datetime.now().date() - timedelta(days=365)
                        st.session_state.end_date = datetime.now().date()
                        st.session_state.saved_interval = '1d'
                        st.session_state.saved_use_llm = True
                        st.session_state.saved_llm_temp = LLM_TEMPERATURE
                        st.session_state.saved_max_tokens = 5000
                        st.session_state.show_vwap = False
                        # Reset erweiterte Token-Einstellungen
                        st.session_state.saved_tokens_indicators = 1500
                        st.session_state.saved_tokens_probabilities = 1200
                        st.session_state.saved_tokens_fibonacci = 1800
                        st.session_state.saved_tokens_questions = 800
                        st.success(get_text('settings_reset', lang))
                        st.rerun()
                    except:
                        st.error(get_text('settings_reset_failed', lang))
        
        # Analyse Button
        analyze_button = st.button(get_text('start_analysis', lang), use_container_width=True)
    
    # Hauptbereich
    if analyze_button:
        # Lösche alte Analyse-Daten um sicherzustellen dass neue Analyse durchgeführt wird
        if 'analysis_data' in st.session_state:
            del st.session_state.analysis_data
        if 'candlestick_patterns' in st.session_state:
            del st.session_state.candlestick_patterns
        if 'llm_analysis' in st.session_state:
            del st.session_state.llm_analysis
        if 'generated_report' in st.session_state:
            del st.session_state.generated_report
            
        with st.spinner(get_text('loading_data', lang)):
            try:
                # Technische Analyse mit Datum-Parametern
                analysis = TechnicalAnalysis(
                    ticker_symbol, 
                    period=None,  # Wird nicht mehr benötigt wenn Datumswerte verwendet werden
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not analysis.fetch_data():
                    st.error(get_text('error_loading', lang))
                    return
                
                # Indikatoren berechnen - VWAP nur wenn aktiviert
                include_vwap = st.session_state.get('show_vwap', False)
                analysis.calculate_all_indicators(include_vwap=include_vwap)
                analysis.calculate_fibonacci_levels()
                analysis.identify_support_resistance()
                
                # Candlestick Patterns erkennen
                pattern_detector = CandlestickPatterns(analysis.data)
                patterns = pattern_detector.detect_all_patterns()
                pattern_stats = pattern_detector.get_pattern_statistics()
                
                # Wahrscheinlichkeiten und Ziele
                probabilities = analysis.calculate_probabilities()
                targets = analysis.calculate_price_targets()
                
                # Speichern in Session State
                st.session_state.analysis_data = {
                    'ticker': ticker_symbol,
                    'data': analysis.data.to_dict(),
                    'indicators': analysis.indicators,
                    'fibonacci': analysis.fibonacci_levels,
                    'support_resistance': analysis.support_resistance,
                    'probabilities': probabilities,
                    'targets': targets,
                    'sentiment': analysis.get_market_sentiment(),
                    'interval': interval,  # Speichere das verwendete Intervall
                    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Aktuelles Datum
                    'settings_used': {  # Speichere verwendete Einstellungen
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'interval': interval,
                        'ticker': ticker_symbol
                    }
                }
                st.session_state.candlestick_patterns = {
                    'patterns': patterns,
                    'statistics': pattern_stats
                }
                
                st.success(get_text('analysis_complete', lang))
            except Exception as e:
                error_msg = get_text('analysis_error', lang) if 'analysis_error' in TRANSLATIONS[lang] else f"Error during analysis: {str(e)}"
                st.error(error_msg)
                st.error(get_text('try_different', lang) if 'try_different' in TRANSLATIONS[lang] else "Please try a different symbol or time period.")
    
    # Ergebnisse anzeigen
    if st.session_state.analysis_data is not None:
        data = st.session_state.analysis_data
        patterns_data = st.session_state.candlestick_patterns
        
        # Tabs erstellen
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            get_text('tab_overview', lang),
            get_text('tab_charts', lang),
            get_text('tab_indicators', lang),
            get_text('tab_patterns', lang),
            get_text('tab_ai_analysis', lang)
        ])
        
        with tab1:
            st.markdown(f"## {data['ticker']} Analysis")
            if 'analysis_date' in data:
                st.caption(f"{get_text('analysis_from', lang)}: {data['analysis_date']}")
            
            # Metriken anzeigen
            analysis_obj = TechnicalAnalysis(data['ticker'])
            analysis_obj.data = pd.DataFrame(data['data'])
            analysis_obj.indicators = data['indicators']
            analysis_obj.fibonacci_levels = data['fibonacci']
            analysis_obj.support_resistance = data['support_resistance']
            
            display_metrics(analysis_obj, lang)
            
            st.markdown("---")
            
            # Wahrscheinlichkeiten und Ziele
            if data.get('probabilities') and data.get('targets'):
                display_probabilities(data['probabilities'], data['targets'], lang)
        
        with tab2:
            st.markdown(f"## {get_text('tab_charts', lang)}")
            
            # HAUPTCHART: Separater Candlestick Chart für bessere Bedienung
            st.markdown("📊 **Candlestick Chart**")
            
            # Bedienungshinweise
            with st.expander(f"💡 {get_text('chart_controls_legend', lang)}", expanded=False):
                if lang == 'de':
                    st.markdown("""
                    **Zoom & Navigation:**
                    - 🔍 **Zoom:** Klicken und ziehen Sie mit der Maus über den Bereich, den Sie vergrößern möchten
                    - 🌐 **X/Y-Achsen Zoom:** Ziehen Sie horizontal für Zeit-Zoom, vertikal für Preis-Zoom, diagonal für beides
                    - 🔄 **Reset:** Doppelklick auf den Chart setzt die Ansicht zurück
                    - 👆 **Pan:** Wählen Sie das Pan-Tool in der Toolbar (Handsymbol) und ziehen Sie den Chart
                    - 📏 **Range Slider:** Nutzen Sie den Slider unter dem Chart für schnelle Navigation
                    - 📅 **Zeiträume:** Nutzen Sie die Buttons (1D, 1W, 1M, etc.) für vordefinierte Zeiträume
                    - 💾 **Screenshot:** Nutzen Sie das Kamera-Symbol in der Toolbar für einen Screenshot
                    
                    **Candlestick Pattern Legende:**
                    
                    🟢 **Bullische Patterns** (Kaufsignale):
                    - **Ham** = Hammer - Umkehrsignal nach Abwärtstrend
                    - **B.Eng** = Bullish Engulfing - Starkes Kaufsignal
                    - **M.Star** = Morning Star - Sehr starkes Umkehrsignal
                    - **3WS** = Three White Soldiers - Starker Aufwärtstrend
                    - **Pierc.** = Piercing Line - Bullische Umkehr
                    
                    🔴 **Bearische Patterns** (Verkaufssignale):
                    - **H.Man** = Hanging Man - Warnung am Top
                    - **B.Eng** = Bearish Engulfing - Starkes Verkaufssignal
                    - **E.Star** = Evening Star - Sehr starkes Umkehrsignal
                    - **3BC** = Three Black Crows - Starker Abwärtstrend
                    - **S.Star** = Shooting Star - Umkehr nach oben
                    
                    🟡 **Neutrale Patterns** (Unentschlossenheit):
                    - **Doji** = Markt-Unentschlossenheit
                    - **Spin** = Spinning Top - Konsolidierung
                    - **Har** = Harami - Mögliche Trendwende
                    
                    **⭐ Zuverlässigkeitssystem:**
                    - ⭐⭐⭐ oder *** = Sehr hohe Zuverlässigkeit (Very High)
                    - ⭐⭐ oder ** = Hohe Zuverlässigkeit (High)
                    - ⭐ oder * = Mittlere Zuverlässigkeit (Medium)
                    - (kein Stern) = Niedrige Zuverlässigkeit (Low)
                    
                    **Hinweis:** Je mehr Sterne, desto verlässlicher das Signal!
                    """)
                else:
                    st.markdown("""
                    **Zoom & Navigation:**
                    - 🔍 **Zoom:** Click and drag to zoom into a specific area
                    - 🌐 **X/Y-Axis Zoom:** Drag horizontally for time zoom, vertically for price zoom, diagonally for both
                    - 🔄 **Reset:** Double-click on chart to reset view
                    - 👆 **Pan:** Select pan tool (hand icon) and drag the chart
                    - 📏 **Range Slider:** Use slider below chart for quick navigation
                    - 📅 **Time Periods:** Use buttons (1D, 1W, 1M, etc.) for predefined periods
                    - 💾 **Screenshot:** Use camera icon in toolbar to save image
                    
                    **Candlestick Pattern Legend:**
                    
                    🟢 **Bullish Patterns** (Buy Signals):
                    - **Ham** = Hammer - Reversal signal after downtrend
                    - **B.Eng** = Bullish Engulfing - Strong buy signal
                    - **M.Star** = Morning Star - Very strong reversal signal
                    - **3WS** = Three White Soldiers - Strong uptrend
                    - **Pierc.** = Piercing Line - Bullish reversal
                    
                    🔴 **Bearish Patterns** (Sell Signals):
                    - **H.Man** = Hanging Man - Warning at top
                    - **B.Eng** = Bearish Engulfing - Strong sell signal
                    - **E.Star** = Evening Star - Very strong reversal signal
                    - **3BC** = Three Black Crows - Strong downtrend
                    - **S.Star** = Shooting Star - Reversal after uptrend
                    
                    🟡 **Neutral Patterns** (Indecision):
                    - **Doji** = Market indecision
                    - **Spin** = Spinning Top - Consolidation
                    - **Har** = Harami - Possible trend change
                    
                    **⭐ Reliability System:**
                    - ⭐⭐⭐ or *** = Very High reliability
                    - ⭐⭐ or ** = High reliability
                    - ⭐ or * = Medium reliability
                    - (no star) = Low reliability
                    
                    **Note:** More stars mean more reliable signals!
                    """)
            
            fig_candles = create_candlestick_chart(
                pd.DataFrame(data['data']),
                data.get('fibonacci'),
                data.get('support_resistance'),
                patterns_data.get('patterns') if patterns_data else None,
                lang,
                data.get('interval', '1d'),  # Verwende gespeichertes Intervall
                show_vwap=st.session_state.get('show_vwap', False)  # Übergebe VWAP-Flag
            )
            st.plotly_chart(fig_candles, use_container_width=True)
            
            # INDIKATOREN: Separate Charts
            st.markdown(f"### 📈 {get_text('technical_indicators_chart', lang)}")
            fig_indicators = create_indicator_charts(
                pd.DataFrame(data['data']), 
                data.get('interval', '1d'),  # Verwende gespeichertes Intervall
                lang
            )
            st.plotly_chart(fig_indicators, use_container_width=True)
            
            # Zusätzliche Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Heatmap der Korrelationen
                st.markdown(f"### {get_text('correlation_matrix', lang)}")
                df = pd.DataFrame(data['data'])
                indicator_cols = [col for col in df.columns if any(ind in col for ind in ['RSI', 'MACD', 'BB', 'SMA', 'EMA'])]
                if len(indicator_cols) > 1:
                    corr_matrix = df[indicator_cols].corr()
                    fig_corr = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0
                    ))
                    fig_corr.update_layout(
                        template='plotly_dark',
                        height=400,
                        title=get_text('correlation_matrix', lang)
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
            
            with col2:
                # Volumen-Analyse
                st.markdown(f"### {get_text('volume_analysis', lang)}")
                df = pd.DataFrame(data['data'])
                if 'Volume' in df.columns:
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Scatter(
                        x=df.index,
                        y=df['Volume'].rolling(window=20).mean(),
                        name=get_text('20_day_average', lang),
                        line=dict(color='yellow', width=2)
                    ))
                    fig_vol.add_trace(go.Bar(
                        x=df.index,
                        y=df['Volume'],
                        name=get_text('volume', lang),
                        marker_color='rgba(100,100,100,0.3)'
                    ))
                    fig_vol.update_layout(
                        template='plotly_dark',
                        height=400,
                        title=get_text('volume_trend', lang) if 'volume_trend' in TRANSLATIONS[lang] else 'Volume Trend'
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)
        
        with tab3:
            st.markdown(f"## {get_text('tab_indicators', lang)}")
            
            if data.get('indicators'):
                # Indikatoren in Kategorien anzeigen
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"### {get_text('trend_indicators', lang)}")
                    if 'moving_averages' in data['indicators']:
                        # Nur EMAs anzeigen (keine SMAs mehr)
                        st.markdown("**Exponential Moving Averages:**")
                        for period, value in data['indicators']['moving_averages']['ema'].items():
                            if value:
                                st.markdown(f"- EMA {period}: ${value:.2f}")
                    
                    if data['indicators'].get('ADX'):
                        adx = data['indicators']['ADX']
                        if adx.get('adx'):
                            st.markdown(f"**ADX:** {adx['adx']:.2f}")
                            if adx.get('di_plus'):
                                st.markdown(f"- DI+: {adx['di_plus']:.2f}")
                            if adx.get('di_minus'):
                                st.markdown(f"- DI-: {adx['di_minus']:.2f}")
                
                with col2:
                    st.markdown(f"### {get_text('momentum_indicators', lang)}")
                    indicators_to_show = ['RSI', 'MACD', 'Stochastic', 'Williams_R', 'ROC', 'CCI']
                    for ind in indicators_to_show:
                        if data['indicators'].get(ind):
                            value = data['indicators'][ind]
                            if isinstance(value, dict):
                                st.markdown(f"**{ind}:**")
                                for k, v in value.items():
                                    if v is not None:
                                        st.markdown(f"- {k}: {v:.2f}")
                            elif value is not None:
                                st.markdown(f"**{ind}:** {value:.2f}")
                
                with col3:
                    st.markdown(f"### {get_text('volume_indicators', lang)}")
                    volume_indicators = ['OBV', 'VWAP', 'MFI', 'CMF']
                    for ind in volume_indicators:
                        if data['indicators'].get(ind):
                            value = data['indicators'][ind]
                            if value is not None:
                                st.markdown(f"**{ind}:** {value:.2f}")
                    
                    st.markdown(f"### {get_text('pivot_points', lang)}")
                    if data['indicators'].get('Pivots'):
                        pivots = data['indicators']['Pivots']
                        if pivots.get('pivot'):
                            st.markdown(f"**Pivot:** ${pivots['pivot']:.2f}")
                        if pivots.get('r1') and pivots.get('r2'):
                            st.markdown(f"**{get_text('resistance', lang)}:** R1: ${pivots['r1']:.2f}, R2: ${pivots['r2']:.2f}")
                        if pivots.get('s1') and pivots.get('s2'):
                            st.markdown(f"**{get_text('support', lang)}:** S1: ${pivots['s1']:.2f}, S2: ${pivots['s2']:.2f}")
            else:
                st.info(get_text('no_indicators_calculated', lang))
        
        with tab4:
            st.markdown(f"## {get_text('tab_patterns', lang)}")
            
            if patterns_data and patterns_data.get('patterns'):
                display_candlestick_patterns(
                    patterns_data['patterns'],
                    patterns_data['statistics'],
                    lang
                )
            else:
                st.info(get_text('patterns_found', lang).lower() if lang == 'de' else get_text('patterns_found', lang).capitalize())
        
        with tab5:
            st.markdown(f"## {get_text('ai_analysis', lang)}")
            
            if st.session_state.use_llm and LLMClient is not None:
                try:
                    # LLM Client initialisieren
                    llm_client = LLMClient()
                    
                    # Verschiedene Analysen durchführen
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        with st.spinner(get_text('ai_thinking', lang)):
                            # Hauptanalyse
                            st.markdown(f"### {get_text('technical_analysis_ai', lang)}")
                            
                            # Füge Candlestick-Muster zur Analyse hinzu
                            df_data = pd.DataFrame(data['data'])
                            analysis_context = {
                                'ticker': data['ticker'],
                                'current_price': df_data['Close'].iloc[-1] if not df_data.empty else 0,
                                'price_change_1d': df_data['Close'].pct_change().iloc[-1] * 100 if not df_data.empty else 0,
                                'volume': df_data['Volume'].iloc[-1] if not df_data.empty else 0,
                                'sentiment': data.get('sentiment'),
                                'candlestick_patterns': patterns_data.get('statistics') if patterns_data else None,
                                'analysis_date': data.get('analysis_date', datetime.now().strftime('%Y-%m-%d')),
                                'data_date': df_data.index[-1].strftime('%Y-%m-%d') if not df_data.empty else 'N/A'
                            }
                            
                            main_analysis = llm_client.analyze_indicators(
                                data['indicators'],
                                analysis_context,
                                max_tokens=st.session_state.get('tokens_indicators', 1500),
                                language=lang
                            )
                            st.markdown(main_analysis)
                            
                            st.markdown("---")
                            
                            # Wahrscheinlichkeitsanalyse
                            if data.get('probabilities') and data.get('targets'):
                                st.markdown(f"### {get_text('scenario_analysis', lang)}")
                                prob_analysis = llm_client.analyze_probabilities(
                                    data['probabilities'],
                                    data['targets'],
                                    data['sentiment'][0] if data.get('sentiment') else "Neutral",
                                    max_tokens=st.session_state.get('tokens_probabilities', 1200),
                                    language=lang
                                )
                                st.markdown(prob_analysis)
                            
                            st.markdown("---")
                            
                            # Fibonacci & Support/Resistance
                            if data.get('fibonacci') or data.get('support_resistance'):
                                st.markdown(f"### {get_text('fibonacci_sr_analysis', lang)}")
                                fib_analysis = llm_client.analyze_fibonacci_support_resistance(
                                    data.get('fibonacci', {}),
                                    data.get('support_resistance', {}),
                                    max_tokens=st.session_state.get('tokens_fibonacci', 1800),
                                    language=lang
                                )
                                st.markdown(fib_analysis)
                            
                            st.markdown("---")
                            
                            # Umfassender Marktbericht generieren
                            st.markdown(f"### {get_text('market_report', lang)}")
                            
                            # Zeige aktuelle Token-Einstellung
                            current_max_tokens = st.session_state.get('max_tokens', 3000)
                            st.info(f"{get_text('max_tokens_for_reports', lang)}: {current_max_tokens}")
                            
                            if st.button(get_text('generate_report', lang)):
                                try:
                                    with st.spinner(get_text('generating_report', lang)):
                                        # Vollständige Analyse für Bericht vorbereiten
                                        df_data = pd.DataFrame(data['data'])
                                        full_analysis = {
                                            'ticker': data['ticker'],
                                            'data': data['data'],  # Vollständige Daten für Berechnungen
                                            'current_price': df_data['Close'].iloc[-1] if not df_data.empty else 0,
                                            'current_metrics': {
                                                'price': df_data['Close'].iloc[-1] if not df_data.empty else 0,
                                                'change_1d': df_data['Close'].pct_change().iloc[-1] * 100 if not df_data.empty else 0,
                                                'volume': df_data['Volume'].iloc[-1] if not df_data.empty else 0,
                                                'high': df_data['High'].iloc[-1] if not df_data.empty else 0,
                                                'low': df_data['Low'].iloc[-1] if not df_data.empty else 0
                                            },
                                            'indicators': data['indicators'],
                                            'fibonacci_levels': data.get('fibonacci'),  # Korrekter Key
                                            'support_resistance': data.get('support_resistance'),
                                            'probabilities': data.get('probabilities'),
                                            'price_targets': data.get('targets'),  # Korrekter Key
                                            'sentiment': data.get('sentiment'),
                                            'candlestick_patterns': patterns_data if patterns_data else None
                                        }
                                        
                                        # Übergebe max_tokens und language an die Funktion
                                        current_tokens = st.session_state.get('max_tokens', 5000)
                                        report = llm_client.generate_complete_report(
                                            full_analysis, 
                                            max_tokens=current_tokens,
                                            language=lang
                                        )
                                        
                                        # Bericht anzeigen
                                        st.markdown(report)
                                        
                                        # Speichere Bericht in Session State für Export
                                        st.session_state.generated_report = report
                                        st.session_state.report_ticker = data['ticker']
                                        
                                except Exception as e:
                                    st.error(f"Fehler bei der Berichterstellung: {str(e)}")
                            
                            # Export-Button wenn Bericht vorhanden
                            if 'generated_report' in st.session_state:
                                st.markdown("---")
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    st.download_button(
                                        label=f"💾 {get_text('download_report', lang)}",
                                        data=st.session_state.generated_report,
                                        file_name=f"{st.session_state.report_ticker}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                        mime="text/markdown",
                                        use_container_width=True
                                    )
                    
                    with col2:
                        st.markdown(f"### {get_text('ask_ai', lang)}")
                        user_question = st.text_area(
                            label="Frage eingeben",  # Füge ein Label hinzu
                            placeholder=get_text('question_placeholder', lang),
                            label_visibility="collapsed"  # Verstecke das Label
                        )
                        
                        if st.button(get_text('ask_question', lang)):
                            if user_question:
                                with st.spinner(get_text('ai_thinking', lang)):
                                    answer = llm_client.answer_question(
                                        user_question,
                                        {
                                            'indicators': data['indicators'],
                                            'probabilities': data.get('probabilities'),
                                            'targets': data.get('targets'),
                                            'sentiment': data.get('sentiment'),
                                            'patterns': patterns_data if patterns_data else None
                                        },
                                        max_tokens=st.session_state.get('tokens_questions', 800),
                                        language=lang
                                    )
                                    st.markdown(f"### {get_text('answer', lang)}:")
                                    st.markdown(answer)
                except Exception as e:
                    st.error(f"KI-Analyse Fehler: {str(e)}")
                    st.info("Stellen Sie sicher, dass das lokale LLM läuft (http://127.0.0.1:1234)")
            elif LLMClient is None:
                st.warning("LLM Client konnte nicht geladen werden. Bitte prüfen Sie die Installation.")
                st.info("Installieren Sie ggf. fehlende Abhängigkeiten mit: pip install openai httpx")
            else:
                st.info(get_text('ai_disabled', lang))
    else:
        # Zeige Willkommensnachricht wenn keine Daten vorhanden
        st.info(f"👈 {get_text('start_analysis', lang)}")
        st.markdown(f"""
        ### {get_text('welcome_title', lang)}
        
        {get_text('welcome_step1', lang)}
        {get_text('welcome_step2', lang)}
        {get_text('welcome_step3', lang)} **{get_text('start_analysis', lang)}**
        
        {get_text('welcome_features', lang)}
        - {get_text('welcome_feature1', lang)}
        - {get_text('welcome_feature2', lang)}
        - {get_text('welcome_feature3', lang)}
        - {get_text('welcome_feature4', lang)}
        - {get_text('welcome_feature5', lang)}
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #888;'>
        <p>{get_text('footer_version', lang)}</p>
        <p>{get_text('footer_disclaimer', lang)}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
