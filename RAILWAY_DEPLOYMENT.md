# Railway Deployment Guide for E-Connect Backend

## Fixed Issues

### 1. JWT Algorithm Error ✅
**Error:** `Algorithm not supported`

**Root Cause:** Environment variable `algorithm` was being set to an invalid value on Railway.

**Fix:** Updated `backend/auth/auth_handler.py` to:
- Validate JWT algorithm against allowed algorithms
- Fallback to `HS256` if invalid
- Support both `JWT_ALGORITHM`/`algorithm` and `JWT_SECRET`/`secret` variable names

### 2. DateTime Serialization Error ✅
**Error:** `Object of type datetime is not JSON serializable`

**Root Cause:** MongoDB returns datetime objects that cannot be directly serialized to JSON.

**Fix:** 
- Updated `cleanid()` function in `Mongo.py` to convert datetime objects to ISO format strings
- Updated `/Gsignin` and `/admin_Gsignin` endpoints to use `json_util` for proper serialization

### 3. Port Configuration ✅
**Issue:** Railway uses port 10000 (set via `PORT` environment variable)

**Status:** Already configured correctly in `Server.py` - reads from `PORT` environment variable

## Railway Environment Variables Setup

### Required Environment Variables

Set these in your Railway project settings (Variables tab):

```bash
# JWT Configuration (use BOTH formats for compatibility)
JWT_SECRET=013aafb560ba561a351e913d3bca0829a290b552
secret=013aafb560ba561a351e913d3bca0829a290b552
JWT_ALGORITHM=HS256
algorithm=HS256

# MongoDB Configuration
MONGODB_URI=mongodb+srv://econnect_user:econnect_user@cluster0.dzthu7w.mongodb.net/RBG_AI?retryWrites=true&w=majority&appName=Cluster0

# Server Configuration (Railway sets PORT automatically, but you can override)
PORT=10000
HOST=0.0.0.0

# CORS Origins (Add all your frontend URLs, comma-separated)
ALLOWED_ORIGINS=https://e-connect-host-frontend.vercel.app,https://econnect-frontend-wheat.vercel.app,http://localhost:5173,http://localhost:5174
```

### Important Notes:

1. **Railway PORT**: Railway automatically sets the `PORT` environment variable. The app will use 10000 if you set it, or Railway's default.

2. **Frontend URLs**: Make sure to add ALL your Vercel deployment URLs to `ALLOWED_ORIGINS`.

3. **MongoDB URI**: Ensure your MongoDB cluster allows connections from Railway's IP addresses (use `0.0.0.0/0` for development).

4. **JWT Variables**: Both old (`secret`, `algorithm`) and new (`JWT_SECRET`, `JWT_ALGORITHM`) formats are supported for backward compatibility.

## Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Fix JWT algorithm and datetime serialization issues"
   git push origin main
   ```

2. **Railway Auto-Deploy:**
   - Railway will automatically detect the changes and redeploy
   - Check the deployment logs for any errors

3. **Verify Deployment:**
   - Check Railway logs: `JWT Configuration Loaded - Algorithm: HS256`
   - Test Google Sign-In from your frontend
   - Check for successful authentication

## Testing the Fix

### Test Google Sign-In:
1. Open your frontend at: https://e-connect-host-frontend.vercel.app
2. Click "Sign in with Google"
3. Complete Google authentication
4. Should redirect to dashboard without errors

### Expected Log Output (Railway):
```
JWT Configuration Loaded - Algorithm: HS256, Secret Length: 42
CORS Allowed Origins: ['https://e-connect-host-frontend.vercel.app', ...]
Starting without SSL on port 10000
```

## Troubleshooting

### If you still get "Algorithm not supported":
1. Go to Railway project settings
2. Variables tab
3. Ensure `JWT_ALGORITHM=HS256` and `algorithm=HS256` are set
4. Redeploy the service

### If you get CORS errors:
1. Check that your frontend URL is in `ALLOWED_ORIGINS`
2. Format: `https://your-app.vercel.app` (no trailing slash)
3. Redeploy after adding origins

### If you get "datetime not serializable":
1. This should be fixed with the `cleanid()` update
2. Check Railway logs for the specific error
3. The fix handles datetime, date, and ObjectId serialization

## Backend URL

Your backend is deployed at:
```
https://e-connect-host-production.up.railway.app
```

Port: 10000 (Railway handles this internally)

## Frontend Configuration

Ensure your frontend uses the correct backend URL in `frontend/src/Utils/Resuse.js`:
```javascript
const defaultUrl = "https://e-connect-host-production.up.railway.app";
```

## Files Modified

1. `backend/auth/auth_handler.py` - JWT algorithm validation and fallback
2. `backend/Mongo.py` - Enhanced `cleanid()` function for datetime serialization
3. `backend/Server.py` - Updated CORS origins to use environment variables
4. `backend/.env.example` - Updated with correct variable names and port

## Next Steps

1. ✅ Commit and push changes to GitHub
2. ✅ Wait for Railway auto-deployment
3. ✅ Set environment variables in Railway dashboard
4. ✅ Test Google Sign-In from frontend
5. ✅ Monitor Railway logs for any issues

---

**Deployment Date:** October 10, 2025
**Backend URL:** https://e-connect-host-production.up.railway.app
**Port:** 10000
