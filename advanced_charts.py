"""
Erweiterte Chart-Visualisierungen mit verbesserter Skalierbarkeit und Interaktivität
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class AdvancedCharts:
    """
    Klasse für erweiterte Chart-Visualisierungen mit verbesserter Skalierbarkeit
    """
    
    @staticmethod
    def _apply_scalable_layout(fig: go.Figure, title: str = "", height: int = 700) -> go.Figure:
        """
        Wendet skalierbare Layout-Einstellungen auf alle Charts an
        """
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=height,
            hovermode='x unified',
            
            # Skalierbare X-Achse
            xaxis=dict(
                rangeslider=dict(visible=False),
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="ALL")
                    ]),
                    bgcolor='rgba(0,0,0,0.3)',
                    activecolor='rgba(0,204,136,0.3)',
                ),
                type='date',
                fixedrange=False,  # Erlaubt Zoom auf X-Achse
            ),
            
            # Skalierbare Y-Achse
            yaxis=dict(
                fixedrange=False,  # Erlaubt Zoom auf Y-Achse
                autorange=True,
                side='right',
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
            ),
            
            # Drag-Modus für bessere Interaktion
            dragmode='zoom',  # Alternativ: 'pan'
            
            # Modebar mit allen Zoom-Optionen
            modebar=dict(
                orientation='v',
                bgcolor='rgba(0,0,0,0.5)',
                color='white',
                activecolor='#00CC88'
            ),
            
            # Erweiterte Interaktivität
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0.5)',
            ),
            
            # Margin für bessere Darstellung
            margin=dict(l=0, r=80, t=100, b=40),
        )
        
        # Zoom-Buttons Configuration
        fig.update_xaxes(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='rgba(128,128,128,0.5)',
            spikethickness=1,
        )
        
        fig.update_yaxes(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            spikecolor='rgba(128,128,128,0.5)',
            spikethickness=1,
        )
        
        return fig
    
    @staticmethod
    def create_main_chart_scalable(data: pd.DataFrame, indicators: Dict, 
                                   fibonacci_levels: Dict = None, 
                                   support_resistance: Dict = None,
                                   patterns: List[Dict] = None) -> go.Figure:
        """
        Erstellt einen Haupt-Chart mit allen Overlays und verbesserter Skalierbarkeit
        """
        # Erstelle Subplots für Preis und Volumen
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=['Preis & Indikatoren', 'Volumen', 'RSI & Momentum']
        )
        
        # Hauptchart - Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Preis',
                increasing=dict(line=dict(color='#00CC88')),
                decreasing=dict(line=dict(color='#FF4444')),
                hoverlabel=dict(namelength=-1)
            ),
            row=1, col=1
        )
        
        # Moving Averages mit verschiedenen Farben
        ma_colors = {
            9: 'rgba(255, 235, 59, 0.8)',   # Gelb
            21: 'rgba(33, 150, 243, 0.8)',   # Blau
            50: 'rgba(255, 152, 0, 0.8)',    # Orange
            200: 'rgba(156, 39, 176, 0.8)'   # Lila
        }
        
        for period, color in ma_colors.items():
            ma_col = f'EMA_{period}'
            if ma_col in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[ma_col],
                        name=f'EMA {period}',
                        line=dict(color=color, width=1.5),
                        hoverlabel=dict(namelength=-1)
                    ),
                    row=1, col=1
                )
        
        # Bollinger Bands
        if 'BB_upper' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_upper'],
                    name='BB Upper',
                    line=dict(color='rgba(128,128,128,0.3)', width=1),
                    hoverlabel=dict(namelength=-1)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['BB_lower'],
                    name='BB Lower',
                    line=dict(color='rgba(128,128,128,0.3)', width=1),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)',
                    hoverlabel=dict(namelength=-1)
                ),
                row=1, col=1
            )
        
        # Fibonacci Levels
        if fibonacci_levels:
            fib_colors = {
                '0.0%': 'rgba(255,0,0,0.5)',
                '23.6%': 'rgba(255,165,0,0.5)',
                '38.2%': 'rgba(255,255,0,0.5)',
                '50.0%': 'rgba(0,255,0,0.5)',
                '61.8%': 'rgba(0,255,255,0.5)',
                '100.0%': 'rgba(0,0,255,0.5)'
            }
            
            for level, price in fibonacci_levels.get('retracement', {}).items():
                color = fib_colors.get(level, 'rgba(128,128,128,0.5)')
                fig.add_hline(
                    y=price,
                    line_dash="dot",
                    line_color=color,
                    line_width=1,
                    annotation_text=f"Fib {level}: ${price:.2f}",
                    annotation_position="left",
                    row=1, col=1
                )
        
        # Support und Resistance
        if support_resistance:
            # Support Levels
            for i, support in enumerate(support_resistance.get('support', [])[:3]):
                fig.add_hline(
                    y=support,
                    line_dash="dash",
                    line_color='rgba(0,255,0,0.5)',
                    line_width=2,
                    annotation_text=f"Support {i+1}: ${support:.2f}",
                    annotation_position="right",
                    row=1, col=1
                )
            
            # Resistance Levels
            for i, resistance in enumerate(support_resistance.get('resistance', [])[:3]):
                fig.add_hline(
                    y=resistance,
                    line_dash="dash",
                    line_color='rgba(255,0,0,0.5)',
                    line_width=2,
                    annotation_text=f"Resistance {i+1}: ${resistance:.2f}",
                    annotation_position="right",
                    row=1, col=1
                )
        
        # Pattern Markierungen - ERWEITERT für alle Patterns
        if patterns:
            # Gruppiere Patterns nach Index um Überlappungen zu vermeiden
            pattern_groups = {}
            for pattern in patterns:
                idx = pattern.get('index', -1)
                if idx >= 0 and idx < len(data):
                    if idx not in pattern_groups:
                        pattern_groups[idx] = []
                    pattern_groups[idx].append(pattern)
            
            # Zeige die wichtigsten Patterns (max 20)
            sorted_indices = sorted(pattern_groups.keys())[-20:]
            
            for idx in sorted_indices:
                patterns_at_idx = pattern_groups[idx]
                
                # Wähle das wichtigste Pattern bei mehreren am gleichen Index
                # Priorität: Very High > High > Medium > Low reliability
                reliability_order = {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1}
                patterns_at_idx.sort(key=lambda p: reliability_order.get(p.get('reliability', 'Low'), 0), reverse=True)
                pattern = patterns_at_idx[0]  # Wichtigstes Pattern
                
                try:
                    # Bestimme Position und Farbe
                    pattern_date = data.index[idx]
                    price_high = data.loc[pattern_date, 'High']
                    price_low = data.loc[pattern_date, 'Low']
                    
                    # Farbe basierend auf Signal
                    signal = pattern.get('signal', '')
                    if 'Bullish' in signal:
                        color = '#00CC88'
                        y_pos = price_low * 0.995  # Unter der Kerze für bullische Signale
                        ay = 30
                    elif 'Bearish' in signal:
                        color = '#FF4444'
                        y_pos = price_high * 1.005  # Über der Kerze für bearische Signale
                        ay = -30
                    else:
                        color = '#FFD700'  # Gold für neutrale
                        y_pos = (price_high + price_low) / 2
                        ay = 0
                    
                    # Pattern Name kürzen für bessere Lesbarkeit
                    pattern_name = pattern['pattern']
                    if len(pattern_name) > 15:
                        # Kürze lange Namen ab
                        short_names = {
                            'Three White Soldiers': '3 White Sol.',
                            'Three Black Crows': '3 Black Crows',
                            'Three Inside Up': '3 Inside Up',
                            'Three Inside Down': '3 Inside Down',
                            'Three Outside Up': '3 Outside Up',
                            'Three Outside Down': '3 Outside Down',
                            'Rising Three Methods': 'Rising 3',
                            'Falling Three Methods': 'Falling 3',
                            'Bullish Engulfing': 'Bull Engulf',
                            'Bearish Engulfing': 'Bear Engulf',
                            'Morning Star': 'Morn. Star',
                            'Evening Star': 'Even. Star',
                            'Shooting Star': 'Shoot. Star',
                            'Inverted Hammer': 'Inv. Hammer',
                            'Hanging Man': 'Hang. Man',
                            'Dark Cloud Cover': 'Dark Cloud',
                            'Piercing Line': 'Pierc. Line',
                            'Bullish Harami': 'Bull Harami',
                            'Bearish Harami': 'Bear Harami',
                            'Tweezer Top': 'Tweez. Top',
                            'Tweezer Bottom': 'Tweez. Bot.',
                            'Bullish Marubozu': 'Bull Marubozu',
                            'Bearish Marubozu': 'Bear Marubozu',
                            'Long-Legged Doji': 'LL Doji',
                            'Dragonfly Doji': 'Dragon. Doji',
                            'Gravestone Doji': 'Grave. Doji',
                            'Spinning Top': 'Spin. Top'
                        }
                        pattern_name = short_names.get(pattern_name, pattern_name[:12] + '.')
                    
                    # Füge Reliability-Indikator hinzu
                    reliability = pattern.get('reliability', 'Medium')
                    if reliability == 'Very High':
                        marker = '⭐⭐⭐'
                    elif reliability == 'High':
                        marker = '⭐⭐'
                    elif reliability == 'Medium':
                        marker = '⭐'
                    else:
                        marker = ''
                    
                    # Erstelle Annotation
                    fig.add_annotation(
                        x=pattern_date,
                        y=y_pos,
                        text=f"{pattern_name} {marker}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=1.5,
                        arrowcolor=color,
                        ax=0,
                        ay=ay,
                        bgcolor=color,
                        bordercolor=color,
                        borderwidth=1,
                        opacity=0.9,
                        font=dict(color='white', size=9, family='Arial Black'),
                        row=1, col=1
                    )
                    
                    # Bei mehreren Patterns am gleichen Index, zeige Anzahl
                    if len(patterns_at_idx) > 1:
                        fig.add_annotation(
                            x=pattern_date,
                            y=y_pos,
                            text=f"+{len(patterns_at_idx)-1}",
                            showarrow=False,
                            bgcolor='rgba(255,255,255,0.2)',
                            font=dict(color='white', size=7),
                            xshift=35,
                            yshift=0,
                            row=1, col=1
                        )
                        
                except Exception as e:
                    print(f"Fehler beim Hinzufügen von Pattern {pattern.get('pattern', 'Unknown')}: {str(e)}")
                    continue
        
        # Volumen Chart
        colors = ['#FF4444' if row['Close'] < row['Open'] else '#00CC88' 
                  for idx, row in data.iterrows()]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volumen',
                marker_color=colors,
                opacity=0.7,
                hoverlabel=dict(namelength=-1)
            ),
            row=2, col=1
        )
        
        # Volumen Moving Average
        if 'Volume' in data.columns:
            vol_ma = data['Volume'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=vol_ma,
                    name='Vol MA(20)',
                    line=dict(color='rgba(255,255,255,0.5)', width=1),
                    hoverlabel=dict(namelength=-1)
                ),
                row=2, col=1
            )
        
        # RSI Chart
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI'],
                    name='RSI',
                    line=dict(color='rgba(255,165,0,0.8)', width=2),
                    hoverlabel=dict(namelength=-1)
                ),
                row=3, col=1
            )
            
            # RSI Überkauft/Überverkauft Linien
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         line_width=1, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         line_width=1, row=3, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                         line_width=1, row=3, col=1)
        
        # Layout mit verbesserter Skalierbarkeit
        fig.update_layout(
            title='Technische Analyse Dashboard - Vollständig Skalierbar',
            template='plotly_dark',
            height=900,
            hovermode='x unified',
            
            # Aktiviere Zoom und Pan
            dragmode='zoom',
            
            # Legende
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(0,0,0,0.5)',
                font=dict(size=10)
            ),
            
            # Margins
            margin=dict(l=0, r=100, t=80, b=40),
        )
        
        # X-Achsen Konfiguration für alle Subplots
        for i in range(1, 4):
            fig.update_xaxes(
                rangeslider_visible=False,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(step="all", label="ALL")
                    ]),
                    bgcolor='rgba(0,0,0,0.3)',
                    activecolor='rgba(0,204,136,0.3)',
                    x=0,
                    y=1.05
                ) if i == 1 else dict(),  # Nur beim ersten Subplot
                fixedrange=False,
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                row=i, col=1
            )
        
        # Y-Achsen Konfiguration für alle Subplots
        for i in range(1, 4):
            fig.update_yaxes(
                fixedrange=False,
                autorange=True,
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                showspikes=True,
                spikemode='across',
                spikesnap='cursor',
                row=i, col=1
            )
        
        # Spezielle Y-Achsen Titel
        fig.update_yaxes(title_text="Preis ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volumen", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1)
        
        # Interaktive Modebar Buttons
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': [
                'drawline',
                'drawopenpath',
                'drawclosedpath',
                'drawcircle',
                'drawrect',
                'eraseshape'
            ],
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'technical_analysis_chart',
                'height': 1080,
                'width': 1920,
                'scale': 1
            }
        }
        
        # Füge Config zum Figure Object hinzu
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"dragmode": "zoom"}],
                            label="Zoom",
                            method="relayout"
                        ),
                        dict(
                            args=[{"dragmode": "pan"}],
                            label="Pan",
                            method="relayout"
                        ),
                        dict(
                            args=[{"dragmode": "select"}],
                            label="Select",
                            method="relayout"
                        ),
                        dict(
                            args=[{"dragmode": "lasso"}],
                            label="Lasso",
                            method="relayout"
                        ),
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.0,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                ),
            ]
        )
        
        return fig
    
    @staticmethod
    def create_heikin_ashi_chart(data: pd.DataFrame, title: str = "Heikin Ashi Chart") -> go.Figure:
        """
        Erstellt einen Heikin Ashi Chart mit verbesserter Skalierbarkeit
        """
        ha_close = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4
        ha_open = [(data['Open'].iloc[0] + data['Close'].iloc[0]) / 2]
        
        for i in range(1, len(data)):
            ha_open.append((ha_open[i-1] + ha_close.iloc[i-1]) / 2)
        
        ha_high = pd.concat([pd.Series(ha_open), ha_close, data['High']], axis=1).max(axis=1)
        ha_low = pd.concat([pd.Series(ha_open), ha_close, data['Low']], axis=1).min(axis=1)
        
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=ha_open,
            high=ha_high,
            low=ha_low,
            close=ha_close,
            name='Heikin Ashi',
            increasing_line_color='#00CC88',
            decreasing_line_color='#FF4444'
        )])
        
        # Wende skalierbare Layout-Einstellungen an
        fig = AdvancedCharts._apply_scalable_layout(fig, title)
        
        return fig
    
    @staticmethod
    def create_renko_chart(data: pd.DataFrame, brick_size: float = None) -> go.Figure:
        """
        Erstellt einen Renko Chart
        """
        if brick_size is None:
            # Automatische Brick-Größe basierend auf ATR
            atr = data['High'].rolling(14).max() - data['Low'].rolling(14).min()
            brick_size = atr.mean() * 0.5
        
        prices = data['Close'].values
        renko_bricks = []
        current_price = prices[0]
        
        for price in prices[1:]:
            if abs(price - current_price) >= brick_size:
                num_bricks = int(abs(price - current_price) / brick_size)
                direction = 1 if price > current_price else -1
                
                for _ in range(num_bricks):
                    current_price += direction * brick_size
                    renko_bricks.append({
                        'price': current_price,
                        'direction': direction
                    })
        
        if not renko_bricks:
            return go.Figure()
        
        fig = go.Figure()
        
        for i, brick in enumerate(renko_bricks):
            color = '#00CC88' if brick['direction'] > 0 else '#FF4444'
            fig.add_trace(go.Bar(
                x=[i],
                y=[brick_size],
                base=brick['price'] - brick_size,
                marker_color=color,
                showlegend=False
            ))
        
        fig.update_layout(
            title='Renko Chart',
            template='plotly_dark',
            xaxis_title='Brick Number',
            yaxis_title='Price',
            height=600,
            bargap=0,
            dragmode='zoom',
            xaxis=dict(fixedrange=False),
            yaxis=dict(fixedrange=False)
        )
        
        return fig
    
    @staticmethod
    def create_point_and_figure_chart(data: pd.DataFrame, box_size: float = None, reversal: int = 3) -> go.Figure:
        """
        Erstellt einen Point & Figure Chart
        """
        if box_size is None:
            # Automatische Box-Größe
            price_range = data['High'].max() - data['Low'].min()
            box_size = price_range / 50
        
        prices = data['Close'].values
        pnf_data = []
        current_column = []
        current_direction = None
        current_price = prices[0]
        
        for price in prices[1:]:
            move = (price - current_price) / box_size
            
            if current_direction is None:
                current_direction = 1 if move > 0 else -1
                current_column = [current_price]
            
            if current_direction * move >= 1:
                # Fortsetzung in gleicher Richtung
                num_boxes = int(abs(move))
                for _ in range(num_boxes):
                    current_price += current_direction * box_size
                    current_column.append(current_price)
            elif current_direction * move <= -reversal:
                # Umkehr
                pnf_data.append({
                    'column': current_column,
                    'type': 'X' if current_direction > 0 else 'O'
                })
                current_direction *= -1
                current_column = [current_price]
                num_boxes = int(abs(move))
                for _ in range(num_boxes):
                    current_price += current_direction * box_size
                    current_column.append(current_price)
        
        # Letzte Spalte hinzufügen
        if current_column:
            pnf_data.append({
                'column': current_column,
                'type': 'X' if current_direction > 0 else 'O'
            })
        
        fig = go.Figure()
        
        for i, col_data in enumerate(pnf_data):
            symbol = col_data['type']
            color = '#00CC88' if symbol == 'X' else '#FF4444'
            
            for price in col_data['column']:
                fig.add_trace(go.Scatter(
                    x=[i],
                    y=[price],
                    mode='text',
                    text=[symbol],
                    textfont=dict(size=12, color=color),
                    showlegend=False
                ))
        
        fig.update_layout(
            title='Point & Figure Chart',
            template='plotly_dark',
            xaxis_title='Column',
            yaxis_title='Price',
            height=600,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#333', fixedrange=False),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#333', fixedrange=False),
            dragmode='zoom'
        )
        
        return fig
    
    @staticmethod
    def create_market_profile_chart(data: pd.DataFrame, bins: int = 30) -> go.Figure:
        """
        Erstellt ein Market Profile Chart mit verbesserter Skalierbarkeit
        """
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.7, 0.3],
            shared_yaxes=True,
            horizontal_spacing=0.01
        )
        
        # Hauptchart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing=dict(line=dict(color='#00CC88')),
                decreasing=dict(line=dict(color='#FF4444'))
            ),
            row=1, col=1
        )
        
        # Volume Profile berechnen
        price_min = data['Low'].min()
        price_max = data['High'].max()
        price_bins = np.linspace(price_min, price_max, bins)
        volume_profile = np.zeros(bins - 1)
        
        for idx, row in data.iterrows():
            for i in range(len(price_bins) - 1):
                if price_bins[i] <= row['Low'] <= price_bins[i+1] or \
                   price_bins[i] <= row['High'] <= price_bins[i+1] or \
                   (row['Low'] <= price_bins[i] and row['High'] >= price_bins[i+1]):
                    volume_profile[i] += row['Volume']
        
        # Volume Profile hinzufügen
        fig.add_trace(
            go.Bar(
                x=volume_profile,
                y=(price_bins[:-1] + price_bins[1:]) / 2,
                orientation='h',
                name='Volume Profile',
                marker_color='rgba(0, 204, 136, 0.5)',
                hoverlabel=dict(namelength=-1)
            ),
            row=1, col=2
        )
        
        # Point of Control (POC)
        poc_idx = np.argmax(volume_profile)
        poc_price = (price_bins[poc_idx] + price_bins[poc_idx + 1]) / 2
        
        fig.add_hline(
            y=poc_price,
            line_dash="dash",
            line_color="yellow",
            annotation_text=f"POC: ${poc_price:.2f}",
            annotation_position="left",
            row=1, col=1
        )
        
        # Value Area (70% des Volumens)
        total_volume = volume_profile.sum()
        value_area_volume = total_volume * 0.7
        sorted_indices = np.argsort(volume_profile)[::-1]
        
        cumulative_volume = 0
        value_area_indices = []
        for idx in sorted_indices:
            cumulative_volume += volume_profile[idx]
            value_area_indices.append(idx)
            if cumulative_volume >= value_area_volume:
                break
        
        if value_area_indices:
            value_area_high = max([(price_bins[i] + price_bins[i+1])/2 for i in value_area_indices])
            value_area_low = min([(price_bins[i] + price_bins[i+1])/2 for i in value_area_indices])
            
            # Value Area markieren
            fig.add_hrect(
                y0=value_area_low,
                y1=value_area_high,
                fillcolor="rgba(100, 100, 100, 0.2)",
                layer="below",
                line_width=0,
                annotation_text="Value Area",
                annotation_position="top left",
                row=1, col=1
            )
        
        # Layout mit Skalierbarkeit
        fig.update_layout(
            title='Market Profile Analysis - Interaktiv & Skalierbar',
            template='plotly_dark',
            height=700,
            showlegend=True,
            hovermode='y unified',
            dragmode='zoom',
            
            # X-Achse skalierbar machen
            xaxis=dict(
                fixedrange=False,
                showspikes=True,
                spikemode='across',
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label="7D", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(step="all", label="ALL")
                    ]),
                    bgcolor='rgba(0,0,0,0.3)',
                    activecolor='rgba(0,204,136,0.3)',
                )
            ),
            
            # Y-Achse skalierbar
            yaxis=dict(
                fixedrange=False,
                showspikes=True,
                spikemode='across',
                title="Preis ($)"
            ),
            
            # Volume Profile Achse
            xaxis2=dict(
                fixedrange=False,
                title="Volumen"
            ),
            
            # Gemeinsame Y-Achse
            yaxis2=dict(
                fixedrange=False,
                showticklabels=False
            )
        )
        
        return fig
    
    @staticmethod
    def create_ichimoku_cloud(data: pd.DataFrame) -> go.Figure:
        """
        Erstellt einen Ichimoku Cloud Chart
        """
        # Ichimoku Berechnungen
        high_9 = data['High'].rolling(window=9).max()
        low_9 = data['Low'].rolling(window=9).min()
        tenkan_sen = (high_9 + low_9) / 2  # Conversion Line
        
        high_26 = data['High'].rolling(window=26).max()
        low_26 = data['Low'].rolling(window=26).min()
        kijun_sen = (high_26 + low_26) / 2  # Base Line
        
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)  # Leading Span A
        
        high_52 = data['High'].rolling(window=52).max()
        low_52 = data['Low'].rolling(window=52).min()
        senkou_span_b = ((high_52 + low_52) / 2).shift(26)  # Leading Span B
        
        chikou_span = data['Close'].shift(-26)  # Lagging Span
        
        fig = go.Figure()
        
        # Preis
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ))
        
        # Tenkan-sen
        fig.add_trace(go.Scatter(
            x=data.index,
            y=tenkan_sen,
            line=dict(color='blue', width=1),
            name='Tenkan-sen (Conversion)'
        ))
        
        # Kijun-sen
        fig.add_trace(go.Scatter(
            x=data.index,
            y=kijun_sen,
            line=dict(color='red', width=1),
            name='Kijun-sen (Base)'
        ))
        
        # Chikou Span
        fig.add_trace(go.Scatter(
            x=data.index,
            y=chikou_span,
            line=dict(color='green', width=1),
            name='Chikou Span (Lagging)'
        ))
        
        # Kumo (Cloud)
        fig.add_trace(go.Scatter(
            x=data.index,
            y=senkou_span_a,
            line=dict(color='rgba(0,250,0,0)'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=senkou_span_b,
            line=dict(color='rgba(250,0,0,0)'),
            fill='tonexty',
            fillcolor='rgba(100,100,100,0.3)',
            name='Kumo (Cloud)'
        ))
        
        # Skalierbare Layout-Einstellungen
        fig = AdvancedCharts._apply_scalable_layout(fig, 'Ichimoku Cloud Analysis')
        
        return fig
    
    @staticmethod
    def create_harmonic_pattern_chart(data: pd.DataFrame) -> go.Figure:
        """
        Erstellt einen Chart mit harmonischen Mustern (Gartley, Butterfly, etc.)
        """
        fig = go.Figure()
        
        # Basis Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ))
        
        # Vereinfachte Harmonic Pattern Detection
        prices = data['Close'].values
        
        # Finde Swing Points
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(prices) - 2):
            if prices[i] > max(prices[i-2:i]) and prices[i] > max(prices[i+1:i+3]):
                swing_highs.append((i, prices[i]))
            elif prices[i] < min(prices[i-2:i]) and prices[i] < min(prices[i+1:i+3]):
                swing_lows.append((i, prices[i]))
        
        # Beispiel: Zeichne potenzielle AB=CD Muster
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Nehme die letzten Swing Points
            A = swing_lows[-2] if swing_lows else None
            B = swing_highs[-2] if swing_highs else None
            C = swing_lows[-1] if swing_lows else None
            D = swing_highs[-1] if swing_highs else None
            
            if A and B and C and D:
                # Zeichne das Muster
                pattern_x = [data.index[A[0]], data.index[B[0]], data.index[C[0]], data.index[D[0]]]
                pattern_y = [A[1], B[1], C[1], D[1]]
                
                fig.add_trace(go.Scatter(
                    x=pattern_x,
                    y=pattern_y,
                    mode='lines+markers',
                    line=dict(color='yellow', width=2, dash='dash'),
                    marker=dict(size=10, color='yellow'),
                    name='Harmonic Pattern'
                ))
                
                # Fibonacci Retracements für das Muster
                ab_range = B[1] - A[1]
                bc_retracement = (B[1] - C[1]) / ab_range if ab_range != 0 else 0
                
                fig.add_annotation(
                    x=data.index[C[0]],
                    y=C[1],
                    text=f"BC Retracement: {bc_retracement:.1%}",
                    showarrow=True,
                    arrowhead=2
                )
        
        # Skalierbare Layout-Einstellungen
        fig = AdvancedCharts._apply_scalable_layout(fig, 'Harmonic Pattern Analysis')
        
        return fig
    
    @staticmethod
    def create_multi_timeframe_chart(ticker_symbol: str, timeframes: List[str] = ['1d', '1wk', '1mo']) -> go.Figure:
        """
        Erstellt einen Multi-Timeframe Chart
        """
        import yfinance as yf
        
        fig = make_subplots(
            rows=len(timeframes), cols=1,
            shared_xaxes=False,
            vertical_spacing=0.05,
            subplot_titles=[f'{tf} Timeframe' for tf in timeframes]
        )
        
        for i, tf in enumerate(timeframes, 1):
            # Lade Daten für jeden Timeframe
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period='1y', interval=tf)
            
            if not data.empty:
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name=f'{tf} Chart',
                        showlegend=False
                    ),
                    row=i, col=1
                )
                
                # Füge SMA hinzu
                sma_20 = data['Close'].rolling(window=20).mean()
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=sma_20,
                        line=dict(color='orange', width=1),
                        name=f'SMA 20 ({tf})',
                        showlegend=False
                    ),
                    row=i, col=1
                )
        
        fig.update_layout(
            title='Multi-Timeframe Analysis',
            template='plotly_dark',
            height=900,
            showlegend=False,
            dragmode='zoom'
        )
        
        # Update x-axes - alle skalierbar machen
        for i in range(1, len(timeframes) + 1):
            fig.update_xaxes(rangeslider_visible=False, fixedrange=False, row=i, col=1)
            fig.update_yaxes(fixedrange=False, row=i, col=1)
        
        return fig
    
    @staticmethod
    def create_advanced_indicator_dashboard(data: pd.DataFrame, indicators: Dict) -> go.Figure:
        """
        Erstellt ein erweitertes Dashboard mit mehreren Indikatoren
        """
        fig = make_subplots(
            rows=4, cols=2,
            shared_xaxes=True,
            subplot_titles=(
                'MACD', 'Stochastic',
                'MFI', 'Williams %R',
                'ADX', 'CCI',
                'OBV', 'CMF'
            ),
            vertical_spacing=0.05,
            horizontal_spacing=0.05
        )
        
        # MACD
        if 'MACD' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], 
                                    name='MACD', line=dict(color='blue')), 
                         row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], 
                                    name='Signal', line=dict(color='red')), 
                         row=1, col=1)
            fig.add_trace(go.Bar(x=data.index, y=data['MACD_diff'], 
                                name='Histogram', marker_color='gray'), 
                         row=1, col=1)
        
        # Stochastic
        if 'Stoch_K' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['Stoch_K'], 
                                    name='%K', line=dict(color='orange')), 
                         row=1, col=2)
            fig.add_trace(go.Scatter(x=data.index, y=data['Stoch_D'], 
                                    name='%D', line=dict(color='purple')), 
                         row=1, col=2)
            fig.add_hline(y=80, line_dash="dash", line_color="red", 
                         row=1, col=2)
            fig.add_hline(y=20, line_dash="dash", line_color="green", 
                         row=1, col=2)
        
        # MFI
        if 'MFI' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['MFI'], 
                                    name='MFI', line=dict(color='green')), 
                         row=2, col=1)
            fig.add_hline(y=80, line_dash="dash", line_color="red", 
                         row=2, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", 
                         row=2, col=1)
        
        # Williams %R
        if 'Williams_R' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['Williams_R'], 
                                    name='Williams %R', line=dict(color='cyan')), 
                         row=2, col=2)
            fig.add_hline(y=-20, line_dash="dash", line_color="red", 
                         row=2, col=2)
            fig.add_hline(y=-80, line_dash="dash", line_color="green", 
                         row=2, col=2)
        
        # ADX
        if 'ADX' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['ADX'], 
                                    name='ADX', line=dict(color='yellow')), 
                         row=3, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['ADX_pos'], 
                                    name='+DI', line=dict(color='green')), 
                         row=3, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['ADX_neg'], 
                                    name='-DI', line=dict(color='red')), 
                         row=3, col=1)
            fig.add_hline(y=25, line_dash="dash", line_color="gray", 
                         row=3, col=1)
        
        # CCI
        if 'CCI' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['CCI'], 
                                    name='CCI', line=dict(color='magenta')), 
                         row=3, col=2)
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                         row=3, col=2)
            fig.add_hline(y=-100, line_dash="dash", line_color="green", 
                         row=3, col=2)
        
        # OBV
        if 'OBV' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['OBV'], 
                                    name='OBV', line=dict(color='brown')), 
                         row=4, col=1)
        
        # CMF
        if 'CMF' in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data['CMF'], 
                                    name='CMF', line=dict(color='pink')), 
                         row=4, col=2)
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         row=4, col=2)
        
        # Layout mit Skalierbarkeit für alle Subplots
        fig.update_layout(
            title='Advanced Indicators Dashboard - Vollständig Interaktiv',
            template='plotly_dark',
            height=1200,
            showlegend=False,
            hovermode='x unified',
            dragmode='zoom'
        )
        
        # Mache alle Achsen skalierbar
        fig.update_xaxes(fixedrange=False, showspikes=True, spikemode='across')
        fig.update_yaxes(fixedrange=False, showspikes=True, spikemode='across')
        
        # Füge Range Selector nur zur untersten X-Achse hinzu
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="7D", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(step="all", label="ALL")
                ]),
                bgcolor='rgba(0,0,0,0.3)',
                activecolor='rgba(0,204,136,0.3)',
            ),
            row=4, col=1
        )
        
        return fig
    
    @staticmethod
    def create_correlation_heatmap(data: pd.DataFrame) -> go.Figure:
        """
        Erstellt eine Korrelations-Heatmap der Indikatoren
        """
        # Wähle nur numerische Spalten
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Füge Indikatoren hinzu wenn vorhanden
        indicator_cols = ['RSI', 'MACD', 'ATR', 'ADX', 'CCI', 'MFI', 'OBV']
        for col in indicator_cols:
            if col in data.columns:
                numeric_cols.append(col)
        
        # Berechne Korrelation
        corr_data = data[numeric_cols].corr()
        
        # Erstelle Heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_data.values,
            x=corr_data.columns,
            y=corr_data.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_data.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Korrelation")
        ))
        
        fig.update_layout(
            title='Korrelations-Matrix der Indikatoren',
            template='plotly_dark',
            height=600,
            width=800,
            xaxis=dict(tickangle=45),
            yaxis=dict(autorange='reversed')
        )
        
        return fig
    
    @staticmethod
    def create_performance_chart(data: pd.DataFrame) -> go.Figure:
        """
        Erstellt einen Performance-Chart mit Returns
        """
        # Berechne Returns
        data['Daily_Return'] = data['Close'].pct_change() * 100
        data['Cumulative_Return'] = (1 + data['Daily_Return'] / 100).cumprod()
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=['Kumulative Performance', 'Tägliche Returns'],
            row_heights=[0.7, 0.3]
        )
        
        # Kumulative Returns
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=(data['Cumulative_Return'] - 1) * 100,
                name='Kumulative Returns',
                line=dict(color='#00CC88', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,204,136,0.2)'
            ),
            row=1, col=1
        )
        
        # Tägliche Returns als Bar Chart
        colors = ['#FF4444' if r < 0 else '#00CC88' for r in data['Daily_Return']]
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Daily_Return'],
                name='Tägliche Returns',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title='Performance Analyse',
            template='plotly_dark',
            height=700,
            showlegend=False,
            hovermode='x unified',
            dragmode='zoom'
        )
        
        # Achsen skalierbar machen
        fig.update_xaxes(
            fixedrange=False,
            showspikes=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="ALL")
                ])
            ),
            row=2, col=1
        )
        
        fig.update_yaxes(
            fixedrange=False,
            showspikes=True,
            title_text="Returns (%)",
            row=1, col=1
        )
        
        fig.update_yaxes(
            fixedrange=False,
            showspikes=True,
            title_text="Daily Return (%)",
            row=2, col=1
        )
        
        return fig
