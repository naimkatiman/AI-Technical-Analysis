# AI-Powered Technical Stock Analysis Dashboard

A Streamlit-based financial dashboard that combines technical analysis with AI-powered insights using Claude 3.5 Sonnet.

## Features

- 📈 Interactive stock data visualization with candlestick charts
- 📊 Multiple technical indicators (SMA, EMA, Bollinger Bands, VWAP)
- 🤖 AI-powered trading recommendations using Claude 3.5 Sonnet
- 🔄 Real-time data fetching using yFinance
- 📱 Responsive design with Streamlit

## Installation

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Use the sidebar to:
   - Enter a stock ticker (e.g., AAPL)
   - Select date range
   - Choose technical indicators
   - Click "Fetch Data" to load stock information

3. Click "Run AI Analysis" to get Claude's recommendation based on the chart

## Technical Indicators

- **SMA (Simple Moving Average)**: 20-day period
- **EMA (Exponential Moving Average)**: 20-day period
- **Bollinger Bands**: 20-day period with 2 standard deviations
- **VWAP (Volume Weighted Average Price)**: Calculated daily

## AI Analysis

The dashboard uses Claude 3.5 Sonnet to analyze charts and provide trading recommendations. The AI considers:
- Candlestick patterns
- Technical indicator signals
- Price trends and momentum

## Important Notes

- This tool is for educational purposes only
- AI recommendations should not be used as sole trading signals
- Always conduct your own research and risk assessment
- Keep your API keys secure

## Dependencies

- yfinance==0.2.40
- streamlit
- pandas
- plotly
- anthropic
- python-dotenv

## License

MIT License
