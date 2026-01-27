# Deployment Guide: GitHub Pages

## 🚀 Quick Deploy to GitHub Pages

### Step 1: Push Dashboard to GitHub

```bash
# From project root
git add dashboard/ data/portfolio_state.json
git commit -m "Phase 3: Add Dashboard"
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/dashboard` (⚠️ Important!)
5. Click **Save**

### Step 3: Wait for Deployment

- GitHub will build your site (takes 1-2 minutes)
- You'll see a green checkmark when ready
- Your URL will be: `https://[username].github.io/[repo-name]/`

---

## 🔧 Alternative: Deploy from Root

If you want the dashboard at the root URL:

### Option A: Move files to root

```bash
# Copy dashboard files to root
cp dashboard/index.html ./
cp dashboard/styles.css ./
cp dashboard/dashboard.js ./

# Update data path in dashboard.js
# Change: const DATA_PATH = '../data/portfolio_state.json';
# To: const DATA_PATH = './data/portfolio_state.json';

# Commit and push
git add index.html styles.css dashboard.js
git commit -m "Move dashboard to root"
git push
```

Then in GitHub Pages settings:
- **Folder**: `/ (root)`

### Option B: Use docs folder

```bash
# Rename dashboard to docs
mv dashboard docs

# Commit and push
git add docs/
git commit -m "Rename dashboard to docs"
git push
```

Then in GitHub Pages settings:
- **Folder**: `/docs`

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. In GitHub Pages settings, add your domain
2. Create CNAME file:

```bash
echo "yourdomain.com" > dashboard/CNAME
git add dashboard/CNAME
git commit -m "Add custom domain"
git push
```

3. Update DNS records at your domain provider:
   - Type: `CNAME`
   - Name: `www` or `@`
   - Value: `[username].github.io`

---

## 🔍 Verify Deployment

### Check Build Status

1. Go to **Actions** tab
2. Look for "pages build and deployment"
3. Green checkmark = Success ✅
4. Red X = Failed ❌ (click to see logs)

### Test Your Dashboard

1. Open your GitHub Pages URL
2. You should see the dashboard
3. Check browser console (F12) for errors

---

## 🐛 Common Issues

### Issue: 404 Not Found

**Cause**: Wrong folder selected or files not in correct location

**Fix**:
```bash
# Verify files exist
ls dashboard/
# Should show: index.html, styles.css, dashboard.js, README.md

# Check folder setting in GitHub Pages
# Must be /dashboard (not /docs or /)
```

### Issue: Dashboard loads but no data

**Cause**: `portfolio_state.json` not accessible

**Fix**:
```bash
# Ensure data folder is committed
git add data/portfolio_state.json
git commit -m "Add portfolio state"
git push

# Update path in dashboard.js if needed
```

### Issue: Charts not showing

**Cause**: Chart.js CDN blocked or not loaded

**Fix**:
- Check internet connection
- Open browser console (F12) for errors
- Verify Chart.js CDN URL in index.html

### Issue: CORS errors

**Cause**: Trying to access local files directly

**Fix**:
- Use GitHub Pages (no CORS issues)
- Or use local server: `python -m http.server 8000`

---

## 🔄 Update Dashboard

### After Bot Runs

GitHub Actions automatically updates `portfolio_state.json`:

1. Bot runs → Updates `data/portfolio_state.json`
2. Commits changes to GitHub
3. GitHub Pages automatically rebuilds
4. Dashboard shows new data (refresh page)

### Manual Updates

```bash
# Make changes to dashboard files
# Then:
git add dashboard/
git commit -m "Update dashboard"
git push

# Wait 1-2 minutes for GitHub Pages to rebuild
```

---

## 📱 Mobile Access

Your dashboard is accessible from any device:

- 📱 **Mobile**: `https://[username].github.io/[repo-name]/`
- 💻 **Desktop**: Same URL
- 📱 **Tablet**: Same URL

Add to home screen on mobile for app-like experience!

---

## 🔒 Security Considerations

⚠️ **GitHub Pages is PUBLIC**

Your portfolio data will be visible to anyone with the URL.

**Options for privacy:**

1. **Use Private Repository** (GitHub Pro required)
2. **Add Authentication** (requires backend)
3. **Use Firebase** instead (with auth)
4. **Host on Private Server**

---

## ✅ Deployment Checklist

- [ ] Dashboard files created in `/dashboard` folder
- [ ] `portfolio_state.json` exists in `/data` folder
- [ ] Files committed and pushed to GitHub
- [ ] GitHub Pages enabled (Settings → Pages)
- [ ] Folder set to `/dashboard`
- [ ] Branch set to `main`
- [ ] Waited 1-2 minutes for deployment
- [ ] Tested URL in browser
- [ ] Dashboard loads correctly
- [ ] Data displays properly
- [ ] Charts render successfully

---

## 🎉 Success!

Your dashboard should now be live at:
`https://[your-username].github.io/[repo-name]/`

Example: `https://supakai2024-cyber.github.io/supak/`

---

**Next Steps:**
- Share your dashboard URL
- Monitor portfolio performance
- Consider upgrading to Firebase for real-time updates
