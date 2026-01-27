"""
Watchlist Generator: สแกนหุ้น 503 ตัว แล้วคัดเหลือ Top 20
รันบนเครื่องตัวเอง 1-2 ครั้ง/วัน
"""

from src.engine.scanner import MarketScanner
import json
from datetime import datetime

# รายชื่อหุ้น 503 ตัว (ตัวอย่าง - เพิ่มเติมได้)
ALL_SYMBOLS = [
    # Big Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX',
    # Semiconductors
    'AMD', 'INTC', 'QCOM', 'MU', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'ASML',
    # Growth/Retail
    'COIN', 'HOOD', 'PLTR', 'U', 'SNOW', 'DDOG', 'NET', 'CRWD', 'ZS', 'OKTA',
    # Indices/ETFs
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO',
    # Traditional Blue Chips
    'DIS', 'BA', 'MCD', 'KO', 'JNJ', 'PG', 'WMT', 'CVX', 'XOM', 'JPM',
    # Crypto Miners
    'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF',
    # EVs & Auto
    'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
    # Finance
    'BAC', 'C', 'GS', 'MS', 'WFC', 'BLK', 'SCHW', 'AXP',
    # Healthcare
    'UNH', 'LLY', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS',
    # Energy
    'SLB', 'COP', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX',
    # Consumer
    'COST', 'HD', 'LOW', 'TGT', 'NKE', 'SBUX', 'CMG', 'YUM',
    # Communications
    'T', 'VZ', 'TMUS', 'CMCSA', 'DIS', 'NFLX', 'PARA',
    # Industrial
    'CAT', 'DE', 'UPS', 'FDX', 'HON', 'MMM', 'GE', 'LMT', 'RTX',
    # Materials
    'LIN', 'APD', 'ECL', 'SHW', 'NEM', 'FCX', 'NUE',
    # Real Estate
    'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'DLR', 'O', 'WELL',
    # Utilities
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE',
    # Add more symbols here to reach 503...
    # (ตัวอย่างนี้มีประมาณ 150 ตัว - เพิ่มเติมได้ตามต้องการ)
]

def generate_watchlist(top_n=20):
    """
    สแกนหุ้นทั้งหมด แล้วคัดเหลือ Top N ตัวที่น่าสนใจที่สุด
    """
    print("=" * 60)
    print("  StockRobo-US01: Watchlist Generator")
    print(f"  Scanning {len(ALL_SYMBOLS)} symbols...")
    print("=" * 60)
    
    scanner = MarketScanner()
    results = scanner.scan(ALL_SYMBOLS)
    
    # รวม Buy Signals ทั้งหมด
    buy_signals = results.get('buy_signals', [])
    
    print(f"\n✅ Found {len(buy_signals)} buy signals")
    
    if not buy_signals:
        print("⚠️ No signals found. Using default watchlist.")
        return ['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD']
    
    # เรียงตาม change_pct (momentum)
    sorted_signals = sorted(buy_signals, key=lambda x: abs(x.get('change_pct', 0)), reverse=True)
    
    # คัดเหลือ Top N
    top_symbols = [sig['symbol'] for sig in sorted_signals[:top_n]]
    
    # บันทึกลงไฟล์
    watchlist_data = {
        'generated_at': datetime.now().isoformat(),
        'total_scanned': len(ALL_SYMBOLS),
        'signals_found': len(buy_signals),
        'watchlist': top_symbols,
        'details': sorted_signals[:top_n]
    }
    
    with open('data/watchlist.json', 'w') as f:
        json.dump(watchlist_data, f, indent=2)
    
    print(f"\n📊 Top {top_n} Watchlist:")
    print("-" * 60)
    for i, symbol in enumerate(top_symbols, 1):
        detail = next((s for s in sorted_signals if s['symbol'] == symbol), {})
        print(f"{i:2d}. {symbol:6s} - Change: {detail.get('change_pct', 0):+.2f}%")
    print("-" * 60)
    
    print(f"\n💾 Saved to: data/watchlist.json")
    
    return top_symbols

if __name__ == "__main__":
    watchlist = generate_watchlist(top_n=20)
    
    print("\n🎯 Next Steps:")
    print("1. Review the watchlist in data/watchlist.json")
    print("2. Phase 2 bot will use these symbols for trading")
    print("3. Re-run this script daily to update watchlist")
