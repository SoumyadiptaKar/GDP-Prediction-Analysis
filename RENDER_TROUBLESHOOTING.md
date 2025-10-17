# Render.com Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Missing Dependencies Error (ModuleNotFoundError)

**Problem**: Your app fails to start with errors like:

```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution**:

- Make sure all required packages are in `requirements-production.txt`
- The fixed version includes all necessary dependencies:
  - scikit-learn (for ML functionality)
  - scipy (for scientific computing)
  - lightgbm (for advanced ML models)

### 2. SQLite CLI Not Available Error

**Problem**: Your app fails to start with errors like:

```
SQLite CLI not available. Please install SQLite.
```

**Solution**:

- The code has been updated to use Python's built-in sqlite3 module as fallback
- No additional installation needed - Python includes SQLite support
- The app will automatically detect and use the best available method

### 3. Build Configuration

**Render Settings You Need**:

- **Build Command**: `pip install -r requirements-production.txt`
- **Start Command**: `gunicorn wsgi:app`
- **Environment**: `Python 3.11` (or latest)

### 4. Environment Variables

Set these in Render dashboard:

- `FLASK_ENV=production`
- `PYTHON_VERSION=3.11.0` (if needed)

### 5. File Structure Check

Make sure these files exist in your repository root:

- `wsgi.py` ✓
- `requirements-production.txt` ✓ (updated with all dependencies)
- `app.py` ✓
- All your other application files

### 6. Quick Deployment Steps

1. **Push Updated Code to GitHub**:

   ```bash
   git add .
   git commit -m "Fix production dependencies for Render deployment"
   git push origin main
   ```

2. **Trigger Redeploy in Render**:

   - Go to your Render dashboard
   - Click "Manual Deploy" > "Deploy latest commit"
   - Or wait for auto-deploy if enabled

3. **Monitor Logs**:
   - Watch the build and deploy logs in Render dashboard
   - Look for successful installation of all packages

### 7. Expected Successful Deploy Log

You should see something like:

```
Installing collected packages: ... scikit-learn, lightgbm ...
Successfully installed Flask-2.3.3 pandas-2.1.1 scikit-learn-1.3.0 ...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Using worker: sync
[INFO] Booting worker with pid: 7
Database connection test successful
```

### 8. Alternative Quick Fix

If you still have issues, try this minimal requirements-production.txt:

```
Flask==2.3.3
pandas==2.1.1
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.17.0
gunicorn==21.2.0
```

## Next Steps

After successful deployment:

1. Test your application URLs
2. Check that all features work
3. Monitor performance in Render dashboard

The main issue was the commented-out scikit-learn dependency. The updated requirements file should resolve the deployment error.
