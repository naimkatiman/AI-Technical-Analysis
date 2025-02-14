# Standalone script to generate and encode chart
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64
import io

# Fetch data
data = yf.download("AAPL", start="2023-01-01", end="2024-12-14")

# Create chart
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])

# Save to buffer
img_bytes = io.BytesIO()
fig.write_image(img_bytes, format='png')
img_bytes.seek(0)
image_b64 = base64.b64encode(img_bytes.read()).decode('utf-8')

print(f"Base64 Image Data: {image_b64[:30]}...[truncated]...{image_b64[-30:]}") 