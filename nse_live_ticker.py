# =============================================================================
# ULTIMATE NSE LIVE TICKER - COMBINED & IMPROVED
# =============================================================================

# Install required packages
!pip install yfinance pandas numpy requests beautifulsoup4 plotly --quiet

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import time
import datetime
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

print("🚀 ULTIMATE NSE LIVE TICKER STARTING...")
print("📍 Combining Yahoo Finance + NSE India APIs")
print("🔄 Real-time updates with fallback system")
print("=" * 70)

class UltimateNseTicker:
    def __init__(self):
        # Yahoo Finance tickers (for fallback)
        self.yf_tickers = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'LT.NS',
            'KOTAKBANK.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'MARUTI.NS', 'TATAMOTORS.NS'
        ]
        
        # NSE India direct API symbols
        self.nse_symbols = {
            'NIFTY 50': 'NIFTY 50',
            'NIFTY BANK': 'NIFTY BANK',
            'RELIANCE': 'RELIANCE',
            'TCS': 'TCS',
            'HDFC BANK': 'HDFCBANK',
            'ICICI BANK': 'ICICIBANK',
            'INFOSYS': 'INFOSYS',
            'SBIN': 'SBIN',
            'BHARTI AIRTEL': 'BHARTIARTL'
        }
        
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.market_data = {}
        self.update_count = 0
        self.data_source = "INITIALIZING"
        
    def get_nse_live_data(self):
        """Get real-time data directly from NSE India"""
        try:
            # Set cookies first
            self.session.get(self.base_url, timeout=10)
            
            successful_fetches = 0
            for display_name, symbol in self.nse_symbols.items():
                try:
                    if 'NIFTY' in display_name:
                        # Index data
                        url = f"{self.base_url}/api/equity-stockIndices?index={symbol.replace(' ', '%20')}"
                    else:
                        # Stock data
                        url = f"{self.base_url}/api/quote-equity?symbol={symbol}"
                    
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'NIFTY' in display_name and 'data' in data and len(data['data']) > 0:
                        index_data = data['data'][0]
                        self.market_data[display_name] = {
                            'current': float(index_data['lastPrice']),
                            'change': float(index_data['change']),
                            'change_pct': float(index_data['pChange']),
                            'source': 'NSE LIVE'
                        }
                        successful_fetches += 1
                        
                    elif 'priceInfo' in data:
                        price_info = data['priceInfo']
                        self.market_data[display_name] = {
                            'current': float(price_info['lastPrice']),
                            'change': float(price_info['change']),
                            'change_pct': float(price_info['pChange']),
                            'source': 'NSE LIVE'
                        }
                        successful_fetches += 1
                        
                except Exception as e:
                    continue
            
            if successful_fetches > 0:
                self.data_source = "NSE LIVE"
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def get_yahoo_fallback_data(self):
        """Get data from Yahoo Finance as fallback"""
        try:
            # Add indices to Yahoo Finance tickers
            all_tickers = self.yf_tickers + ['^NSEI', '^NSEBANK']
            
            data = yf.download(tickers=all_tickers, period="1d", interval="1m", progress=False)
            
            if data.empty or len(data) < 2:
                return False
            
            last_close = data['Close'].iloc[-1]
            previous_close = data['Close'].iloc[-2]
            changes = ((last_close - previous_close) / previous_close) * 100
            
            # Map Yahoo symbols to display names
            symbol_map = {
                '^NSEI': 'NIFTY 50', '^NSEBANK': 'NIFTY BANK',
                'RELIANCE.NS': 'RELIANCE', 'TCS.NS': 'TCS', 
                'HDFCBANK.NS': 'HDFC BANK', 'ICICIBANK.NS': 'ICICI BANK',
                'INFY.NS': 'INFOSYS', 'SBIN.NS': 'SBIN', 
                'BHARTIARTL.NS': 'BHARTI AIRTEL'
            }
            
            for ticker in last_close.index:
                if ticker in symbol_map:
                    display_name = symbol_map[ticker]
                    self.market_data[display_name] = {
                        'current': round(float(last_close[ticker]), 2),
                        'change': round(float(last_close[ticker] - previous_close[ticker]), 2),
                        'change_pct': round(float(changes[ticker]), 2),
                        'source': 'YAHOO FINANCE'
                    }
            
            self.data_source = "YAHOO FINANCE"
            return True
            
        except Exception as e:
            return False
    
    def get_simulated_data(self):
        """Generate simulated data as last resort"""
        base_prices = {
            'NIFTY 50': 22150, 'NIFTY BANK': 48500,
            'RELIANCE': 2850, 'TCS': 3850, 'HDFC BANK': 1550,
            'ICICI BANK': 1025, 'INFOSYS': 1650, 'SBIN': 750,
            'BHARTI AIRTEL': 1125
        }
        
        for name, base_price in base_prices.items():
            change = np.random.normal(0, base_price * 0.001)
            current_price = base_price + change
            
            self.market_data[name] = {
                'current': round(current_price, 2),
                'change': round(change, 2),
                'change_pct': round((change / base_price) * 100, 2),
                'source': 'SIMULATED'
            }
        
        self.data_source = "SIMULATED"
        return True
    
    def fetch_all_data(self):
        """Fetch data with fallback system"""
        # Try NSE Live first
        if self.get_nse_live_data():
            status = "🟢 NSE LIVE DATA"
        # Fallback to Yahoo Finance
        elif self.get_yahoo_fallback_data():
            status = "🟡 YAHOO FINANCE"
        # Last resort: Simulated data
        else:
            self.get_simulated_data()
            status = "🔴 SIMULATED DATA"
        
        self.update_count += 1
        self.last_update_time = datetime.datetime.now()
        return status

