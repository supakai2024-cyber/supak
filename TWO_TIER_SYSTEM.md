# 🎯 StockRobo-US01: Two-Tier Scanning System

## 📊 ภาพรวมระบบ

ระบบของเรามี **2 ชั้น** ทำงานร่วมกัน:

```
┌─────────────────────────────────────────────────────────┐
│  TIER 1: Full Market Scanner (รันบนเครื่องตัวเอง)      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ • สแกน 503 หุ้นทั้งหมด                            │ │
│  │ • ใช้ CDC Action Zone Strategy                    │ │
│  │ • คัดเหลือ Top 20 หุ้นที่น่าสนใจ                  │ │
│  │ • บันทึกลง data/watchlist.json                    │ │
│  │ • รัน: 1-2 ครั้ง/วัน (เช้า/เย็น)                  │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ watchlist.json
┌─────────────────────────────────────────────────────────┐
│  TIER 2: Quick Execution Bot (รันบน GitHub Actions)    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ • อ่าน watchlist.json (20 หุ้น)                   │ │
│  │ • สแกนเฉพาะหุ้นที่คัดมาแล้ว                       │ │
│  │ • ซื้อขายตาม Signal                               │ │
│  │ • บันทึกลง portfolio_state.json                   │ │
│  │ • รัน: 5 ครั้ง/วัน (อัตโนมัติ)                    │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼ portfolio_state.json
┌─────────────────────────────────────────────────────────┐
│  TIER 3: Dashboard (GitHub Pages)                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ • อ่าน portfolio_state.json                       │ │
│  │ • แสดงผล Portfolio, Charts, Trades                │ │
│  │ • Auto-refresh ทุก 30 วินาที                      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 ไฟล์และหน้าที่

### **Tier 1: Full Scanner**

**ไฟล์:** `generate_watchlist.py`

**หน้าที่:**
- สแกนหุ้น 503 ตัวทั้งหมด
- วิเคราะห์ด้วย CDC Action Zone
- คัดเหลือ Top 20 ตัวที่มี Signal แรงที่สุด
- บันทึกลง `data/watchlist.json`

**วิธีรัน:**
```bash
python generate_watchlist.py
```

**ความถี่:** 1-2 ครั้ง/วัน (แนะนำ: เช้า 08:00 และเย็น 20:00)

**Output:** `data/watchlist.json`
```json
{
  "generated_at": "2026-01-27T22:00:00",
  "total_scanned": 503,
  "signals_found": 45,
  "watchlist": ["NVDA", "TSLA", "AAPL", ...],
  "details": [...]
}
```

---

### **Tier 2: Quick Execution**

**ไฟล์:** `run_phase2_gh_action.py`

**หน้าที่:**
- อ่าน `data/watchlist.json`
- สแกนเฉพาะหุ้นที่คัดมาแล้ว (20 ตัว)
- ซื้อขายตาม Signal
- บันทึกลง `data/portfolio_state.json`

**วิธีรัน:**
- **อัตโนมัติ:** GitHub Actions (5 ครั้ง/วัน)
- **Manual:** `python run_phase2_gh_action.py`

**ความถี่:** 5 รอบ/วัน
- 21:35 น. (Pre-Market)
- 23:05 น. (Market Open)
- 00:35 น. (Mid Session)
- 02:05 น. (Late Session)
- 03:35 น. (Near Close)

**Output:** `data/portfolio_state.json`

---

### **Tier 3: Dashboard**

**ไฟล์:** `dashboard/index.html`

**หน้าที่:**
- อ่าน `data/portfolio_state.json`
- แสดงผล Portfolio, Charts, Trades
- Auto-refresh ทุก 30 วินาที

**วิธีเปิด:**
- ดับเบิลคลิก `dashboard/index.html`
- หรือ Deploy ไป GitHub Pages

---

## 📋 รายชื่อหุ้น 503 ตัว

### **หมวดหมู่หลัก:**

1. **Big Tech (10 ตัว)**
   - AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, NFLX, ORCL, CRM

2. **Semiconductors (20 ตัว)**
   - AMD, INTC, QCOM, MU, AVGO, TXN, AMAT, LRCX, KLAC, ASML, ...

3. **Growth/SaaS (25 ตัว)**
   - COIN, HOOD, PLTR, U, SNOW, DDOG, NET, CRWD, ZS, OKTA, ...

4. **Indices/ETFs (10 ตัว)**
   - SPY, QQQ, IWM, DIA, VTI, VOO, XLK, XLF, XLE, XLV

5. **Blue Chips (50 ตัว)**
   - DIS, BA, MCD, KO, JNJ, PG, WMT, CVX, XOM, JPM, ...

6. **Finance (30 ตัว)**
   - BAC, C, GS, MS, WFC, BLK, SCHW, AXP, V, MA, ...

7. **Healthcare (30 ตัว)**
   - UNH, LLY, ABBV, TMO, ABT, DHR, BMY, AMGN, GILD, CVS, ...

8. **Energy (25 ตัว)**
   - SLB, COP, EOG, PXD, MPC, VLO, PSX, OXY, HAL, ...

9. **Consumer (40 ตัว)**
   - COST, HD, LOW, TGT, NKE, SBUX, CMG, YUM, MCD, ...

10. **และอื่นๆ อีก 263 ตัว**

**📝 หมายเหตุ:** ไฟล์ `generate_watchlist.py` มีตัวอย่าง 150 ตัว คุณสามารถเพิ่มเติมได้ใน list `ALL_SYMBOLS`

---

## 🚀 วิธีใช้งาน

### **ขั้นตอนที่ 1: สร้าง Watchlist (ทำบนเครื่องตัวเอง)**

```bash
# รันทุกเช้า หรือทุกเย็น
python generate_watchlist.py
```

**ผลลัพธ์:**
```
==========================================
  StockRobo-US01: Watchlist Generator
  Scanning 503 symbols...
