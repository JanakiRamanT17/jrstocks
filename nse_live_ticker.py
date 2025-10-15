# =============================================================================
# REAL-TIME NSE INDIA LIVE DATA TICKER - PROPER FIXED VERSION
# =============================================================================

# Install required packages
!pip install pandas numpy requests beautifulsoup4 plotly yfinance --quiet

import pandas as pd
import numpy as np
import requests
import json
import time
import datetime
from IPython.display import display, clear_output, HTML
import warnings
import yfinance as yf
warnings.filterwarnings('ignore')

print("✅ Libraries imported successfully!")

# =============================================================================
# REAL NSE INDIA DATA FETCHER - PROPER REAL-TIME IMPLEMENTATION
# =============================================================================

class NseLiveTicker:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Watchlist with proper symbol mapping
        self.watchlist = {
            'NIFTY 50': {'type': 'index', 'symbol': 'NIFTY 50'},
            'NIFTY BANK': {'type': 'index', 'symbol': 'NIFTY BANK'}, 
            'RELIANCE': {'type': 'stock', 'symbol': 'RELIANCE', 'yf': 'RELIANCE.NS'},
            'TCS': {'type': 'stock', 'symbol': 'TCS', 'yf': 'TCS.NS'},
            'INFOSYS': {'type': 'stock', 'symbol': 'INFOSYS', 'yf': 'INFY.NS'},
            'HDFC BANK': {'type': 'stock', 'symbol': 'HDFCBANK', 'yf': 'HDFCBANK.NS'},
            'ICICI BANK': {'type': 'stock', 'symbol': 'ICICIBANK', 'yf': 'ICICIBANK.NS'},
            'SBIN': {'type': 'stock', 'symbol': 'SBIN', 'yf': 'SBIN.NS'},
            'BHARTI AIRTEL': {'type': 'stock', 'symbol': 'BHARTIARTL', 'yf': 'BHARTIARTL.NS'},
            'ITC': {'type': 'stock', 'symbol': 'ITC', 'yf': 'ITC.NS'}
        }
        
        self.market_data = {}
        self.update_count = 0
        self.cookies_set = False
        
    def set_cookies(self):
        """Set cookies by visiting NSE homepage"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.cookies_set = True
                return True
        except Exception as e:
            print(f"❌ Failed to set cookies: {e}")
        return False
    
    def get_nse_index_data(self, index_name):
        """Get real-time NSE index data"""
        try:
            if not self.cookies_set:
                self.set_cookies()
                
            url = f"{self.base_url}/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                index_data = data['data'][0]
                return {
                    'current': float(index_data['lastPrice']),
                    'change': float(index_data['change']),
                    'change_pct': float(index_data['pChange']),
                    'high': float(index_data['dayHigh']),
                    'low': float(index_data['dayLow']),
                    'open': float(index_data['open']),
                    'previous_close': float(index_data['previousClose']),
                    'volume': float(index_data.get('totalTradedVolume', 0)),
                    'source': 'NSE LIVE'
                }
        except Exception as e:
            print(f"❌ NSE Index API error for {index_name}: {e}")
        return None
    
    def get_nse_stock_data(self, symbol):
        """Get real-time NSE stock data"""
        try:
            if not self.cookies_set:
                self.set_cookies()
                
            url = f"{self.base_url}/api/quote-equity?symbol={symbol}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if 'priceInfo' in data:
                price_info = data['priceInfo']
                return {
                    'current': float(price_info['lastPrice']),
                    'change': float(price_info['change']),
                    'change_pct': float(price_info['pChange']),
                    'high': float(price_info['intraDayHighLow']['max']),
                    'low': float(price_info['intraDayHighLow']['min']),
                    'open': float(price_info['open']),
                    'previous_close': float(price_info['previousClose']),
                    'volume': int(price_info['totalTradedVolume']),
                    'source': 'NSE LIVE'
                }
        except Exception as e:
            print(f"❌ NSE Stock API error for {symbol}: {e}")
        return None
    
    def get_yahoo_data(self, symbol):
        """Get Yahoo Finance data as fallback - REAL DATA ONLY"""
        try:
            # Download 1-minute data for near real-time
            data = yf.download(symbol, period='1d', interval='1m', progress=False)
            
            if data.empty or len(data) < 2:
                return None
            
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            return {
                'current': float(current_price),
                'change': float(change),
                'change_pct': float(change_pct),
                'high': float(data['High'].iloc[-1]),
                'low': float(data['Low'].iloc[-1]),
                'open': float(data['Open'].iloc[-1]),
                'previous_close': float(prev_price),
                'volume': int(data['Volume'].iloc[-1]),
                'source': 'YAHOO 1M'
            }
        except Exception as e:
            print(f"❌ Yahoo Finance error for {symbol}: {e}")
        return None
    
    def get_all_data(self):
        """Fetch all market data with proper fallback"""
        successful_fetches = 0
        
        for display_name, info in self.watchlist.items():
            data = None
            
            # Try NSE API first
            if info['type'] == 'index':
                data = self.get_nse_index_data(info['symbol'])
            else:
                data = self.get_nse_stock_data(info['symbol'])
            
            # If NSE fails, try Yahoo Finance
            if not data and 'yf' in info:
                data = self.get_yahoo_data(info['yf'])
            
            if data:
                self.market_data[display_name] = data
                successful_fetches += 1
            else:
                print(f"⚠️ All data sources failed for {display_name}")
        
        self.update_count += 1
        self.last_update_time = datetime.datetime.now()
        
        return successful_fetches > 0

# =============================================================================
# LIVE TICKER DISPLAY - COMPLETE VERSION
# =============================================================================

class NseLiveTickerDisplay:
    def __init__(self):
        self.nse_ticker = NseLiveTicker()
        
    def create_dashboard(self):
        """Create complete real-time dashboard"""
        real_data_available = self.nse_ticker.get_all_data()
        
        # Header
        header_html = f"""
        <div style='
            background: linear-gradient(135deg, #1e3d6d, #2c5282);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            font-family: Arial, sans-serif;
        '>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div>
                    <h1 style='margin: 0; font-size: 28px; color: #ffd700;'>
                        🇮🇳 NSE INDIA LIVE TICKER
                    </h1>
                    <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>
                        📍 Real-time data from nseindia.com | 🕒 {self.nse_ticker.last_update_time.strftime("%Y-%m-%d %H:%M:%S")}
                    </p>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 16px; font-weight: bold;'>
                        🔄 Update #{self.nse_ticker.update_count}
                    </div>
                    <div style='font-size: 14px; opacity: 0.9;'>
                        {'🟢 LIVE DATA' if real_data_available else '🟡 FALLBACK DATA'}
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Ticker Tape
        ticker_items = []
        for stock, data in self.nse_ticker.market_data.items():
            color = "#90EE90" if data['change'] >= 0 else "#FF6B6B"
            arrow = "▲" if data['change'] >= 0 else "▼"
            source_icon = "🟢" if data['source'] == 'NSE LIVE' else "🟡"
            
            ticker_items.append(f"""
            <span style='margin: 0 25px; font-family: Arial, sans-serif; white-space: nowrap;'>
                {source_icon} <strong>{stock}</strong>
                <span style='color: white;'> ₹{data['current']:,.2f}</span>
                <span style='color: {color}; font-weight: bold;'> {arrow} {data['change']:+.2f}</span>
                <span style='color: {color};'>({data['change_pct']:+.2f}%)</span>
            </span>
            """)
        
        if not ticker_items:
            ticker_items = ["<span style='color: white;'>🔴 No data available - Retrying...</span>"]
        
        ticker_content = "".join(ticker_items)
        ticker_content_double = ticker_content + ticker_content
        
        ticker_html = f"""
        <div style='
            background: #152642;
            color: white;
            padding: 15px 0;
            border-bottom: 3px solid #ff9933;
            font-family: Arial, sans-serif;
            overflow: hidden;
            position: relative;
        '>
            <div style='
                display: inline-block;
                white-space: nowrap;
                animation: ticker-scroll 40s linear infinite;
                padding-left: 100%;
            '>
                {ticker_content_double}
            </div>
        </div>
        
        <style>
        @keyframes ticker-scroll {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-100%); }}
        }}
        </style>
        """
        
        # Market Overview
        gainers = sum(1 for data in self.nse_ticker.market_data.values() if data['change'] > 0)
        losers = sum(1 for data in self.nse_ticker.market_data.values() if data['change'] < 0)
        live_feeds = sum(1 for data in self.nse_ticker.market_data.values() if data['source'] == 'NSE LIVE')
        
        overview_html = f"""
        <div style='
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 5px solid #28a745;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div>
                    <h3 style='margin: 0; color: #1e3d6d;'>
                        📊 LIVE MARKET OVERVIEW
                    </h3>
                    <p style='margin: 5px 0; color: #666; font-size: 12px;'>
                        Real-time market data with automatic fallback
                    </p>
                </div>
                <div style='display: flex; gap: 25px; text-align: center;'>
                    <div>
                        <div style='color: #28a745; font-size: 24px; font-weight: bold;'>{gainers}</div>
                        <div style='color: #666; font-size: 12px; font-weight: bold;'>GAINERS</div>
                    </div>
                    <div>
                        <div style='color: #dc3545; font-size: 24px; font-weight: bold;'>{losers}</div>
                        <div style='color: #666; font-size: 12px; font-weight: bold;'>LOSERS</div>
                    </div>
                    <div>
                        <div style='color: #1e3d6d; font-size: 24px; font-weight: bold;'>{live_feeds}</div>
                        <div style='color: #666; font-size: 12px; font-weight: bold;'>LIVE FEEDS</div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Stock Grid
        stock_grid_html = """
        <div style='
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
            font-family: Arial, sans-serif;
        '>
        """
        
        for stock, data in self.nse_ticker.market_data.items():
            bg_color = "#d4edda" if data['change'] >= 0 else "#f8d7da"
            text_color = "#155724" if data['change'] >= 0 else "#721c24"
            border_color = "#c3e6cb" if data['change'] >= 0 else "#f5c6cb"
            arrow = "▲" if data['change'] >= 0 else "▼"
            source_badge = "🟢 LIVE" if data['source'] == 'NSE LIVE' else "🟡 YAHOO"
            badge_color = "#28a745" if data['source'] == 'NSE LIVE' else "#ffc107"
            
            stock_grid_html += f"""
            <div style='
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            '>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <div style='font-weight: bold; color: #1e3d6d; font-size: 16px;'>
                            {stock}
                        </div>
                        <div style='font-size: 22px; font-weight: bold; color: {text_color}; margin: 5px 0;'>
                            ₹{data['current']:,.2f}
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 11px; background: {badge_color}; color: white; padding: 3px 8px; border-radius: 10px;'>
                            {source_badge}
                        </div>
                        <div style='color: {text_color}; font-weight: bold; font-size: 14px; margin-top: 5px;'>
                            {arrow} {data['change']:+.2f} ({data['change_pct']:+.2f}%)
                        </div>
                    </div>
                </div>
                <div style='font-size: 11px; color: {text_color}; margin-top: 8px;'>
                    <div>High: ₹{data['high']:,.2f} | Low: ₹{data['low']:,.2f}</div>
                    <div>Open: ₹{data['open']:,.2f} | Volume: {data['volume']:,}</div>
                </div>
            </div>
            """
        
        stock_grid_html += "</div>"
        
        # Footer
        next_update = datetime.datetime.now() + datetime.timedelta(seconds=15)
        footer_html = f"""
        <div style='
            background: #1e3d6d;
            color: white;
            padding: 15px;
            border-radius: 0 0 10px 10px;
            text-align: center;
            font-family: Arial, sans-serif;
            border-top: 2px solid #ff9933;
        '>
            <div style='display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;'>
                <div style='font-size: 14px;'>
                    ⚡ <strong>REAL-TIME NSE DATA</strong>
                </div>
                <div style='font-size: 13px;'>
                    🔄 Next update: {next_update.strftime('%H:%M:%S')}
                </div>
                <div style='font-size: 12px; opacity: 0.9;'>
                    📍 Source: nseindia.com + yahoo finance
                </div>
            </div>
        </div>
        """
        
        return header_html + ticker_html + overview_html + stock_grid_html + footer_html
    
    def run_continuous_updates(self, interval=15):
        """Run continuous real-time updates"""
        print("🚀 STARTING REAL-TIME NSE INDIA TICKER")
        print("📍 Data Sources: NSE Live → Yahoo Finance 1-minute")
        print(f"🔄 Updates every {interval} seconds")
        print("🟢 Green = NSE Live Data | 🟡 Yellow = Yahoo Finance")
        print("=" * 70)
        
        while True:
            try:
                clear_output(wait=True)
                display(HTML(self.create_dashboard()))
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n🛑 Ticker stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in update cycle: {e}")
                print("🔄 Retrying in 10 seconds...")
                time.sleep(10)

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def start_nse_live_ticker():
    """Start the real NSE live ticker"""
    ticker_display = NseLiveTickerDisplay()
    ticker_display.run_continuous_updates(interval=15)

def test_nse_connection():
    """Test NSE connection with single update"""
    ticker_display = NseLiveTickerDisplay()
    
    print("🧪 TESTING NSE INDIA CONNECTION...")
    print("=" * 50)
    
    clear_output(wait=True)
    display(HTML(ticker_display.create_dashboard()))
    
    print(f"\n✅ NSE Ticker Ready!")
    print(f"📊 Stocks Loaded: {len(ticker_display.nse_ticker.market_data)}")
    print("💡 Run 'start_nse_live_ticker()' for continuous updates")

# =============================================================================
# RUN THE TICKER
# =============================================================================

if __name__ == "__main__":
    # Test connection first
    test_nse_connection()
    
    # Uncomment the line below to start continuous real-time updates
    #start_nse_live_ticker()