class UltimateTickerDisplay:
    def __init__(self):
        self.ticker = UltimateNseTicker()
        
    def create_scrolling_ticker(self):
        """Create scrolling ticker tape"""
        if not self.ticker.market_data:
            return "<div>No data available</div>"
        
        ticker_items = []
        for stock, data in self.ticker.market_data.items():
            color = "#90EE90" if data['change'] >= 0 else "#FF6B6B"
            arrow = "▲" if data['change'] >= 0 else "▼"
            
            source_icon = "🟢" if data['source'] == 'NSE LIVE' else "🟡" if data['source'] == 'YAHOO FINANCE' else "🔴"
            
            ticker_items.append(f"""
            <span style='margin: 0 20px; font-family: Arial, sans-serif; white-space: nowrap;'>
                {source_icon} <strong>{stock}</strong>
                <span style='color: white;'> ₹{data['current']:,.2f}</span>
                <span style='color: {color};'> {arrow} {data['change']:+.2f}</span>
                <span style='color: {color};'>({data['change_pct']:+.2f}%)</span>
            </span>
            """)
        
        ticker_content = "".join(ticker_items)
        ticker_content_double = ticker_content + ticker_content
        
        html = f"""
        <div style='
            background: linear-gradient(135deg, #1e3d6d, #2c5282);
            color: white;
            padding: 12px 0;
            border-bottom: 3px solid #ff9933;
            font-family: Arial, sans-serif;
            overflow: hidden;
            position: relative;
        '>
            <div style='
                display: inline-block;
                white-space: nowrap;
                animation: ticker-scroll 30s linear infinite;
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
        
        return html
    
    def create_detailed_view(self):
        """Create detailed stock cards view"""
        if not self.ticker.market_data:
            return "<div>No data available</div>"
        
        cards_html = """
        <div style='
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
            font-family: Arial, sans-serif;
        '>
        """
        
        for stock, data in self.ticker.market_data.items():
            bg_color = "#d4edda" if data['change'] >= 0 else "#f8d7da"
            text_color = "#155724" if data['change'] >= 0 else "#721c24"
            arrow = "▲" if data['change'] >= 0 else "▼"
            
            source_color = "#28a745" if data['source'] == 'NSE LIVE' else "#ffc107" if data['source'] == 'YAHOO FINANCE' else "#dc3545"
            
            cards_html += f"""
            <div style='
                background: {bg_color};
                border: 2px solid {text_color}30;
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
                        <div style='font-size: 11px; background: {source_color}; color: white; padding: 3px 8px; border-radius: 10px;'>
                            {data['source']}
                        </div>
                        <div style='color: {text_color}; font-weight: bold; font-size: 14px; margin-top: 5px;'>
                            {arrow} {data['change']:+.2f} ({data['change_pct']:+.2f}%)
                        </div>
                    </div>
                </div>
            </div>
            """
        
        cards_html += "</div>"
        return cards_html
    
    def create_dashboard(self):
        """Create complete dashboard"""
        status = self.ticker.fetch_all_data()
        
        # Header with status
        header_html = f"""
        <div style='
            background: #152642;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            font-family: Arial, sans-serif;
        '>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div>
                    <h2 style='margin: 0; color: #ffd700;'>📈 ULTIMATE NSE TICKER</h2>
                    <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;'>
                        {status} | Update #{self.ticker.update_count} | {self.ticker.last_update_time.strftime("%H:%M:%S")}
                    </p>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 12px; opacity: 0.9;'>
                        🟢 NSE Live | 🟡 Yahoo | 🔴 Simulated
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Market overview
        gainers = sum(1 for data in self.ticker.market_data.values() if data['change'] > 0)
        losers = sum(1 for data in self.ticker.market_data.values() if data['change'] < 0)
        
        overview_html = f"""
        <div style='
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            font-family: Arial, sans-serif;
        '>
            <div style='display: flex; justify-content: space-around; text-align: center;'>
                <div>
                    <div style='color: #28a745; font-size: 20px; font-weight: bold;'>{gainers}</div>
                    <div style='color: #666; font-size: 12px;'>GAINERS</div>
                </div>
                <div>
                    <div style='color: #dc3545; font-size: 20px; font-weight: bold;'>{losers}</div>
                    <div style='color: #666; font-size: 12px;'>LOSERS</div>
                </div>
                <div>
                    <div style='color: #1e3d6d; font-size: 20px; font-weight: bold;'>{len(self.ticker.market_data)}</div>
                    <div style='color: #666; font-size: 12px;'>STOCKS</div>
                </div>
            </div>
        </div>
        """
        
        return header_html + self.create_scrolling_ticker() + overview_html + self.create_detailed_view()

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def test_ultimate_ticker():
    """Test the ultimate ticker with single update"""
    display_obj = UltimateTickerDisplay()
    
    print("🧪 TESTING ULTIMATE NSE TICKER...")
    print("=" * 60)
    
    clear_output(wait=True)
    display(HTML(display_obj.create_dashboard()))
    
    print(f"\n✅ ULTIMATE TICKER READY!")
    print(f"📊 Data Source: {display_obj.ticker.data_source}")
    print(f"🔄 Updates: {display_obj.ticker.update_count}")
    print("💡 Run 'start_ultimate_ticker()' for continuous updates")

def start_ultimate_ticker(interval=15):
    """Start continuous updates"""
    display_obj = UltimateTickerDisplay()
    
    print("🚀 STARTING ULTIMATE NSE TICKER")
    print("📍 Combined: NSE Live + Yahoo Finance + Simulated")
    print(f"🔄 Auto-update every {interval} seconds")
    print("=" * 70)
    
    try:
        while True:
            clear_output(wait=True)
            display(HTML(display_obj.create_dashboard()))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n🛑 Ticker stopped by user")

# =============================================================================
# RUN THE ULTIMATE TICKER
# =============================================================================

if __name__ == "__main__":
    # Test with single update
    test_ultimate_ticker()
    
    # Uncomment below line for continuous updates
    # start_ultimate_ticker()
