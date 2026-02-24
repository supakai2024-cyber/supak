"""
Combined Watchlist Generator: Top 25 CDC + Fibo Opportunities
รวมทั้ง Trend Following (CDC) และ Mean Reversion (Fibo)

รอบการทำงาน:
  - Round 1: 21:35 น. ไทย (14:35 UTC) → Full Scan 500+ หุ้น + สร้าง Watchlist
  - Round 2: 03:30 น. ไทย (20:30 UTC) → ใช้ Watchlist เดิม (ไม่ต้อง Rescan)
"""

from src.engine.scanner import MarketScanner
from src.data.market_data import MarketData
from src.strategies.cdc_action_zone import CDCActionZone
from src.strategies.fibo_strategy import FiboZoneStrategy
import json
from datetime import datetime, timezone, timedelta

# ============================================================
# ⏰ เวลาไทย (UTC+7)
# ============================================================
THAI_TZ = timezone(timedelta(hours=7))

def get_thai_time():
    """คืนเวลาปัจจุบันในเขตเวลาไทย (UTC+7)"""
    return datetime.now(THAI_TZ)

def is_round1_scan_time(tolerance_minutes=30):
    """
    ตรวจสอบว่าเป็นเวลา Round 1 (21:35 น. ไทย) หรือไม่
    คืนค่า True ถ้าอยู่ในช่วง ±tolerance_minutes จากเวลาเป้าหมาย
    
    Round 1 Target: 21:35 น. ไทย → ช่วง 21:05 - 22:05 น.
    Round 2 Target: 03:30 น. ไทย → ใช้ Watchlist เดิม ไม่ต้อง Rescan
    """
    now = get_thai_time()
    thai_hour = now.hour
    thai_min = now.minute
    total_minutes = thai_hour * 60 + thai_min
    
    # Target Round 1 = 21:35 น. = 21*60+35 = 1295 นาที
    target_round1 = 21 * 60 + 35
    diff = abs(total_minutes - target_round1)
    
    is_round1 = diff <= tolerance_minutes
    
    print(f"[TIME CHECK] เวลาไทยปัจจุบัน: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"[TIME CHECK] เป้าหมาย Round 1: 21:35 น. ไทย (ค่าเบี่ยงเบน: {diff} นาที, tolerance: ±{tolerance_minutes} นาที)")
    print(f"[TIME CHECK] → {'✅ Round 1 (Full Scan)' if is_round1 else '⏩ Round 2 (Use Existing Watchlist)'}")
    
    return is_round1

# รายชื่อหุ้น 503 ตัว
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
    'SLB', 'COP', 'EOG', 'MPC', 'VLO', 'PSX',
    # Consumer
    'COST', 'HD', 'LOW', 'TGT', 'NKE', 'SBUX', 'CMG', 'YUM',
    # Communications
    'T', 'VZ', 'TMUS', 'CMCSA',
    # Industrial
    'CAT', 'DE', 'UPS', 'FDX', 'HON', 'MMM', 'GE', 'LMT', 'RTX',
]

