"""
Top 25 Watching Stock Generator
สแกนหุ้น 503 ตัว แล้วคัดเลือก Top 25 ตามเกณฑ์หลายมิติ
"""

from src.engine.scanner import MarketScanner
from src.data.market_data import MarketData
import json
from datetime import datetime
import pandas as pd

# รายชื่อหุ้น 503 ตัว (เพิ่มเติมได้)
ALL_SYMBOLS = [
    # Big Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX',
    # Semiconductors
    'AMD', 'INTC', 'QCOM', 'MU', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'ASML',
    # Growth/SaaS
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
    'T', 'VZ', 'TMUS', 'CMCSA', 'PARA',
    # Industrial
    'CAT', 'DE', 'UPS', 'FDX', 'HON', 'MMM', 'GE', 'LMT', 'RTX',
    # Materials
    'LIN', 'APD', 'ECL', 'SHW', 'NEM', 'FCX', 'NUE',
    # Real Estate
    'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'DLR', 'O', 'WELL',
    # Utilities
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE',
]

# Sector Mapping
SECTOR_MAP = {
    'Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'CRM', 'ORCL'],
    'Semiconductor': ['NVDA', 'AMD', 'INTC', 'QCOM', 'MU', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'ASML', 'TSM'],
    'Growth': ['COIN', 'HOOD', 'PLTR', 'U', 'SNOW', 'DDOG', 'NET', 'CRWD', 'ZS', 'OKTA'],
    'Auto': ['TSLA', 'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI'],
    'Finance': ['JPM', 'BAC', 'C', 'GS', 'MS', 'WFC', 'BLK', 'SCHW', 'AXP'],
    'Healthcare': ['UNH', 'LLY', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS'],
    'Energy': ['XOM', 'CVX', 'SLB', 'COP', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX'],
    'Consumer': ['COST', 'HD', 'LOW', 'TGT', 'NKE', 'SBUX', 'CMG', 'YUM', 'MCD', 'KO', 'PG', 'WMT'],
}

def get_sector(symbol):
    """หา Sector ของหุ้น"""
    for sector, symbols in SECTOR_MAP.items():
        if symbol in symbols:
            return sector
    return 'Other'

def calculate_score(symbol, signal_data, market_data_df):
    """
    คำนวณคะแนนรวมจาก 5 เกณฑ์:
    1. Technical Signal (40)
    2. Momentum (25)
    3. Volatility (20)
    4. Market Cap (10)
    5. Sector (5)
    """
    score = 0
    details = {}
    
    # 1. Technical Signal (40 คะแนน)
    color = signal_data.get('color', 'Neutral')
    if color == 'Green':
        score += 40
        details['signal'] = 'Green (Strong Uptrend)'
    elif color == 'Blue':
        score += 30
        details['signal'] = 'Blue (Weak Uptrend)'
    elif color == 'Yellow':
        score += 20
        details['signal'] = 'Yellow (Weak Downtrend)'
    else:  # Red
        score += 0
        details['signal'] = 'Red (Downtrend)'
    
    # 2. Momentum (25 คะแนน)
    change_pct = abs(signal_data.get('change_pct', 0))
    if change_pct > 2:
        score += 25
        details['momentum'] = 'High (+25)'
    elif change_pct > 1:
        score += 15
        details['momentum'] = 'Medium (+15)'
    else:
        score += 5
        details['momentum'] = 'Low (+5)'
    
    # 3. Volatility (20 คะแนน) - ใช้ change_pct เป็นตัวแทน ATR
    if change_pct > 3:
        score += 20
        details['volatility'] = 'High (+20)'
    elif change_pct > 1:
        score += 15
        details['volatility'] = 'Medium (+15)'
    else:
        score += 10
        details['volatility'] = 'Low (+10)'
    
    # 4. Market Cap & Liquidity (10 คะแนน)
    # สมมติว่าหุ้นใน list หลักๆ เป็น Large Cap
    large_caps = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM', 'UNH']
    if symbol in large_caps:
        score += 10
        details['market_cap'] = 'Large Cap (+10)'
    else:
        score += 7
        details['market_cap'] = 'Mid/Small Cap (+7)'
    
    # 5. Sector Rotation (5 คะแนน)
    sector = get_sector(symbol)
    # สมมติว่าหุ้นแรกใน Sector เป็น Leader
    is_leader = False
    for sec, syms in SECTOR_MAP.items():
        if symbol in syms and syms[0] == symbol:
            is_leader = True
            break
    
    if is_leader:
        score += 5
        details['sector'] = f'{sector} Leader (+5)'
    else:
        score += 3
        details['sector'] = f'{sector} (+3)'
    
    return score, details

def generate_top25_watchlist(strategy='hybrid'):
    """
    สร้าง Top 25 Watchlist
    
    Args:
        strategy: 'top_score', 'diversified', 'hybrid'
    """
    print("=" * 70)
    print("  StockRobo-US01: Top 25 Watching Stock Generator")
    print(f"  Strategy: {strategy.upper()}")
    print(f"  Scanning {len(ALL_SYMBOLS)} symbols...")
    print("=" * 70)
    
    scanner = MarketScanner()
    market_data = MarketData()
    
    # สแกนทั้งหมด
    results = scanner.scan(ALL_SYMBOLS)
    
    # รวม Buy + Sell signals (เราต้องการทุกหุ้นที่มี Signal)
    all_signals = results.get('buy_signals', []) + results.get('sell_signals', [])
    
    print(f"\n✅ Found {len(all_signals)} signals")
    
    if not all_signals:
        print("⚠️ No signals found. Using default watchlist.")
        return ['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD']
    
    # คำนวณคะแนนแต่ละหุ้น
    scored_stocks = []
    
    for sig in all_signals:
        symbol = sig['symbol']
        
        # ดึงข้อมูลเพิ่มเติม (ถ้าต้องการ)
        try:
            df = market_data.get_history(symbol, period='1mo')
            score, details = calculate_score(symbol, sig, df)
            
            scored_stocks.append({
                'symbol': symbol,
                'score': score,
                'price': sig.get('price', 0),
                'change_pct': sig.get('change_pct', 0),
                'color': sig.get('color', 'Unknown'),
                'sector': get_sector(symbol),
                'details': details
            })
        except Exception as e:
            print(f"⚠️ Error processing {symbol}: {e}")
            continue
    
    # เรียงตามคะแนน
    scored_stocks.sort(key=lambda x: x['score'], reverse=True)
    
    # เลือก Top 25 ตาม Strategy
    if strategy == 'top_score':
        top_25 = scored_stocks[:25]
    
    elif strategy == 'diversified':
        # กระจาย Sector
        top_25 = []
        sector_quota = {
            'Tech': 6,
            'Semiconductor': 5,
            'Growth': 4,
            'Auto': 3,
            'Finance': 2,
            'Healthcare': 2,
            'Energy': 1,
            'Consumer': 1,
            'Other': 1
        }
        
        for sector, quota in sector_quota.items():
            sector_stocks = [s for s in scored_stocks if s['sector'] == sector]
            top_25.extend(sector_stocks[:quota])
        
        # เติมให้ครบ 25
        remaining = 25 - len(top_25)
        if remaining > 0:
            added_symbols = {s['symbol'] for s in top_25}
            for stock in scored_stocks:
                if stock['symbol'] not in added_symbols:
                    top_25.append(stock)
                    if len(top_25) >= 25:
                        break
    
    else:  # hybrid
        # เอา Top 15 ตามคะแนน
        top_25 = scored_stocks[:15]
        added_symbols = {s['symbol'] for s in top_25}
        
        # + 10 หุ้นกระจาย Sector
        for sector in ['Tech', 'Semiconductor', 'Growth', 'Auto', 'Finance', 'Healthcare']:
            sector_stocks = [s for s in scored_stocks if s['sector'] == sector and s['symbol'] not in added_symbols]
            if sector_stocks:
                top_25.append(sector_stocks[0])
                added_symbols.add(sector_stocks[0]['symbol'])
                if len(top_25) >= 25:
                    break
        
        # เติมให้ครบ 25
        remaining = 25 - len(top_25)
        if remaining > 0:
            for stock in scored_stocks:
                if stock['symbol'] not in added_symbols:
                    top_25.append(stock)
                    if len(top_25) >= 25:
                        break
    
    # จำกัดไว้ที่ 25
    top_25 = top_25[:25]
    
    # บันทึกลงไฟล์
    watchlist_data = {
        'generated_at': datetime.now().isoformat(),
        'strategy': strategy,
        'total_scanned': len(ALL_SYMBOLS),
        'signals_found': len(all_signals),
        'watchlist': [s['symbol'] for s in top_25],
        'details': top_25
    }
    
    with open('data/watchlist.json', 'w') as f:
        json.dump(watchlist_data, f, indent=2)
    
    # แสดงผล
    print(f"\n🏆 Top 25 Watching Stock:")
    print("=" * 90)
    print(f"{'#':<3} {'Symbol':<8} {'Score':<6} {'Price':<10} {'Change%':<10} {'Signal':<15} {'Sector':<15}")
    print("=" * 90)
    
    for i, stock in enumerate(top_25, 1):
        print(f"{i:<3} {stock['symbol']:<8} {stock['score']:<6} "
              f"${stock['price']:<9.2f} {stock['change_pct']:>+8.2f}% "
              f"{stock['color']:<15} {stock['sector']:<15}")
    
    print("=" * 90)
    
    # สรุป Sector Distribution
    sector_count = {}
    for stock in top_25:
        sector = stock['sector']
        sector_count[sector] = sector_count.get(sector, 0) + 1
    
    print(f"\n📊 Sector Distribution:")
    for sector, count in sorted(sector_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sector:<15}: {count} stocks")
    
    print(f"\n💾 Saved to: data/watchlist.json")
    
    return [s['symbol'] for s in top_25]

if __name__ == "__main__":
    import sys
    
    # รับ strategy จาก command line (default: hybrid)
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'hybrid'
    
    if strategy not in ['top_score', 'diversified', 'hybrid']:
        print(f"⚠️ Invalid strategy: {strategy}")
        print("Valid options: top_score, diversified, hybrid")
        sys.exit(1)
    
    watchlist = generate_top25_watchlist(strategy=strategy)
    
    print("\n🎯 Next Steps:")
    print("1. Review the watchlist in data/watchlist.json")
    print("2. Push to GitHub: git add data/watchlist.json && git commit -m 'Update watchlist' && git push")
    print("3. Phase 2 bot will use these 25 symbols for trading (5 rounds/day)")
    print("4. Re-run this script tomorrow morning for fresh watchlist")
