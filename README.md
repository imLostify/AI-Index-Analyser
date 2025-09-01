# 🚀 Advanced Index Analyzer with AI

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Status](https://img.shields.io/badge/status-Beta-yellow)

A professional-grade financial analysis tool that combines advanced technical analysis with AI-powered insights for comprehensive market analysis.

## ✨ Features

### 📊 Technical Analysis
- **30+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages (EMA/SMA), ATR, ADX, Stochastic, Williams %R, CCI, MFI, OBV, CMF, and more
- **Fibonacci Analysis**: Automatic calculation of retracement and extension levels
- **Support & Resistance**: Dynamic identification of key price levels
- **Pivot Points**: Classic, Fibonacci, and Camarilla pivot calculations
- **VWAP**: Volume Weighted Average Price with real-time updates

### 🕯️ Candlestick Pattern Recognition
- **45+ Patterns**: Comprehensive detection of classic candlestick patterns
- **Pattern Categories**:
  - Single Candle: Doji, Hammer, Shooting Star, Marubozu
  - Two Candle: Engulfing, Harami, Piercing Line, Dark Cloud Cover
  - Three Candle: Morning/Evening Star, Three White Soldiers/Black Crows
  - Complex: Rising/Falling Three Methods
- **Reliability Rating**: Each pattern rated from Low to Very High reliability
- **Visual Markers**: Color-coded pattern annotations directly on charts

### 📈 Advanced Charting
- **Interactive Charts**: Fully scalable and zoomable Plotly charts
- **Multiple Timeframes**: Support for 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo intervals
- **Gap-Free Display**: Clean candlestick charts without weekend/holiday gaps
- **Custom Date Ranges**: Flexible period selection with calendar widgets
- **Multi-Panel Layout**: Separate panels for price, volume, and indicators

### 🤖 AI-Powered Analysis
- **LLM Integration**: Compatible with local LLMs (LM Studio, Ollama, etc.)
- **Intelligent Reports**: Comprehensive market reports with trading recommendations
- **Scenario Analysis**: Probability-weighted market scenarios
- **Natural Language Q&A**: Ask questions about the analysis in plain language
- **Customizable Parameters**: Adjustable creativity and token limits

### 🌐 Multi-Language Support
- **Deutsch**: Vollständige deutsche Übersetzung
- **English**: Complete English translation
- **Dynamic Switching**: Change language on-the-fly without restart

### 💾 Data Management
- **Settings Persistence**: Save and load your preferred settings
- **Export Options**: Download reports as Markdown files
- **Popular Indices**: Quick access to major indices (S&P 500, NASDAQ, DAX, etc.)
- **Custom Symbols**: Analyze any ticker symbol from Yahoo Finance

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Local LLM server for AI features

### Step 1: Clone the Repository
```bash
git clone [repository-url]
cd yfinance+llm-index-analyser
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure LLM (Optional)
For AI features, set up a local LLM server:

1. **Using LM Studio** (Recommended):
   - Download from: https://lmstudio.ai/
   - Load a model (e.g., Mistral, Llama, etc.)
   - Start the server on port 1234

2. **Using Ollama**:
   ```bash
   ollama serve
   ollama pull mistral
   ```

3. **Update config.py** if using different settings:
   ```python
   LLM_API_BASE = "http://127.0.0.1:1234/v1"
   LLM_MODEL = "your-model-name"
   ```

## 🎮 Usage

### Starting the Application
```bash
# Windows
python main.py
# or
streamlit run main.py

# Linux/Mac
python3 main.py
# or
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

### Basic Workflow

1. **Select Index or Symbol**:
   - Choose from popular indices (S&P 500, NASDAQ, DAX, etc.)
   - Or enter a custom ticker symbol

2. **Configure Time Period**:
   - Select date range using calendar widgets
   - Choose interval (1 minute to 1 month)
   - Enable/disable VWAP display

3. **Run Analysis**:
   - Click "🔍 Start Analysis" button
   - Wait for data loading and calculation

4. **Explore Results**:
   - **Overview Tab**: Key metrics and probabilities
   - **Charts Tab**: Interactive price and indicator charts
   - **Indicators Tab**: Detailed indicator values
   - **Patterns Tab**: Detected candlestick patterns
   - **AI Analysis Tab**: LLM-generated insights and reports

### Understanding the Charts

#### Candlestick Patterns
- **Green (🟢)**: Bullish patterns - potential buy signals
- **Red (🔴)**: Bearish patterns - potential sell signals
- **Yellow (🟡)**: Neutral patterns - market indecision

#### Reliability Indicators
- **⭐⭐⭐ or *****: Very High reliability
- **⭐⭐ or ****: High reliability
- **⭐ or ***: Medium reliability
- **(no star)**: Low reliability

#### Pattern Abbreviations
- **Ham**: Hammer
- **B.Eng**: Bullish/Bearish Engulfing
- **M.Star**: Morning Star
- **E.Star**: Evening Star
- **3WS**: Three White Soldiers
- **3BC**: Three Black Crows
- **Doji**: Doji patterns
- **Spin**: Spinning Top

## 📁 Project Structure

```
yfinance+llm-index-analyser/
│
├── main.py                 # Main Streamlit application
├── analysis.py            # Technical analysis engine
├── candlestick_patterns.py # Pattern recognition module
├── advanced_charts.py     # Advanced charting functions
├── llm_client.py         # LLM integration client
├── config.py             # Configuration settings
├── translations.py       # Multi-language support
├── utils.py             # Utility functions
├── export_utils.py      # Export functionality
│
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── LICENSE            # License information
│
└── user_settings.json  # Saved user preferences (auto-generated)
```

## ⚙️ Configuration

### config.py Settings
```python
# LLM Configuration
LLM_API_BASE = "http://127.0.0.1:1234/v1"
LLM_MODEL = "local-model"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 5000

# Chart Settings
CHART_COLORS = {
    'bullish': '#00CC88',
    'bearish': '#FF4444',
    'neutral': '#FFD700'
}

# Popular Indices
POPULAR_INDICES = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'DAX': '^GDAXI',
    ...
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Error loading data"**
   - Check internet connection
   - Verify ticker symbol is valid
   - Try a different time period

2. **AI Analysis Not Working**
   - Ensure LLM server is running
   - Check port 1234 is accessible
   - Verify model is loaded in LM Studio/Ollama

3. **Charts Not Displaying**
   - Clear browser cache
   - Try a different browser
   - Check for JavaScript errors in console

4. **Slow Performance**
   - Reduce token limit for AI analysis
   - Use larger intervals (daily instead of minute)
   - Close other applications

### Debug Mode
Enable debug output by setting in config.py:
```python
DEBUG_MODE = True
```

## 🤝 Contributing

This project is currently in beta. For bug reports or feature requests, please contact the development team through the official GitHub repository.

## 📄 License

This software is proprietary and licensed for non-commercial testing purposes only. See LICENSE file for details.

## 🙏 Acknowledgments

- **yfinance**: For reliable market data access
- **Streamlit**: For the amazing web framework
- **Plotly**: For interactive charting capabilities
- **TA-Lib**: For technical analysis calculations
- **OpenAI API**: For LLM integration standards

## 📞 Support

For support, please refer to the official GitHub repository or contact the development team.

---

**Disclaimer**: This tool is for informational purposes only and does not constitute investment advice. Always do your own research and consult with qualified financial advisors before making investment decisions.

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: Beta Testing