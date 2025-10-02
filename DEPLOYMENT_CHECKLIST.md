# Deployment Checklist for Production

## Pre-Deployment Steps

### 1. Frontend (Vercel)
- [ ] Run `npm run build` locally to verify build succeeds
- [ ] Check build output shows chunked bundles (react-vendor, markdown, ui-vendor)
- [ ] Verify no build errors
- [ ] Push changes to GitHub/Git repository

### 2. Backend (Render)
- [ ] Verify `requirements.txt` includes all dependencies
- [ ] Test Flask-Caching installs correctly: `pip install Flask-Caching`
- [ ] Ensure environment variables are set in Render dashboard
- [ ] Check gunicorn starts: `gunicorn app:app`

## Deployment Steps

### Frontend (Vercel)

1. **Connect Repository** (if first time)
   - Go to Vercel dashboard
   - Import your Git repository
   - Select the `frontend` directory as root

2. **Configure Build Settings**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

3. **Environment Variables**
   ```
   VITE_API_URL=https://ai-agent-with-frontend.onrender.com
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Check deployment preview

### Backend (Render)

1. **Configure Service**
   ```
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

2. **Environment Variables**
   Set all required variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<your-secret-key>`
   - `GROQ_API_KEY=<your-key>` (or other LLM keys)
   - `GOOGLE_API_KEY=<your-key>` (if using)
   - Firebase credentials (if needed)

3. **Deploy**
   - Push to main/master branch
   - Render auto-deploys
   - Monitor build logs

## Post-Deployment Verification

### Frontend Tests
- [ ] Visit deployed URL (e.g., https://your-app.vercel.app)
- [ ] Check initial page load is fast (<3 seconds)
- [ ] Verify login/signup works
- [ ] Test chat functionality
- [ ] Check sidebar loads chat history
- [ ] Verify media upload works
- [ ] Test dark mode toggle
- [ ] Check mobile responsiveness

### Backend Tests
- [ ] Visit `/api/health` endpoint
- [ ] Verify returns `{"status": "ok"}`
- [ ] Test `/api/auth/check-auth` endpoint
- [ ] Send a test chat message
- [ ] Check logs for errors
- [ ] Verify database connections work
- [ ] Test file upload endpoint

### Performance Tests
1. **Lighthouse Audit**
   - Open Chrome DevTools
   - Run Lighthouse audit
   - Target scores:
     - Performance: >80
     - Accessibility: >90
     - Best Practices: >90

2. **Network Analysis**
   - Check initial bundle size (<500 KB total)
   - Verify chunks load on-demand
   - Check caching headers are present
   - Confirm GZIP compression is active

3. **Load Testing**
   - Test with multiple concurrent users
   - Verify response times <2 seconds
   - Check for memory leaks
   - Monitor Render metrics

## Troubleshooting

### Slow Loading Issues
1. Check Vercel build logs for errors
2. Verify environment variables are set correctly
3. Check browser DevTools Network tab:
   - Look for slow requests (>3s)
   - Check if chunks are cached properly
   - Verify backend API responds quickly

### CORS Errors
1. Verify frontend origin is in backend `allowed_origins`
2. Check backend CORS headers in Network tab
3. Ensure credentials are being sent: `withCredentials: true`

### Build Failures
1. **Frontend**: Check Node.js version (should be 18+)
2. **Backend**: Check Python version (should be 3.9+)
3. Verify all dependencies install correctly
4. Check for missing environment variables

### API Connection Issues
1. Verify backend URL in frontend `.env.production`
2. Check Render service is running
3. Test backend health endpoint directly
4. Check firewall/security group settings

## Rollback Plan

If deployment fails:

### Frontend
```bash
# Revert to previous Vercel deployment
vercel rollback
```
Or use Vercel dashboard to rollback to previous deployment

### Backend
1. Go to Render dashboard
2. Select previous deployment from history
3. Click "Redeploy"

## Monitoring & Maintenance

### Daily Checks
- [ ] Check error logs in Render
- [ ] Monitor response times
- [ ] Verify user can access the app

### Weekly Checks
- [ ] Review Vercel analytics
- [ ] Check for dependency updates
- [ ] Monitor API usage
- [ ] Review error rates

### Monthly Maintenance
- [ ] Update dependencies
- [ ] Run security audit: `npm audit`
- [ ] Review and optimize slow queries
- [ ] Clean up old chat history
- [ ] Check disk usage on Render

## Performance Metrics to Track

### Frontend
- **First Contentful Paint (FCP)**: <1.5s
- **Time to Interactive (TTI)**: <3.5s
- **Largest Contentful Paint (LCP)**: <2.5s
- **Cumulative Layout Shift (CLS)**: <0.1
- **First Input Delay (FID)**: <100ms

### Backend
- **Health Check Response**: <500ms
- **Auth Check Response**: <1s
- **Chat Response**: <5s (depending on AI processing)
- **Database Query**: <500ms
- **File Upload**: <3s for 5MB

## Success Criteria

Deployment is successful if:
- ✅ App loads in production without errors
- ✅ Users can login/register
- ✅ Chat messages send and receive
- ✅ Page load time <3 seconds
- ✅ No console errors in production
- ✅ All API endpoints respond correctly
- ✅ Mobile experience is smooth
- ✅ Lighthouse score >80

## Contact & Support

If issues persist:
1. Check application logs
2. Review error messages
3. Test in incognito mode
4. Try different browsers/devices
5. Check network connectivity

## Notes

- Production builds are optimized and minified
- Console logs are removed in production
- Source maps are disabled for security
- All optimizations are automatic
- No code changes needed for local development
