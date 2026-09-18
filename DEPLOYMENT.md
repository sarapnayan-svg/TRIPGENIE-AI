# TripGenie AI — Production Deployment Guide

This document outlines the end-to-end procedure for deploying TripGenie AI to production cloud infrastructure.

---

## 1. Architecture Overview

- **Frontend**: React 19 Single-Page Application (SPA) bundled with Vite 5.
- **Backend**: FastAPI (Python 3.11+) ASGI application powered by Uvicorn.
- **RAG Engine**: In-memory dense vector retrieval using `sentence-transformers` (`all-MiniLM-L6-v2`).
- **Database**: SQLite (local/ephemeral) or PostgreSQL (production-ready via `DATABASE_URL`).
- **LLM Integration**: Anthropic Claude API (`claude-3-5-sonnet-20241022`).

---

## 2. Prerequisites

1. **Git**: Repository cloned with frontend and backend subdirectories.
2. **Node.js**: v18.0+ or v20.0+ for frontend builds.
3. **Python**: 3.10+ or 3.11+ (recommended) for backend runtime.
4. **Anthropic API Key**: An active API key from [Anthropic Console](https://console.anthropic.com/).
5. **Hosting Accounts**:
   - Backend: Render, Railway, or any Docker/VM container platform.
   - Frontend: Vercel, Netlify, Cloudflare Pages, or Render Static Sites.

---

## 3. Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default / Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | Your secret Anthropic API key. |
| `LLM_MODEL` | No | `claude-3-5-sonnet-20241022` |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` |
| `TOP_K_RESULTS` | No | `6` |
| `WEATHER_API_KEY` | No | Optional OpenWeatherMap key (defaults to free Open-Meteo if empty). |
| `DATABASE_URL` | No | `sqlite:///./tripgenie.db` (or PostgreSQL connection URL). |
| `JWT_SECRET` | Recommended | Random 32+ char secret for user session tokens (`openssl rand -hex 32`). |
| `CORS_ORIGINS` | Recommended | Comma-separated list of deployed frontend URLs (e.g. `https://tripgenie.vercel.app`). |
| `PORT` | Auto | Cloud provider assigned port (e.g. `8000` or `$PORT`). |
| `HOST` | Auto | Binding address (`0.0.0.0`). |

### Frontend (`frontend/.env`)

| Variable | Required | Default / Description |
|---|---|---|
| `VITE_API_URL` | **Yes in Prod** | Full URL to your deployed backend API (e.g. `https://tripgenie-backend.onrender.com/api`). |
| `VITE_API_BASE_URL` | Optional | Alias for `VITE_API_URL`. Both conventions are supported. |

---

## 4. Backend Deployment Steps

### Option A: Render (Recommended for FastAPI + ML)

1. Sign in to [Render](https://render.com/).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Set the service settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python`
   - **Python Version**: `3.11.9`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
5. Under **Environment Variables**, add:
   - `ANTHROPIC_API_KEY` = `your-actual-api-key`
   - `JWT_SECRET` = `your-random-secret`
   - `CORS_ORIGINS` = `https://your-frontend-app.vercel.app` (update once frontend is deployed)
6. Click **Create Web Service**. Wait for the build and deployment to finish.
7. Note down your backend URL: `https://<your-backend-name>.onrender.com`.

### Option B: Docker Container (Railway, AWS ECS, Google Cloud Run)

1. Build the Docker image from the `backend/` directory:
   ```bash
   docker build -t tripgenie-backend ./backend
   ```
2. Run the container locally or push to your container registry:
   ```bash
   docker run -p 8000:8000 -e ANTHROPIC_API_KEY="your-key" tripgenie-backend
   ```

---

## 5. Frontend Deployment Steps

### Option A: Vercel (Recommended for React + Vite)

1. Sign in to [Vercel](https://vercel.com/).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository.
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. In **Environment Variables**, add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://<your-backend-name>.onrender.com/api`
6. Click **Deploy**. Vercel will build and publish your frontend.
7. Note down your frontend URL (e.g., `https://tripgenie.vercel.app`).

### Option B: Netlify / Render Static Site

1. Set **Build Command**: `npm run build`
2. Set **Publish directory**: `dist`
3. Add `VITE_API_URL` pointing to your deployed backend API URL.

---

## 6. Connecting Frontend to Backend

1. Once your backend is deployed and healthy, copy its root or API URL.
2. In your frontend hosting platform's Environment Variables panel:
   - Set `VITE_API_URL` = `https://<your-backend-url>/api`
3. Redeploy your frontend so the new environment variable is baked into the client bundle.
4. In your backend hosting platform's Environment Variables panel:
   - Set `CORS_ORIGINS` = `https://<your-frontend-url>`
5. Trigger a quick restart or redeploy on the backend to apply CORS restriction.

---

## 7. How to Test Production Deployment

### 1. Verify Backend Sanity & Health
Open in your browser or curl:
- `https://<your-backend-url>/` → should return:
  ```json
  {"name": "TripGenie AI API", "version": "1.0.0", "status": "online", "health": "/api/health", "docs": "/docs"}
  ```
- `https://<your-backend-url>/api/health` → should return:
  ```json
  {"status": "ok", "known_destinations": ["Goa", "Jaipur", "Kerala", "Manali", "Rishikesh"]}
  ```

### 2. Verify Frontend Application
1. Open your production frontend URL in a browser.
2. Observe that the **System Online** indicator in the navigation header displays green.
3. Test planning a trip (e.g. Goa, 4 days, 2 travelers, ₹50,000 budget).
4. Verify the itinerary, day-by-day plan, budget breakdown, and recommended hotels render.
5. Click **Export PDF** to verify client-side PDF document generation.
6. Open the AI Chat drawer and send a test query (e.g. *"What are the best seafood spots in Goa?"*).
