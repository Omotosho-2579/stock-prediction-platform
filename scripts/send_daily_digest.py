# scripts/send_daily_digest.py

import sys
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import (
    EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT,
    ENABLE_EMAIL_ALERTS, POPULAR_STOCKS
)
from src.data.data_loader import DataLoader
from src.data.technical_indicators import TechnicalIndicators
from src.trading_signals.signal_generator import SignalGenerator
from src.utils.logger import Logger
from src.utils.formatters import Formatters

logger = Logger(__name__)
data_loader = DataLoader()
tech_indicators = TechnicalIndicators()
signal_generator = SignalGenerator()
formatters = Formatters()

def get_market_summary():
    summary = {
        'indices': [],
        'top_gainers': [],
        'top_losers': [],
        'high_volume': []
    }
    
    indices = {
        'S&P 500': '^GSPC',
        'Dow Jones': '^DJI',
        'NASDAQ': '^IXIC'
    }
    
    for name, symbol in indices.items():
        try:
            df = data_loader.load_stock_data(symbol, period='2d')
            if df is not None and len(df) >= 2:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                
                summary['indices'].append({
                    'name': name,
                    'price': current,
                    'change': change
                })
        except Exception as e:
            logger.error(f"Error loading {name}: {str(e)}")
    
    stocks_data = []
    for symbol in POPULAR_STOCKS[:20]:
        try:
            df = data_loader.load_stock_data(symbol, period='2d')
            if df is not None and len(df) >= 2:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                volume = df['Volume'].iloc[-1]
                
                stocks_data.append({
                    'symbol': symbol,
                    'price': current,
                    'change': change,
                    'volume': volume
                })
        except Exception as e:
            logger.error(f"Error loading {symbol}: {str(e)}")
    
    stocks_data.sort(key=lambda x: x['change'], reverse=True)
    summary['top_gainers'] = stocks_data[:5]
    summary['top_losers'] = stocks_data[-5:]
    
    stocks_data.sort(key=lambda x: x['volume'], reverse=True)
    summary['high_volume'] = stocks_data[:5]
    
    return summary

def get_trading_signals():
    signals = []
    
    for symbol in POPULAR_STOCKS[:10]:
        try:
            df = data_loader.load_stock_data(symbol, period='1mo')
            if df is not None and not df.empty:
                df_with_indicators = tech_indicators.add_all_indicators(df)
                
                signal_data = signal_generator.generate_signal(
                    df_with_indicators,
                    strategy='AI Composite',
                    sensitivity='Moderate'
                )
                
                if signal_data.get('signal') in ['BUY', 'SELL']:
                    signals.append({
                        'symbol': symbol,
                        'signal': signal_data.get('signal'),
                        'confidence': signal_data.get('confidence', 0),
                        'price': df['Close'].iloc[-1]
                    })
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
    
    signals.sort(key=lambda x: x['confidence'], reverse=True)
    return signals[:5]