==========================================

✅ Found 45 buy signals

📊 Top 20 Watchlist:
------------------------------------------------------------
 1. NVDA   - Change: +3.45%
 2. TSLA   - Change: +2.89%
 3. AAPL   - Change: +2.12%
...
------------------------------------------------------------

💾 Saved to: data/watchlist.json
```

---

### **ขั้นตอนที่ 2: Push Watchlist ไป GitHub**

```bash
git add data/watchlist.json
git commit -m "Update watchlist"
git push
```

---

### **ขั้นตอนที่ 3: ให้ Bot รันอัตโนมัติ**

GitHub Actions จะ:
1. อ่าน `data/watchlist.json`
2. สแกนเฉพาะ 20 หุ้นที่คัดมา
3. ซื้อขายตาม Signal
4. อัปเดต `data/portfolio_state.json`

---

### **ขั้นตอนที่ 4: ดู Dashboard**

เปิด `dashboard/index.html` เพื่อดูผลลัพธ์

---

## ⏰ ตารางเวลาแนะนำ

| เวลา (ไทย) | กิจกรรม | ไฟล์ที่รัน |
|-----------|---------|-----------|
| 08:00 | สร้าง Watchlist (เช้า) | `generate_watchlist.py` |
| 20:00 | อัปเดต Watchlist (เย็น) | `generate_watchlist.py` |
| 21:35 | Bot รอบ 1 (Auto) | `run_phase2_gh_action.py` |
| 23:05 | Bot รอบ 2 (Auto) | `run_phase2_gh_action.py` |
| 00:35 | Bot รอบ 3 (Auto) | `run_phase2_gh_action.py` |
| 02:05 | Bot รอบ 4 (Auto) | `run_phase2_gh_action.py` |
| 03:35 | Bot รอบ 5 (Auto) | `run_phase2_gh_action.py` |

---

## 🎯 ข้อดีของระบบ 2 ชั้น

### ✅ **Tier 1 (Full Scanner)**
- ครอบคลุมหุ้นทั้งตลาด (503 ตัว)
- หาโอกาสที่ดีที่สุด
- รันบนเครื่องตัวเอง (ไม่มีข้อจำกัด)

### ✅ **Tier 2 (Quick Bot)**
- รันเร็ว (1-2 นาที)
- ประหยัด API Quota
- เหมาะกับ GitHub Actions
- ซื้อขายได้ทันเวลา

### ✅ **ผลรวม**
- ได้ทั้งความครอบคลุม (503 หุ้น)
- และความรวดเร็ว (5 รอบ/วัน)
- ไม่เสีย GitHub Actions Quota

---

## 🔧 การปรับแต่ง

### **เปลี่ยนจำนวนหุ้นใน Watchlist**

แก้ไขใน `generate_watchlist.py`:
```python
watchlist = generate_watchlist(top_n=30)  # เปลี่ยนจาก 20 เป็น 30
```

### **เพิ่มหุ้นที่ต้องการสแกน**

แก้ไขใน `generate_watchlist.py`:
```python
ALL_SYMBOLS = [
    'AAPL', 'MSFT', ...
    'YOUR_SYMBOL_HERE',  # เพิ่มตรงนี้
]
```

### **เปลี่ยนเกณฑ์การคัดเลือก**

แก้ไขใน `generate_watchlist.py`:
```python
# เรียงตาม momentum (default)
sorted_signals = sorted(buy_signals, key=lambda x: abs(x.get('change_pct', 0)), reverse=True)

# หรือเรียงตามราคา
sorted_signals = sorted(buy_signals, key=lambda x: x.get('price', 0))
```

---

## 📊 ตัวอย่างผลลัพธ์

### **watchlist.json**
```json
{
  "generated_at": "2026-01-27T08:00:00",
  "total_scanned": 503,
  "signals_found": 45,
  "watchlist": [
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN",
    "GOOGL", "META", "AMD", "COIN", "PLTR",
    "SNOW", "CRWD", "NET", "DDOG", "ZS",
    "SPY", "QQQ", "AVGO", "ASML", "TSM"
  ],
  "details": [
    {
      "symbol": "NVDA",
      "price": 145.50,
      "change_pct": 3.45,
      "date": "2026-01-27"
    },
    ...
  ]
}
```

---

## 🐛 Troubleshooting

### **ปัญหา: generate_watchlist.py รันช้า**
**สาเหตุ:** สแกน 503 หุ้นใช้เวลานาน
**แก้ไข:** ปกติครับ รอ 5-10 นาที

### **ปัญหา: Bot ไม่อ่าน watchlist.json**
**สาเหตุ:** ไฟล์ยังไม่ได้ Push ไป GitHub
**แก้ไข:** 
```bash
git add data/watchlist.json
git commit -m "Add watchlist"
git push
```

### **ปัญหา: watchlist.json ไม่มี**
**สาเหตุ:** ยังไม่ได้รัน `generate_watchlist.py`
**แก้ไข:** Bot จะใช้ default 10 หุ้นแทน (ไม่มีปัญหา)

---

## 📝 สรุป

**ระบบ 2 ชั้นนี้ให้คุณ:**
- ✅ สแกนหุ้น 503 ตัวทั้งหมด (Tier 1)
- ✅ ซื้อขายอัตโนมัติ 5 รอบ/วัน (Tier 2)
- ✅ ดู Dashboard แบบ Real-time (Tier 3)
- ✅ ไม่เสีย GitHub Actions Quota
- ✅ ไม่ต้องเปิดคอมทิ้งไว้

**Best of Both Worlds!** 🎉
