# Frontend Troubleshooting Guide

## Issue: Large Heart Icon on Blue Background

This typically happens when:
1. Dependencies are not installed
2. The dev server needs to be restarted
3. There's a build cache issue

## Solution Steps

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Clear Next.js Cache
```bash
# Delete the .next folder
rm -rf .next

# On Windows:
rmdir /s /q .next
```

### Step 3: Restart Dev Server
```bash
npm run dev
```

### Step 4: Clear Browser Cache
- Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Or open DevTools (F12) and right-click the refresh button, select "Empty Cache and Hard Reload"

## Expected Behavior

After following these steps, you should see:
1. **Login Page** - If not authenticated
   - MedAI logo with heart icon (normal size)
   - Username and password fields
   - Demo credentials section
   
2. **Dashboard** - If authenticated
   - Sidebar on the left with navigation
   - Main content area with KPI cards and charts
   - Professional dark theme with blue/purple accents

## Common Issues

### Issue: "next is not recognized"
**Solution:** Run `npm install` in the frontend directory

### Issue: Port 3000 already in use
**Solution:** 
```bash
# Find and kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
npm run dev -- -p 3001
```

### Issue: Styles not loading
**Solution:**
1. Check that `globals.css` is imported in `layout.tsx`
2. Verify `tailwind.config.js` content paths
3. Restart the dev server

### Issue: Components not rendering
**Solution:**
1. Check browser console for errors (F12)
2. Verify all imports are correct
3. Check that all component files exist

## Verification Checklist

- [ ] Node modules installed (`node_modules` folder exists)
- [ ] Dev server running without errors
- [ ] Browser console shows no errors
- [ ] Can see login page or dashboard
- [ ] Styles are applied correctly
- [ ] Navigation works

## Still Having Issues?

Check the browser console (F12) for specific error messages and share them for more targeted help.
