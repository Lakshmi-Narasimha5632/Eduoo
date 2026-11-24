# Eduoo - AI-Powered Career Intelligence & Preparation Platform

Eduoo is a modern, full-stack AI career development platform designed to accelerate tech career readiness. It brings together unified telemetry across developer platforms, personalized daily study planning, resume parsing with ATS scoring, and a complete three-pillar AI Career Preparation Suite: **Job Interviews**, **Communication Practice**, and **Skill Assessment**.

---

## 🌟 Key Architecture & Capabilities

### 1. AI Career Preparation Suite
- **Job Interviews**:
  - Customizable target roles (Full Stack, Frontend, Backend, Python Developer, Data Scientist, AI/ML, etc.) and experience levels (Fresher, Intermediate, Experienced).
  - Interview categories: HR, Technical, Project-Based, Company-Specific, Full Mock.
  - Interactive interviewer interface with text and real-time speech/microphone input.
  - Contextual follow-up questions generated dynamically based on actual candidate answers.
  - Granular answer evaluation across technical accuracy, communication, confidence, and relevance with comprehensive end-of-interview scorecards.
- **Communication Practice**:
  - 10 targeted modules: Daily Practice, Conversational AI, Real-Time Voice, Self-Introduction, Group Discussion, Public Speaking, Pronunciation, Vocabulary, Grammar, and Workplace Scenarios.
  - High-fidelity speech recognition and evaluation of actual spoken sentences.
  - Feedback on pronunciation, grammar, fluency, vocabulary, speaking pace, and confidence.
- **Skill Assessment**:
  - LeetCode and HackerRank style coding challenges across Easy, Medium, and Hard tiers.
  - Multi-language support (Python, Java, JavaScript, C, C++).
  - Online code editor with "Run Code" and "Submit Code" against visible and hidden test cases.
  - Execution engine providing run-time diagnostics, memory usage, and execution timing.
  - Technical MCQs and domain quizzes (Python, JavaScript, DSA, SQL, Logical Reasoning).
  - Rich analytics: problems solved, accuracy, topic breakdown, and streak metrics.

### 2. Unified Developer Telemetry
- Real-time connector integrations across **LeetCode**, **GitHub**, **Duolingo**, **HackerRank**, **CodeChef**, and **LinkedIn**.
- Fault-tolerant connectors with graceful fallback and non-blocking sync.

### 3. Adaptive Daily Task Planner
- Generates dynamic, day-by-day customized learning schedules targeted at detected skill gaps.
- Day-specific variation algorithms ensuring unique tasks each day without monotonous repetition.
- Automated completion tracking and streak maintenance.

### 4. Resume Intelligence & ATS Scoring
- Native PDF extraction with intelligent regex and heuristic segmentation.
- Extracts candidate name, email, phone number, experience, education, and technical skills.
- Dynamic ATS matching score, keyword density, and custom recommendations derived strictly from the uploaded resume.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+, Django 6.0+, Django REST Framework, SimpleJWT, Gunicorn, WhiteNoise |
| **Database** | PostgreSQL (Render production) / SQLite (local development) with `dj-database-url` |
| **AI Integration** | TokenHarbor, Google Gemini, OpenAI, or local intelligent fallback |
| **Frontend** | React 18, React Router 6, Tailwind CSS, Lucide Icons, Recharts |
| **Deployment** | GitHub (Source), Render (Backend Web Service & PostgreSQL), Vercel (Frontend SPA) |

---

## 🚀 Deployment Guide: GitHub, Render & Vercel

This repository is structured as a clean monorepo ready for immediate deployment:
```
Eduoo_new/
├── backend/          # Django REST Framework backend
│   ├── build.sh      # Render deployment build script
│   ├── manage.py
│   ├── requirements.txt
│   └── eduoo/settings.py
├── frontend/         # React SPA frontend
│   ├── vercel.json   # Vercel SPA routing configuration
│   ├── package.json
│   └── src/
├── render.yaml       # Render Blueprint configuration
├── vercel.json       # Root Vercel routing configuration
└── README.md
```

---

### Step 1: Push Code to GitHub

