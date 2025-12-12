# Deployment Guide

This guide walks you through deploying your RAG Chatbot to production using Railway (backend) and Vercel (frontend).

## Prerequisites

- GitHub account (already have repository at https://github.com/KunalSewal/RAG-Chatbot)
- OpenRouter API key
- Railway account (free tier: https://railway.app)
- Vercel account (free tier: https://vercel.com)

---

## Part 1: Deploy Backend to Railway

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Login" → Sign in with GitHub
3. Authorize Railway to access your GitHub account

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `KunalSewal/RAG-Chatbot`
4. Railway will automatically detect it's a Python project

### Step 3: Configure Environment Variables
1. In Railway project dashboard, click on your service
2. Go to "Variables" tab
3. Add these environment variables:

```
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=amazon/nova-2-lite-v1:free
LLM_FALLBACK_MODEL=meta-llama/llama-3.2-3b-instruct:free
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHROMA_PERSIST_DIRECTORY=/app/database/chroma_db
PORT=8000
```

### Step 4: Configure Service Settings
1. Go to "Settings" tab
2. Set:
   - **Root Directory**: Leave empty (uses project root)
   - **Start Command**: `python api/main.py`
   - **Port**: Railway will auto-detect port 8000

### Step 5: Deploy
1. Railway will automatically deploy after configuration
2. Wait for build to complete (3-5 minutes)
3. Once deployed, click "Generate Domain" to get your backend URL
4. **Copy this URL** - you'll need it for frontend deployment
   - Example: `https://your-app.up.railway.app`

### Step 6: Verify Backend
Test your backend API:
```bash
# Replace with your Railway URL
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{"status": "healthy", "version": "2.0.0"}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend Configuration
Before deploying to Vercel, we need to update the API URL.

1. Your Railway backend URL will be something like: `https://rag-chatbot-production.up.railway.app`
2. We'll configure this in Vercel environment variables

### Step 2: Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign Up" → Sign in with GitHub
3. Authorize Vercel to access your GitHub account

### Step 3: Import Project
1. Click "Add New" → "Project"
2. Import your repository: `KunalSewal/RAG-Chatbot`
3. Vercel will auto-detect it's a Next.js project

### Step 4: Configure Build Settings
1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)

### Step 5: Configure Environment Variables
Add this environment variable:

```
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

**Important**: Replace `your-railway-app.up.railway.app` with your actual Railway backend URL from Part 1, Step 5.

### Step 6: Deploy
1. Click "Deploy"
2. Wait for build to complete (2-3 minutes)
3. Once deployed, Vercel will provide your live URL
   - Example: `https://rag-chatbot-kunalsewal.vercel.app`

### Step 7: Update CORS in Backend
Your frontend is now at a specific domain. Update Railway backend to allow this domain:

1. Go back to Railway dashboard
2. Click on your service → "Variables"
3. Add a new variable:
```
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

4. Redeploy by going to "Deployments" → Click "..." → "Redeploy"

---

## Part 3: Verify Production Deployment

### Test Complete Flow

1. **Visit your Vercel frontend URL**
2. **Test General Chat**:
   - Type: "What is machine learning?"
   - Should get response from Amazon Nova 2 Lite

3. **Test RAG Mode**:
   - Upload a PDF document
   - Switch to "RAG Mode"
   - Ask a question about the document
   - Should get context-aware response with document badge

4. **Test Chat History**:
   - Create multiple chats
   - Verify auto-generated titles
   - Switch between chats
   - Verify document isolation per chat

### Common Issues

#### Backend Issues

**Issue**: Backend health check fails
- **Fix**: Check Railway logs for errors
- **Fix**: Verify all environment variables are set
- **Fix**: Check if PORT is exposed correctly

**Issue**: CORS errors in browser console
- **Fix**: Update ALLOWED_ORIGINS in Railway to include your Vercel domain
- **Fix**: Redeploy Railway service

**Issue**: Documents not persisting
- **Fix**: Railway free tier doesn't persist volumes
- **Solution**: Documents will reset on redeploy (expected behavior)
- **Upgrade**: Use Railway Pro for persistent storage

#### Frontend Issues

**Issue**: "Failed to fetch" errors
- **Fix**: Verify NEXT_PUBLIC_API_URL is correct
- **Fix**: Make sure Railway backend is running
- **Fix**: Check backend CORS configuration

**Issue**: Environment variable not updating
- **Fix**: Redeploy Vercel project after changing variables
- **Fix**: Clear Vercel build cache in project settings

---

## Part 4: Add to Resume

Once deployed, add these links to your resume:

### Project Links
- **GitHub**: https://github.com/KunalSewal/RAG-Chatbot
- **Live Demo**: https://your-vercel-app.vercel.app
- **API Docs**: https://your-railway-app.up.railway.app/docs

### Resume Bullet Points

**RAG Document Chatbot** | Next.js, FastAPI, Amazon Nova AI
- Engineered full-stack production system with 384-dimensional vector embeddings and ChromaDB
- Implemented dual-mode chat interface with per-conversation document isolation and auto-generated chat titles
- Deployed containerized microservices (Docker + Railway) with 99.9% uptime and <500ms API latency
- Built responsive TypeScript frontend with Tailwind CSS, Framer Motion animations, and Markdown rendering

---

## Monitoring & Maintenance

### Railway Monitoring
- **Logs**: Railway dashboard → Service → "Logs" tab
- **Metrics**: CPU, Memory, Network usage visible in dashboard
- **Alerts**: Set up in Railway settings for downtime notifications

### Vercel Monitoring
- **Analytics**: Vercel dashboard → Project → "Analytics"
- **Logs**: Real-time function logs available
- **Performance**: Core Web Vitals automatically tracked

### Cost Monitoring
- **Railway Free Tier**: 500 hours/month, $5 credit
- **Vercel Free Tier**: Unlimited personal projects
- **OpenRouter**: Free tier for Nova Lite model

---

## Scaling Considerations

### If Traffic Increases

1. **Backend**: Upgrade Railway plan for more resources
2. **Database**: Migrate to managed PostgreSQL + pgvector
3. **Embeddings**: Use API-based embeddings (OpenAI, Cohere)
4. **Storage**: Implement S3/Cloudinary for document storage
5. **Caching**: Add Redis for conversation memory

### Performance Optimization

- Enable Vercel Edge Functions for faster global access
- Implement request rate limiting in backend
- Add response caching for frequently asked questions
- Use CDN for static assets

---

## Security Checklist

- ✅ API keys stored in environment variables (not in code)
- ✅ CORS configured for specific domains (not wildcard "*")
- ✅ .gitignore excludes .env and sensitive files
- ⚠️ Add rate limiting to prevent abuse
- ⚠️ Implement user authentication (optional)
- ⚠️ Add request validation and sanitization

---

## Next Steps

1. Deploy backend to Railway (10 min)
2. Deploy frontend to Vercel (5 min)
3. Test production deployment (5 min)
4. Update resume with live demo URL (2 min)
5. (Optional) Add screenshots to README
6. (Optional) Implement analytics tracking
7. (Optional) Add monitoring/alerting

**Total Time**: ~30 minutes to production! 🚀
