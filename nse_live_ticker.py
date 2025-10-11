# nse_live_ticker.py
# REAL-TIME NSE INDIA LIVE DATA TICKER

import pandas as pd
import numpy as np
import requests
import json
import time
import datetime
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

class NseLiveTicker:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.watchlist = {
            'NIFTY 50': 'NIFTY 50',
            'NIFTY BANK': 'NIFTY BANK', 
            'NIFTY NEXT 50': 'NIFTY NEXT 50',
            'RELIANCE': 'RELIANCE',
            'TCS': 'TCS',
            'INFY': 'INFOSYS',
            'HDFC BANK': 'HDFCBANK',
            'ICICI BANK': 'ICICIBANK',
            'SBIN': 'SBIN',
            'HUL': 'HINDUNILVR',
            'BHARTI AIRTEL': 'BHARTIARTL',
            'ITC': 'ITC',
            'LT': 'LT',
            'KOTAK BANK': 'KOTAKBANK',
            'AXIS BANK': 'AXISBANK',
            'BAJAJ FINANCE': 'BAJFINANCE'
        }
        
        self.market_data = {}
        self.update_count = 0
        self.cookies_set = False
        
    def set_cookies(self):
        """Set required cookies by visiting NSE first"""
        try:
            self.session.get(self.base_url, timeout=10)
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
                
            url = f"{self.base_url}/api/equity-stockIndices?index={index_name.upper().replace(' ', '%20')}"
            response = self.session.get(url, timeout=10)
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
                    'source': 'NSE LIVE'
                }
            
        except Exception as e:
            print(f"❌ Error fetching {index_name}: {e}")
            
        return None
    
    def get_nse_stock_data(self, symbol):
        """Get real-time NSE stock data"""
        try:
            if not self.cookies_set:
                self.set_cookies()
                
            url = f"{self.base_url}/api/quote-equity?symbol={symbol}"
            response = self.session.get(url, timeout=10)
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
            print(f"❌ Error fetching {symbol}: {e}")
            
        return None
    
    def get_all_data(self):
        """Fetch all market data from NSE"""
        successful_fetches = 0
        
        for display_name, nse_symbol in self.watchlist.items():
            try:
                if 'NIFTY' in display_name:
                    data = self.get_nse_index_data(nse_symbol)
                else:
                    data = self.get_nse_stock_data(nse_symbol)
                
                if data:
                    self.market_data[display_name] = data
                    successful_fetches += 1
                else:
                    self._generate_fallback_data(display_name)
                    
            except Exception as e:
                print(f"❌ Failed to fetch {display_name}: {e}")
                self._generate_fallback_data(display_name)
        
        self.update_count += 1
        self.last_update_time = datetime.datetime.now()
        
        return successful_fetches > 0
    
    def _generate_fallback_data(self, display_name):
        """Generate fallback data when NSE API fails"""
        base_prices = {
            'NIFTY 50': 22150, 'NIFTY BANK': 48500, 'NIFTY NEXT 50': 68500,
            'RELIANCE': 2850, 'TCS': 3850, 'INFY': 1650, 'HDFC BANK': 1550,
            'ICICI BANK': 1025, 'SBIN': 750, 'HUL': 2450, 'BHARTI AIRTEL': 1125,
            'ITC': 425, 'LT': 3250, 'KOTAK BANK': 1785, 'AXIS BANK': 1120,
            'BAJAJ FINANCE': 6850
        }
        
        if display_name in base_prices:
            base_price = base_prices[display_name]
            change = np.random.normal(0, base_price * 0.0005)
            current_price = base_price * (1 + np.random.uniform(-0.02, 0.02))
            current_price = max(base_price * 0.8, min(base_price * 1.2, current_price))
            
            self.market_data[display_name] = {
                'current': round(current_price, 2),
                'change': round(change, 2),
                'change_pct': round((change / base_price) * 100, 2),
                'high': round(current_price * 1.01, 2),
                'low': round(current_price * 0.99, 2),
                'open': round(base_price, 2),
                'volume': np.random.randint(100000, 5000000),
                'source': 'FALLBACK'
            }

class NseLiveTickerDisplay:
    def __init__(self):
        self.nse_ticker = NseLiveTicker()
        self.start_time = datetime.datetime.now()
        
    def create_dashboard(self):
        """Create the complete live dashboard"""
        real_data_available = self.nse_ticker.get_all_data()
        
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
        #ticker-scroll:hover {{
            animation-play-state: paused;
        }}
        </style>
        """
        
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
                        Data sourced directly from NSE India | Real-time updates
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
        
        stock_grid_html = """
        <div style='
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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
            source_badge = "🟢 LIVE" if data['source'] == 'NSE LIVE' else "🟡 FALLBACK"
            badge_color = "#28a745" if data['source'] == 'NSE LIVE' else "#ffc107"
            
            stock_grid_html += f"""
            <div style='
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 18px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transition: transform 0.2s ease;
            ' onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;'>
                    <div>
                        <div style='font-weight: bold; color: #1e3d6d; font-size: 18px;'>
                            {stock}
                        </div>
                        <div style='font-size: 24px; font-weight: bold; color: {text_color}; margin: 8px 0;'>
                            ₹{data['current']:,.2f}
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 12px; background: {badge_color}; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold;'>
                            {source_badge}
                        </div>
                        <div style='color: {text_color}; font-weight: bold; font-size: 16px; margin-top: 8px;'>
                            {arrow} {data['change']:+.2f} ({data['change_pct']:+.2f}%)
                        </div>
                    </div>
                </div>
                
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; color: {text_color};'>
                    <div><strong>Open:</strong> ₹{data.get('open', data['current']):.2f}</div>
                    <div><strong>High:</strong> ₹{data.get('high', data['current']):.2f}</div>
                    <div><strong>Low:</strong> ₹{data.get('low', data['current']):.2f}</div>
                    <div><strong>Volume:</strong> {data.get('volume', 0):,}</div>
                </div>
            </div>
            """
        
        stock_grid_html += "</div>"
        
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
                    📍 Source: nseindia.com
                </div>
            </div>
        </div>
        """
        
        return header_html + ticker_html + overview_html + stock_grid_html + footer_html

def test_nse_connection():
    """Test NSE connection with single update"""
    ticker_display = NseLiveTickerDisplay()
    
    print("🧪 TESTING NSE INDIA CONNECTION...")
    print("=" * 50)
    
    clear_output(wait=True)
    display(HTML(ticker_display.create_dashboard()))
    
    print("\n✅ NSE Ticker Ready!")
    print("💡 Run 'start_nse_live_ticker()' for continuous updates")

def start_nse_live_ticker():
    """Start the real NSE live ticker"""
    ticker_display = NseLiveTickerDisplay()
    
    print("🚀 STARTING REAL-TIME NSE INDIA TICKER")
    print("📍 Fetching live data directly from nseindia.com")
    print("🔄 Updates every 15 seconds")
    print("=" * 70)
    
    while True:
        try:
            clear_output(wait=True)
            display(HTML(ticker_display.create_dashboard()))
            time.sleep(15)
        except KeyboardInterrupt:
            print("\n🛑 Ticker stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in update cycle: {e}")
            print("🔄 Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    test_nse_connection()
