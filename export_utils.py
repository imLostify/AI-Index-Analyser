"""
Export-Funktionen für Analyseberichte
Erstellt PDF, Excel und HTML Exports
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from typing import Dict, Any, Optional
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import xlsxwriter

class ReportExporter:
    """
    Klasse zum Exportieren von Analyseberichten in verschiedene Formate
    """
    
    def __init__(self, analysis_data: Dict, language: str = 'de'):
        """
        Initialisiert den Report Exporter
        
        Args:
            analysis_data: Vollständige Analysedaten
            language: Sprache für den Bericht ('de' oder 'en')
        """
        self.data = analysis_data
        self.language = language
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def export_to_excel(self, filename: Optional[str] = None) -> str:
        """
        Exportiert die Analyse nach Excel
        """
        if filename is None:
            filename = f"{self.data['ticker']}_analysis_{self.timestamp}.xlsx"
        
        # Excel Writer erstellen
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formatierungen definieren
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#1e3c72',
                'font_color': 'white',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%',
                'border': 1
            })
            
            # 1. Übersichtsblatt
            overview_data = {
                'Metric': ['Current Price', 'Daily Change', 'Volume', 'RSI', 'Market Sentiment'],
                'Value': [
                    self.data.get('current_price', 'N/A'),
                    self.data.get('daily_change', 'N/A'),
                    self.data.get('volume', 'N/A'),
                    self.data.get('indicators', {}).get('RSI', 'N/A'),
                    self.data.get('sentiment', ['N/A'])[0] if self.data.get('sentiment') else 'N/A'
                ]
            }
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Overview', index=False)
            
            # 2. Kursdaten
            if 'data' in self.data:
                price_df = pd.DataFrame(self.data['data'])
                price_df.to_excel(writer, sheet_name='Price Data')
            
            # 3. Technische Indikatoren
            if 'indicators' in self.data:
                indicators_list = []
                for key, value in self.data['indicators'].items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            indicators_list.append({
                                'Indicator': f"{key} - {sub_key}",
                                'Value': sub_value
                            })
                    else:
                        indicators_list.append({
                            'Indicator': key,
                            'Value': value
                        })
                
                indicators_df = pd.DataFrame(indicators_list)
                indicators_df.to_excel(writer, sheet_name='Indicators', index=False)
            
            # 4. Wahrscheinlichkeiten
            if 'probabilities' in self.data:
                prob_df = pd.DataFrame([self.data['probabilities']])
                prob_df.to_excel(writer, sheet_name='Probabilities', index=False)
            
            # 5. Kursziele
            if 'targets' in self.data:
                bullish_df = pd.DataFrame(self.data['targets'].get('bullish', []))
                bearish_df = pd.DataFrame(self.data['targets'].get('bearish', []))
                
                if not bullish_df.empty:
                    bullish_df.to_excel(writer, sheet_name='Bullish Targets', index=False)
                if not bearish_df.empty:
                    bearish_df.to_excel(writer, sheet_name='Bearish Targets', index=False)
            
            # 6. Candlestick Patterns
            if 'patterns' in self.data:
                patterns_df = pd.DataFrame(self.data['patterns'])
                if not patterns_df.empty:
                    patterns_df.to_excel(writer, sheet_name='Candlestick Patterns', index=False)
            
            # Formatierung anpassen
            for sheet in writer.sheets.values():
                sheet.set_column('A:Z', 15)
        
        return filename
    
    def export_to_html(self, filename: Optional[str] = None) -> str:
        """
        Exportiert die Analyse als interaktive HTML-Datei
        """
        if filename is None:
            filename = f"{self.data['ticker']}_analysis_{self.timestamp}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="{self.language}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.data['ticker']} Analysis Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    padding: 30px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                    margin-top: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .bullish {{
                    color: #27ae60;
                    font-weight: bold;
                }}
                .bearish {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .timestamp {{
                    text-align: right;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📈 {self.data['ticker']} Technical Analysis Report</h1>
                <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>📊 Overview</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">${self.data.get('current_price', 'N/A')}</div>
                        <div class="metric-label">Current Price</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{self.data.get('daily_change', 'N/A')}%</div>
                        <div class="metric-label">Daily Change</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{self.data.get('indicators', {}).get('RSI', 'N/A')}</div>
                        <div class="metric-label">RSI</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{self.data.get('sentiment', ['N/A'])[0] if self.data.get('sentiment') else 'N/A'}</div>
                        <div class="metric-label">Market Sentiment</div>
                    </div>
                </div>
                
                <h2>🎯 Probabilities</h2>
                <table>
                    <tr>
                        <th>Scenario</th>
                        <th>Probability</th>
                        <th>Signals</th>
                    </tr>
                    <tr>
                        <td class="bullish">Bullish</td>
                        <td>{self.data.get('probabilities', {}).get('bullish_probability', 'N/A')}%</td>
                        <td>{self.data.get('probabilities', {}).get('bullish_signals', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td class="bearish">Bearish</td>
                        <td>{self.data.get('probabilities', {}).get('bearish_probability', 'N/A')}%</td>
                        <td>{self.data.get('probabilities', {}).get('bearish_signals', 'N/A')}</td>
                    </tr>
                </table>
                
                <h2>📍 Price Targets</h2>
                <h3>Bullish Targets</h3>
                <table>
                    <tr>
                        <th>Level</th>
                        <th>Price</th>
                        <th>Distance</th>
                    </tr>
        """
        
        # Bullische Ziele hinzufügen
        if 'targets' in self.data and 'bullish' in self.data['targets']:
            for target in self.data['targets']['bullish'][:5]:
                html_content += f"""
                    <tr>
                        <td>{target.get('level', 'N/A')}</td>
                        <td>${target.get('price', 'N/A')}</td>
                        <td class="bullish">+{target.get('distance', 'N/A')}%</td>
                    </tr>
                """
        
        html_content += """
                </table>
                
                <h3>Bearish Targets</h3>
                <table>
                    <tr>
                        <th>Level</th>
                        <th>Price</th>
                        <th>Distance</th>
                    </tr>
        """
        
        # Bearische Ziele hinzufügen
        if 'targets' in self.data and 'bearish' in self.data['targets']:
            for target in self.data['targets']['bearish'][:5]:
                html_content += f"""
                    <tr>
                        <td>{target.get('level', 'N/A')}</td>
                        <td>${target.get('price', 'N/A')}</td>
                        <td class="bearish">{target.get('distance', 'N/A')}%</td>
                    </tr>
                """
        
        html_content += """
                </table>
                
                <h2>🕯️ Candlestick Patterns</h2>
        """
        
        if 'patterns' in self.data and self.data['patterns']:
            html_content += """
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Pattern</th>
                        <th>Signal</th>
                        <th>Reliability</th>
                    </tr>
            """
            
            for pattern in self.data['patterns'][-10:]:  # Letzte 10 Muster
                signal_class = 'bullish' if 'Bullish' in pattern.get('signal', '') else 'bearish' if 'Bearish' in pattern.get('signal', '') else ''
                html_content += f"""
                    <tr>
                        <td>{pattern.get('date', 'N/A')}</td>
                        <td>{pattern.get('pattern', 'N/A')}</td>
                        <td class="{signal_class}">{pattern.get('signal', 'N/A')}</td>
                        <td>{pattern.get('reliability', 'N/A')}</td>
                    </tr>
                """
            
            html_content += "</table>"
        else:
            html_content += "<p>No patterns detected</p>"
        
        html_content += """
                <div class="timestamp">
                    <p>Report generated by Advanced Index Analyser with AI</p>
                    <p>Disclaimer: This analysis is for informational purposes only and does not constitute investment advice.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # HTML-Datei speichern
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Exportiert die Analyse als JSON
        """
        if filename is None:
            filename = f"{self.data['ticker']}_analysis_{self.timestamp}.json"
        
        # Konvertiere alle numpy/pandas Objekte zu nativen Python-Typen
        export_data = self._convert_to_serializable(self.data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def _convert_to_serializable(self, obj: Any) -> Any:
        """
        Konvertiert Objekte in JSON-serialisierbare Formate
        """
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_to_serializable(item) for item in obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        else:
            return obj