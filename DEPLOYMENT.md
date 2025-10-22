# Deployment Guide - Streamlit Cloud

Deploy your Low Hold Betting Simulator to Streamlit Cloud for free hosting and sharing.

## Prerequisites

- GitHub account
- Code pushed to a GitHub repository
- Streamlit Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))

## Quick Deployment Steps

### 1. Prepare Your Repository

Ensure these files are in your repository:
- ✅ `app.py` - The Streamlit application
- ✅ `monte_carlo_betting_simulator.py` - Core simulation engine
- ✅ `requirements.txt` - Python dependencies

### 2. Push to GitHub

```bash
# Make sure all changes are committed and pushed
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set the branch (e.g., `claude/monte-carlo-betting-simulator-011CULGUqu7KEFk65rcMZaKS` or `main`)
5. Set main file path: `app.py`
6. Click "Deploy"!

### 4. Your App is Live!

Streamlit will:
- Install dependencies from `requirements.txt`
- Start your app
- Give you a public URL (e.g., `https://your-app.streamlit.app`)

## Configuration Options

### App Settings (Optional)

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
```

### Secrets Management

If you need to store secrets (not required for this app):

1. Go to your app settings on Streamlit Cloud
2. Click "Secrets"
3. Add key-value pairs in TOML format

## Performance Optimization

For public deployment, consider:

1. **Limit Max Simulations**
   Edit `app.py` line with select_slider:
   ```python
   options=[1000, 2500, 5000, 10000]  # Remove 25000, 50000
   value=5000
   ```

2. **Add Caching**
   Already implemented with function imports, but you can add:
   ```python
   @st.cache_data
   def run_simulation(config):
       return run_monte_carlo(config)
   ```

3. **Resource Limits**
   Streamlit Cloud free tier has:
   - 1 GB RAM
   - 1 CPU core
   - Should handle up to 10k simulations easily

## Updating Your App

App auto-updates when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update simulation parameters"
git push origin main

# Streamlit Cloud will automatically redeploy
```

## Sharing Your App

Once deployed, you can:
- Share the public URL with anyone
- Embed in websites
- No authentication required (public by default)

## Troubleshooting

### Build Fails

**Check logs** in Streamlit Cloud dashboard

**Common issues:**
- Missing dependencies in `requirements.txt`
- Import errors (check file paths)
- Memory limits exceeded (reduce default simulations)

### App is Slow

- Reduce default number of simulations
- Add progress indicators (already included)
- Consider caching results

### Import Errors

Make sure both files are in the same directory:
```
your-repo/
├── app.py
├── monte_carlo_betting_simulator.py
├── requirements.txt
└── README.md
```

## Free Tier Limits

Streamlit Cloud Community (free):
- **Resources**: 1 GB RAM, 1 CPU
- **Apps**: Up to 3 public apps
- **Sleep mode**: Apps sleep after inactivity
- **Auto-wake**: Apps wake when visited

This is perfect for your simulator - can handle 5-10k simulations easily.

## Advanced: Custom Domain

For custom domains (requires paid plan):
1. Upgrade to Streamlit Cloud Pro
2. Add domain in settings
3. Update DNS records

## Support

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started)

---

**Your app URL will be something like:**
`https://low-hold-betting-simulator.streamlit.app`

Share it with anyone who wants to analyze bonus conversion strategies! 🚀
