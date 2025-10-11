# NSE India Live Ticker

Real-time stock market data directly from NSE India.

## Features
- Real-time NSE data
- Live scrolling ticker
- Auto-updating every 15 seconds
- Fallback system for reliability

## Quick Start
```python
from nse_live_ticker import test_nse_connection, start_nse_live_ticker

# Test connection
test_nse_connection()

# Start live updates
start_nse_live_ticker()