def generate_html_email(summary, signals):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                background: white;
                margin: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .section {{
                padding: 30px;
                border-bottom: 1px solid #eee;
            }}
            .section:last-child {{
                border-bottom: none;
            }}
            .section h2 {{
                color: #667eea;
                margin-top: 0;
                font-size: 22px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .index-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .index-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border: 2px solid #e9ecef;
            }}
            .index-name {{
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 5px;
            }}
            .index-price {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .index-change {{
                font-size: 14px;
                font-weight: 600;
                margin-top: 5px;
            }}
            .positive {{
                color: #22c55e;
            }}
            .negative {{
                color: #ef4444;
            }}
            .stock-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            .stock-table th {{
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #dee2e6;
            }}
            .stock-table td {{
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
            }}
            .stock-table tr:hover {{
                background: #f8f9fa;
            }}
            .signal-badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .signal-buy {{
                background: #d1fae5;
                color: #065f46;
            }}
            .signal-sell {{
                background: #fee2e2;
                color: #991b1b;
            }}
            .confidence-bar {{
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
                overflow: hidden;
                margin-top: 5px;
            }}
            .confidence-fill {{
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
            @media only screen and (max-width: 600px) {{
                .index-grid {{
                    grid-template-columns: 1fr;
                }}
                .stock-table {{
                    font-size: 14px;
                }}
                .stock-table th, .stock-table td {{
                    padding: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 Daily Market Digest</h1>
                <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Major Indices</h2>
                <div class="index-grid">
    """
    
    for index in summary['indices']:
        change_class = 'positive' if index['change'] > 0 else 'negative'
        change_symbol = '+' if index['change'] > 0 else ''
        html += f"""
                    <div class="index-card">
                        <div class="index-name">{index['name']}</div>
                        <div class="index-price">{formatters.format_number(index['price'])}</div>
                        <div class="index-change {change_class}">{change_symbol}{index['change']:.2f}%</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <div class="section">
                <h2>🔥 Top Gainers</h2>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Change</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for stock in summary['top_gainers']:
        html += f"""
                        <tr>
                            <td><strong>{stock['symbol']}</strong></td>
                            <td>{formatters.format_currency(stock['price'])}</td>
                            <td class="positive">+{stock['change']:.2f}%</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📉 Top Losers</h2>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Change</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for stock in summary['top_losers']:
        html += f"""
                        <tr>
                            <td><strong>{stock['symbol']}</strong></td>
                            <td>{formatters.format_currency(stock['price'])}</td>
                            <td class="negative">{stock['change']:.2f}%</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
    """
    
    if signals:
        html += """
            <div class="section">
                <h2>🎯 AI Trading Signals</h2>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Signal</th>
                            <th>Price</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for signal in signals:
            signal_class = 'signal-buy' if signal['signal'] == 'BUY' else 'signal-sell'
            html += f"""
                        <tr>
                            <td><strong>{signal['symbol']}</strong></td>
                            <td><span class="signal-badge {signal_class}">{signal['signal']}</span></td>
                            <td>{formatters.format_currency(signal['price'])}</td>
                            <td>
                                {signal['confidence']}%
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: {signal['confidence']}%"></div>
                                </div>
                            </td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        """
    
    html += """
            <div class="section">
                <h2>📈 High Volume Stocks</h2>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Volume</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for stock in summary['high_volume']:
        html += f"""
                        <tr>
                            <td><strong>{stock['symbol']}</strong></td>
                            <td>{formatters.format_currency(stock['price'])}</td>
                            <td>{formatters.format_number(stock['volume'])}</td>
                        </tr>
        """
    
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p><strong>AI Stock Prediction Platform</strong></p>
                <p>This is an automated daily digest. Market data is for informational purposes only.</p>
                <p>⚠️ This is not financial advice. Always do your own research before making investment decisions.</p>
                <p style="margin-top: 15px;">
                    <a href="#">View Full Dashboard</a> | 
                    <a href="#">Manage Preferences</a> | 
                    <a href="#">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(recipient_email, subject, html_content):
    if not ENABLE_EMAIL_ALERTS:
        logger.warning("Email alerts are disabled. Configure EMAIL_SENDER and EMAIL_PASSWORD.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Send daily market digest email')
    parser.add_argument('--email', type=str, help='Recipient email address')
    parser.add_argument('--test', action='store_true', help='Test mode - prints HTML instead of sending')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Generating Daily Market Digest")
    print("="*60 + "\n")
    
    print("Fetching market data...")
    summary = get_market_summary()
    
    print("Generating trading signals...")
    signals = get_trading_signals()
    
    print("Creating email content...")
    html_content = generate_html_email(summary, signals)
    
    if args.test:
        print("\n" + "="*60)
        print("TEST MODE - Email Content")
        print("="*60 + "\n")
        print(html_content)
        print("\n" + "="*60 + "\n")
        return
    
    if not args.email:
        print("\n✗ Error: Please provide recipient email with --email flag")
        print("Example: python send_daily_digest.py --email user@example.com")
        return
    
    subject = f"📈 Daily Market Digest - {datetime.now().strftime('%B %d, %Y')}"
    
    print(f"Sending email to {args.email}...")
    
    if send_email(args.email, subject, html_content):
        print("\n✓ Email sent successfully")
    else:
        print("\n✗ Failed to send email")

if __name__ == "__main__":
    main()