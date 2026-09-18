# Local Setup & Installation Guide — TripGenie AI

Follow these instructions to set up and run TripGenie AI locally on your development machine.

---

## 1. Prerequisites

- **Python**: 3.10, 3.11, or 3.12 installed
- **Node.js**: v18.0+ or v20.0+ (with `npm`)
- **Anthropic API Key**: For Claude LLM generation (obtain from [Anthropic Console](https://console.anthropic.com/))
- **Git** (optional, recommended for version control)

---

## 2. Repository Clone & Structure

```bash
git clone https://github.com/<your-username>/TripGenie-AI.git
cd TripGenie-AI
```

Project Directory Layout:
```text
TripGenie-AI/
├── backend/          # FastAPI ASGI Backend & RAG Engine
├── frontend/         # React 19 + Vite Frontend SPA
├── docs/             # Technical Documentation
├── render.yaml       # Cloud Deployment Blueprint
└── README.md         # Main Project Documentation
```

---

## 3. Backend Setup

### 3.1 Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Configure Environment Variables
Copy the template file to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and configure:
```env
# Required: Anthropic Claude API Key
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional configurations:
LLM_MODEL=claude-3-5-sonnet-20241022
DATABASE_URL=sqlite:///./tripgenie.db
JWT_SECRET=supersecretjwtstring12345
```

### 3.4 Start the Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- The backend will initialize the vector database, load embedding models, and start at: **`http://127.0.0.1:8000`**
- Interactive Swagger API Documentation: **`http://127.0.0.1:8000/docs`**
- Health check verification: **`http://127.0.0.1:8000/api/health`**

---

## 4. Frontend Setup

### 4.1 Install Node Dependencies
Open a separate terminal window:
```bash
cd frontend
npm install
```

### 4.2 Configure Environment Variables
Copy the frontend template:
```bash
cp .env.example .env
```
Ensure the API base URL points to your local backend:
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### 4.3 Start the Frontend Development Server
```bash
npm run dev
```
The application will be accessible at: **`http://localhost:5173/`**

---

## 5. Running Production Preview Locally

To test the exact production build locally:

1. **Build the Frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve the Production Build:**
   ```bash
   npm run preview
   ```
   Access the production bundle at: **`http://127.0.0.1:4173/`**

---

## 6. Running Automated Tests

### 6.1 Backend Validation Tests
Run unit tests for budget calculations and route computations:
```bash
cd backend

# Test 1: Deterministic Budget Planning Engine
python test_budget_planner.py

# Test 2: Verified GPS Spatial Engine & Distances
python test_locations.py

# Test 3: FastAPI Endpoints & Health Status
python -c "from fastapi.testclient import TestClient; from app.main import app; c = TestClient(app); print(c.get('/api/health').json())"
```

### 6.2 Frontend Lint & Build Test
```bash
cd frontend
npm run build
```
Ensure the output indicates `0 errors` and generates production bundles in `dist/`.
