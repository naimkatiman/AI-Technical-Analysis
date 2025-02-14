import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import json
import tempfile
import base64
import os
import io
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize API key
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    st.error("Please set your DEEPSEEK_API_KEY in the .env file")
    st.stop()

# Set up Streamlit app
st.set_page_config(layout="wide")
st.title("AI-Powered Technical Stock Analysis Dashboard")
st.sidebar.header("Configuration")

# Input for stock ticker and date range
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-14"))

# Fetch stock data
if st.sidebar.button("Fetch Data"):
    st.session_state["stock_data"] = yf.download(ticker, start=start_date, end=end_date)
    # Only drop level if we have multi-level columns
    if isinstance(st.session_state["stock_data"].columns, pd.MultiIndex):
        st.session_state["stock_data"].columns = st.session_state["stock_data"].columns.droplevel(1)
    st.success("Stock data loaded successfully!")

# Check if data is available
if "stock_data" in st.session_state:
    data = st.session_state["stock_data"]

    # Plot candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlestick"
        )
    ])

    # Sidebar: Select technical indicators
    st.sidebar.subheader("Technical Indicators")
    indicators = st.sidebar.multiselect(
        "Select Indicators:",
        ["20-Day SMA", "20-Day EMA", "20-Day Bollinger Bands", "VWAP"],
        default=["20-Day SMA"]
    )

    # Helper function to add indicators to the chart
    def add_indicator(indicator):
        if indicator == "20-Day SMA":
            sma = data['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=sma, mode='lines', name='SMA (20)'))
        elif indicator == "20-Day EMA":
            ema = data['Close'].ewm(span=20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='EMA (20)'))
        elif indicator == "20-Day Bollinger Bands":
            sma = data['Close'].rolling(window=20).mean()
            std = data['Close'].rolling(window=20).std()
            bb_upper = sma + 2 * std
            bb_lower = sma - 2 * std
            fig.add_trace(go.Scatter(x=data.index, y=bb_upper, mode='lines', name='BB Upper'))
            fig.add_trace(go.Scatter(x=data.index, y=bb_lower, mode='lines', name='BB Lower'))
        elif indicator == "VWAP":
            data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
            fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name='VWAP'))

    # Add selected indicators to the chart
    for indicator in indicators:
        add_indicator(indicator)

    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

    # Analyze chart with Deepseek
    st.subheader("AI-Powered Analysis")
    if st.button("Run AI Analysis"):
        logging.debug("Run AI Analysis button clicked")
        try:
            with st.spinner("Analyzing the data, please wait..."):
                logging.debug("Inside spinner context")
                try:
                    # Convert DataFrame to CSV string
                    logging.debug("Converting DataFrame to CSV")
                    csv_data = data.to_csv(index=True)  # Include the index (dates)

                    # Prepare the message for Deepseek
                    logging.debug("Sending request to Deepseek API")

                    url = "https://api.deepseek.com/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    data_payload = {
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert Stock Market Technical Analyst."
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Analyze the following historical stock data for {ticker} from {start_date} to {end_date}.\n\n"
                                    "The data is provided in CSV format with the following columns: Date, Open, High, Low, Close, Adj Close, Volume.\n\n"
                                    "Focus on:\n"
                                    "1. Trend Analysis: Identify the primary and secondary trends\n"
                                    "2. Technical Indicators: Consider the provided data and common indicator calculations (SMA, EMA, etc.)\n"
                                    "3. Price Patterns: Identify any significant patterns\n"
                                    "4. Support/Resistance: Note key price levels\n\n"
                                    "Provide:\n"
                                    "1. A clear BUY, HOLD, or SELL recommendation\n"
                                    "2. Your confidence level (High/Medium/Low)\n"
                                    "3. A concise explanation of your reasoning\n"
                                    "4. Key risk factors to consider\n\n"
                                    "Here is the data:\n\n"
                                    f"{csv_data}"
                                )
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 4000
                    }

                    # Log request details (excluding sensitive data)
                    logging.debug(f"Making request to URL: {url}")
                    safe_headers = headers.copy()
                    safe_headers["Authorization"] = "REDACTED"
                    logging.debug(f"Request headers (excluding Authorization): {safe_headers}")

                    try:
                        # Make the API request with a timeout
                        response = requests.post(url, headers=headers, json=data_payload, timeout=60)

                        # Log and display response details
                        logging.debug(f"HTTP Status Code: {response.status_code}")
                        logging.debug(f"Response Headers: {response.headers}")
                        logging.debug(f"Raw Response Content: {response.text}")

                        with st.expander("Debug Information"):
                            st.write(f"HTTP Status Code: {response.status_code}")
                            st.write("Response Headers:")
                            st.json(dict(response.headers))
                            st.write("Raw Response Content:")
                            st.code(response.text)

                        # Handle the response based on status code
                        if response.status_code == 200:
                            try:
                                # Check for empty response
                                if not response.text.strip():
                                    error_msg = "API returned an empty response."
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                # Attempt to parse JSON
                                json_response = response.json()

                                # Check for expected keys in the response
                                if not json_response:
                                    error_msg = "Empty JSON response"
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                if 'choices' not in json_response:
                                    error_msg = "No 'choices' in response"
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                if not json_response['choices']:
                                    error_msg = "Empty choices array"
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                choice = json_response['choices'][0]
                                if 'message' not in choice:
                                    error_msg = "No 'message' in choice"
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                if 'content' not in choice['message']:
                                    error_msg = "No 'content' in message"
                                    logging.error(error_msg)
                                    st.error(error_msg)
                                    raise ValueError(error_msg)

                                # Display the analysis
                                st.markdown(choice['message']['content'])
                                logging.debug("Successfully displayed analysis")

                            except json.JSONDecodeError as e:
                                error_msg = f"JSON parsing error: {e}. See raw response in debug information."
                                logging.error(error_msg)
                                st.error(error_msg)

                        else:
                            error_msg = f"API call failed with status code: {response.status_code}. See debug information."
                            logging.error(error_msg)
                            st.error(error_msg)

                    except requests.exceptions.Timeout as e:
                        error_msg = f"API request timed out: {e}"
                        logging.exception(error_msg)
                        st.error(error_msg)
                    except requests.exceptions.RequestException as e:
                        error_msg = f"Request error: {e}"
                        logging.exception(error_msg)
                        st.error(error_msg)

                except Exception as e:
                    error_msg = f"Error during API call: {str(e)}"
                    logging.exception(error_msg)
                    st.error(error_msg)
        except Exception as outer_e:
            error_msg = f"Outer error: {str(outer_e)}"
            logging.exception(error_msg)
            st.error(error_msg)
