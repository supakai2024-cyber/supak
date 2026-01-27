# StockRobo-US01: Push Phase 3 Updates to GitHub
# Created: 2026-01-27

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  StockRobo-US01: Git Push Script" -ForegroundColor Cyan
Write-Host "  Phase 3: Dashboard & Combined Strategy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a git repository!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Checking Git Status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "[2/5] Adding all new and modified files..." -ForegroundColor Yellow

# Add Dashboard files
git add dashboard/

# Add Watchlist generators
git add generate_watchlist.py
git add generate_top25_watchlist.py
git add generate_combined_watchlist.py

# Add updated Phase 2 file
git add run_phase2_gh_action.py

# Add Documentation
git add PHASE3_SUMMARY.md
git add TWO_TIER_SYSTEM.md
git add TOP25_SYSTEM.md
git add COMBINED_STRATEGY.md
git add ROADMAP.md

# Add data (if exists)
if (Test-Path "data/portfolio_state.json") {
    git add data/portfolio_state.json
}

Write-Host ""
Write-Host "[3/5] Showing what will be committed..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "[4/5] Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
Phase 3: Dashboard & Combined Strategy System

New Features:
- Dashboard (GitHub Pages ready)
  - Portfolio overview cards
  - Performance charts (Chart.js)
  - Positions & trades tables
  - Auto-refresh (30s)
  - Responsive design

- Watchlist Generators
  - generate_watchlist.py (503 → Top 20)
  - generate_top25_watchlist.py (5-criteria scoring)
  - generate_combined_watchlist.py (CDC + Fibo)

- Combined Strategy
  - CDC Action Zone (Trend Following)
  - Fibonacci Retracement (Mean Reversion)
  - 50-78.6% pullback zone

Updates:
- run_phase2_gh_action.py: Load watchlist.json dynamically
- ROADMAP.md: Phase 3 progress updated

Documentation:
- PHASE3_SUMMARY.md
- TWO_TIER_SYSTEM.md
- TOP25_SYSTEM.md
- COMBINED_STRATEGY.md
- dashboard/README.md
- dashboard/DEPLOYMENT.md
"@

git commit -m $commitMessage

Write-Host ""
Write-Host "[5/5] Pushing to GitHub..." -ForegroundColor Yellow
git push

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to GitHub → Settings → Pages" -ForegroundColor White
Write-Host "2. Set Source: Branch 'main', Folder '/dashboard'" -ForegroundColor White
Write-Host "3. Wait 1-2 minutes for deployment" -ForegroundColor White
Write-Host "4. Access dashboard at: https://[username].github.io/[repo-name]/" -ForegroundColor White
Write-Host ""
Write-Host "Optional:" -ForegroundColor Cyan
Write-Host "- Run: python generate_combined_watchlist.py" -ForegroundColor White
Write-Host "- Then: git add data/watchlist.json && git commit -m 'Add watchlist' && git push" -ForegroundColor White
Write-Host ""