def generate_combined_watchlist():
    """
    สร้าง Watchlist แบบรวม:
    1. Top 20 CDC (Trend Following)
    2. Top 10 Fibo (Mean Reversion)
    = รวม 30 หุ้น
    """
    print("=" * 80)
    print("  StockRobo-US01: Combined Watchlist Generator")
    print("  Strategy: CDC (Trend) + Fibo (Pullback)")
    print(f"  Scanning {len(ALL_SYMBOLS)} symbols...")
    print("=" * 80)
    
    market_data = MarketData()
    cdc_strategy = CDCActionZone()
    fibo_strategy = FiboZoneStrategy(lookback_period=120)
    
    cdc_opportunities = []
    fibo_opportunities = []
    
    # สแกนทุกหุ้น
    for symbol in ALL_SYMBOLS:
        try:
            print(f"  Scanning {symbol}...", end='\r')
            
            # ดึงข้อมูล
            df = market_data.get_history(symbol, period='6mo')
            if df.empty or len(df) < 120:
                continue
            
            # วิเคราะห์ด้วย CDC
            df_cdc = cdc_strategy.calculate(df.copy())
            last_row = df_cdc.iloc[-1]
            prev_row = df_cdc.iloc[-2]
            
            current_price = last_row['Close']
            prev_price = prev_row['Close']
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            # CDC Signal (Green = Buy)
            if last_row['Color'] == 'Green':
                cdc_opportunities.append({
                    'symbol': symbol,
                    'strategy': 'CDC',
                    'price': current_price,
                    'change_pct': change_pct,
                    'color': 'Green',
                    'signal_strength': 'Strong' if change_pct > 2 else 'Moderate'
                })
            
            # วิเคราะห์ด้วย Fibo
            df_fibo = fibo_strategy.calculate(df.copy())
            last_fibo = df_fibo.iloc[-1]
            
            # Fibo Signal (In Zone = Buy)
            if last_fibo.get('In_Fibo_Zone', False):
                # คำนวณ % ที่ตกลงมา
                swing_high = last_fibo['Swing_High']
                swing_low = last_fibo['Swing_Low']
                fibo_range = swing_high - swing_low
                
                if fibo_range > 0:
                    retracement_pct = ((swing_high - current_price) / fibo_range) * 100
                    
                    # เช็คว่าอยู่ในช่วง 50-78.6% จริงๆ
                    if 50 <= retracement_pct <= 78.6:
                        fibo_opportunities.append({
                            'symbol': symbol,
                            'strategy': 'Fibo',
                            'price': current_price,
                            'swing_high': swing_high,
                            'swing_low': swing_low,
                            'retracement_pct': retracement_pct,
                            'fibo_500': last_fibo['Fibo_500'],
                            'fibo_786': last_fibo['Fibo_786'],
                            'discount': 'Deep' if retracement_pct > 65 else 'Moderate'
                        })
        
        except Exception as e:
            continue
    
    print(" " * 80, end='\r')  # Clear line
    
    # เรียงและคัดเลือก
    # CDC: เรียงตาม change_pct (momentum)
    cdc_opportunities.sort(key=lambda x: abs(x['change_pct']), reverse=True)
    top_cdc = cdc_opportunities[:20]
    
    # Fibo: เรียงตาม retracement_pct (ยิ่งลึกยิ่งดี)
    fibo_opportunities.sort(key=lambda x: x['retracement_pct'], reverse=True)
    top_fibo = fibo_opportunities[:10]
    
    # รวมกัน (ตัดซ้ำออก)
    combined_symbols = []
    combined_details = []
    
    # เพิ่ม CDC ก่อน
    for opp in top_cdc:
        combined_symbols.append(opp['symbol'])
        combined_details.append(opp)
    
    # เพิ่ม Fibo (ถ้าไม่ซ้ำ)
    for opp in top_fibo:
        if opp['symbol'] not in combined_symbols:
            combined_symbols.append(opp['symbol'])
            combined_details.append(opp)
    
    # บันทึกลงไฟล์
    watchlist_data = {
        'generated_at': datetime.now().isoformat(),
        'total_scanned': len(ALL_SYMBOLS),
        'cdc_signals': len(cdc_opportunities),
        'fibo_signals': len(fibo_opportunities),
        'watchlist': combined_symbols,
        'cdc_list': [o['symbol'] for o in top_cdc],
        'fibo_list': [o['symbol'] for o in top_fibo],
        'details': combined_details
    }
    
    with open('data/watchlist.json', 'w') as f:
        json.dump(watchlist_data, f, indent=2)
    
    # แสดงผล
    print(f"\n[OK] Found {len(cdc_opportunities)} CDC signals (Green)")
    print(f"[OK] Found {len(fibo_opportunities)} Fibo signals (50-78.6% zone)")
    
    print(f"\n[Trend] Top 20 CDC Opportunities (Trend Following):")
    print("=" * 80)
    print(f"{'#':<3} {'Symbol':<8} {'Price':<10} {'Change%':<10} {'Strength':<12}")
    print("=" * 80)
    for i, opp in enumerate(top_cdc, 1):
        print(f"{i:<3} {opp['symbol']:<8} ${opp['price']:<9.2f} "
              f"{opp['change_pct']:>+8.2f}% {opp['signal_strength']:<12}")
    
    print(f"\n[Pullback] Top 10 Fibo Opportunities (Pullback/Dip Buying):")
    print("=" * 80)
    print(f"{'#':<3} {'Symbol':<8} {'Price':<10} {'High':<10} {'Retrace%':<12} {'Discount':<12}")
    print("=" * 80)
    for i, opp in enumerate(top_fibo, 1):
        print(f"{i:<3} {opp['symbol']:<8} ${opp['price']:<9.2f} "
              f"${opp['swing_high']:<9.2f} {opp['retracement_pct']:>8.1f}% "
              f"{opp['discount']:<12}")
    
    print("=" * 80)
    print(f"\n[Summary] Combined Watchlist: {len(combined_symbols)} symbols")
    print(f"   - CDC (Green): {len(top_cdc)} stocks")
    print(f"   - Fibo (Dip): {len([o for o in top_fibo if o['symbol'] not in [c['symbol'] for c in top_cdc]])} stocks (unique)")
    
    print(f"\n[Save] Saved to: data/watchlist.json")
    
    return combined_symbols