1. If you haven't already created a GitHub repository, create a new repository on [GitHub](https://github.com/new) (e.g. `eduoo` or `eduoo-app`).
2. Open your terminal in the project root:
   ```bash
   # Add your GitHub repository as remote origin
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/<YOUR-REPO-NAME>.git

   # Push to main branch
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy Backend to Render

1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Configure the Web Service settings:
   - **Name**: `eduoo-backend` (or your preferred name)
   - **Region**: Choose the region closest to you (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
     *(Or: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`)*
   - **Start Command**: `gunicorn eduoo.wsgi:application`
   - **Plan**: `Free`
5. *(Optional but Recommended)* Create a managed PostgreSQL database on Render:
   - Click **New +** -> **PostgreSQL**.
   - Copy the **Internal Database URL**.
6. Set the **Environment Variables** in Render (under the **Environment** tab):
   | Variable | Recommended Value | Description |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.12.8` | Python runtime version |
   | `DEBUG` | `False` | Disables debug mode in production |
   | `SECRET_KEY` | *(generate a strong 50+ char string)* | Django cryptographic key |
   | `ALLOWED_HOSTS` | `*` | Or `.onrender.com` |
   | `FRONTEND_URL` | `https://<your-vercel-app>.vercel.app` | Vercel frontend URL for CORS & CSRF |
   | `DATABASE_URL` | *(your Render PostgreSQL internal URL)* | Automatically configured if database is attached |
   | `AI_PROVIDER` | `token_harbor` *(or `gemini` / `openai`)* | Chosen AI service provider |
   | `TOKEN_HARBOR_API_KEY` | `your-token-harbor-key` | API key if using TokenHarbor |
   | `GEMINI_API_KEY` | `your-gemini-key` | API key if using Google Gemini |
7. Click **Create Web Service**.
8. Render will run `./build.sh`, collect static files with WhiteNoise, apply database migrations, and boot up Gunicorn.
9. Note down your backend URL (e.g., `https://eduoo-backend.onrender.com`).
   - You can test it by visiting: `https://eduoo-backend.onrender.com/api/health/`

---

### Step 3: Deploy Frontend to Vercel

1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Select your GitHub repository and click **Import**.
4. In the **Configure Project** screen:
   - **Project Name**: `eduoo-frontend` (or your preferred name)
   - **Framework Preset**: `Create React App`
   - **Root Directory**: Click **Edit** and select `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `build` (default)
5. Under **Environment Variables**, add:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `REACT_APP_API_URL` | `https://<your-backend-app>.onrender.com/api` | Your Render backend API URL (include `/api`) |
6. Click **Deploy**.
7. Vercel will install dependencies, compile the production bundle, and deploy the application.
8. Once finished, Vercel will provide your live URL (e.g., `https://eduoo-frontend.vercel.app`).

---

### Step 4: Final Connection (CORS / CSRF)

1. Return to your **Render Dashboard** -> `eduoo-backend` -> **Environment**.
2. Make sure `FRONTEND_URL` is set to your actual Vercel domain:
   ```
   FRONTEND_URL=https://eduoo-frontend.vercel.app
   ```
3. Save changes (Render will automatically redeploy with the updated CORS configuration).
4. Open your Vercel URL in your browser and verify:
   - Registration and login work smoothly.
   - Job Interviews, Communication Practice, and Skill Assessment execute with real-time feedback.
   - Resume upload and ATS scoring extract accurate data.
   - Daily tasks load with day-by-day dynamic generation.

---

## 💻 Local Development Setup

### Backend (Django)
```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
# Windows:
..\.venv\Scripts\activate
# Linux/macOS:
source ../.venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start development server
python manage.py runserver 8000
```
Backend API will be available at: `http://localhost:8000/api/`  
Health check endpoint: `http://localhost:8000/api/health/`

### Frontend (React)
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env if needed (defaults to http://localhost:8000/api)
# REACT_APP_API_URL=http://localhost:8000/api

# 4. Start local development server
npm start
```
Frontend UI will be available at: `http://localhost:3000/`

---

## 🧪 Testing & Verification

### Run Backend Pytest Suite
```bash
cd backend
pytest -v
```
Or test specific suites:
```bash
pytest backend/interviews/test_career_platform.py -v
pytest backend/tasks/tests.py backend/resume/tests.py -v
```

### Run Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 📄 License
This project is proprietary and maintained for **Eduoo AI Career Systems**. All rights reserved.
