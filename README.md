# LegacyMind AI

**Modernize Legacy Software, Securely.**

LegacyMind AI is a working MVP inspired by the hackathon pitch. It lets a user upload a legacy codebase, analyze its files, inspect dependencies, run lightweight security checks, generate documentation, and preview a modernization plan.

The pitch describes an eight-stage pipeline:

1. Upload Legacy Code
2. AI Understands Code
3. Dependency Analysis
4. Security Scan
5. Documentation Generation
6. AI Code Modernization
7. Testing & Verification
8. Deployment

This repository implements a runnable MVP of stages 1–6 and a basic verification report. The architecture is intentionally modular so Tree-sitter, GraphRAG/Neo4j, LangGraph, Semgrep, and an LLM can be added incrementally.

## Project structure

```text
legacymind-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── analyzer.py
│   │   └── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── style.css
├── sample_legacy_code/
│   ├── banking.py
│   └── billing.cob
├── .env.example
└── .gitignore
```

## Run locally

### Backend

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp ../.env.example .env   # Or create .env and add GROQ_API_KEY=your_key
uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

The Vite frontend proxies `/api` requests to the FastAPI server.

## What the MVP does

- Upload `.zip`, `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.cob`, `.cbl`, `.f`, and `.f90` files.
- Extract and inspect source files.
- Count files and lines.
- Detect common imports/includes.
- Build a lightweight dependency list.
- Detect simple high-risk patterns such as `eval`, shell execution, hard-coded passwords/API keys, and SQL string concatenation.
- Generate a human-readable documentation summary.
- Generate a modernization preview for selected legacy patterns.
- Produce a verification summary.

## Important

This is a hackathon MVP, not a production-grade autonomous modernization system. Security findings are heuristic and should not be treated as a complete security audit. Modernized code must be reviewed and tested before deployment.

## Team

- Shreyansh Keshari — AI / Backend
- Utsav Singh — Full-Stack & DevOps
- Shaurya Verma — Frontend & Security