if __name__ == "__main__":
    import sys
    import os
    
    print("=" * 80)
    print("  StockRobo-US01: Smart Round Detection")
    print("=" * 80)
    
    # ตรวจสอบว่า Force scan หรือไม่ (ส่ง argument "--force-scan" เพื่อ Force)
    force_scan = "--force-scan" in sys.argv
    
    if force_scan:
        print("[MODE] Force Scan: ข้ามการตรวจสอบเวลา → Full Scan ทันที")
        watchlist = generate_combined_watchlist()
    
    elif is_round1_scan_time(tolerance_minutes=30):
        # ✅ Round 1: 21:35 น. ไทย → Full Scan + สร้าง Watchlist ใหม่
        print("\n[ROUND 1] 21:35 น. ไทย → Full Scan 500+ หุ้น + สร้าง Watchlist ใหม่")
        print("=" * 80)
        watchlist = generate_combined_watchlist()
    
    else:
        # ⏩ Round 2: 03:30 น. ไทย → ใช้ Watchlist เดิม ไม่ต้อง Rescan
        print("\n[ROUND 2] 03:30 น. ไทย → ใช้ Watchlist เดิม (ประหยัด API Quota)")
        print("=" * 80)
        
        watchlist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "watchlist.json")
        
        if os.path.exists(watchlist_path):
            with open(watchlist_path, 'r') as f:
                watchlist_data = json.load(f)
            watchlist = watchlist_data.get('watchlist', [])
            gen_at = watchlist_data.get('generated_at', 'Unknown')
            print(f"[ROUND 2] ✅ โหลด Watchlist เดิมสำเร็จ: {len(watchlist)} หุ้น")
            print(f"[ROUND 2] 📅 สร้างเมื่อ: {gen_at}")
            print(f"[ROUND 2] 📋 รายชื่อ: {', '.join(watchlist[:10])} ...")
        else:
            print("[ROUND 2] ⚠️ ไม่พบ watchlist.json → Fallback: Full Scan")
            watchlist = generate_combined_watchlist()
    
    print("\n" + "=" * 80)
    print("[DONE] Watchlist พร้อมแล้ว!")
    print(f"[DONE] จำนวนหุ้น: {len(watchlist)} ตัว")
    print("[DONE] ขั้นตอนถัดไป:")
    print("  1. Push ไป GitHub: git add data/ && git commit -m 'Update' && git push")
    print("  2. GitHub Actions จะรัน run_phase2_gh_action.py อัตโนมัติ 2 รอบ/วัน")
    print("     - Round 1: 21:35 น. ไทย (Full Scan)")
    print("     - Round 2: 03:30 น. ไทย (Trade Only)")
    print("=" * 80)
