# SentinelVision

Production-ready image moderation web application for Trust & Safety–style workflows. Multi-label classification (NSFW, violence, sexual content, hate symbols, drugs, self-harm) with configurable thresholds and natural-language explainability via image captioning.

## Features

- **Live web app**: Upload images via drag-and-drop or file picker; analyze and view results on the same page.
- **Risk verdict**: SAFE / REVIEW / BLOCK with configurable thresholds.
- **Per-category confidence**: Progress bars and scores (0–1) for each moderation category.
- **Explainability**: Short image description from a captioning model for transparency and auditability.
- **Backend**: FastAPI with clear API / inference / post-processing layers, structured JSON, error handling.
- **Frontend**: React (Vite) with a clean, professional UI.
- **Deployment**: Dockerized backend; environment-based configuration.

## Project structure

```
SentinelVision/
├── backend/                 # FastAPI + ML
│   ├── app/
│   │   ├── api/             # API layer (routes)
│   │   ├── services/        # Inference + post-processing
│   │   ├── schemas/         # Pydantic response models
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── run.py
├── frontend/                # React (Vite)
│   ├── src/
│   │   ├── components/      # ImageUpload, ResultsDashboard
│   │   ├── api/            # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/
│   └── example-response.json
└── README.md
```

## Setup

### Prerequisites

- **Backend**: Python 3.11+, pip
- **Frontend**: Node.js 18+, npm
- **Optional**: Docker for backend deployment

### Backend

1. Create a virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy environment template and adjust if needed:

   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env  # macOS/Linux
   ```

3. (Optional) For GPU: set `DEVICE=cuda` in `.env` and ensure PyTorch with CUDA is installed.

### Frontend

```bash
cd frontend
npm install
```

## Local run

1. **Start the backend** (from `backend/` with venv active):

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   # or: python run.py
   ```

2. **Start the frontend** (from `frontend/`):

   ```bash
   npm run dev
   ```

3. Open **http://localhost:3000**. Upload an image, click **Analyze**, and view the verdict, confidence bars, and description.

The frontend proxies `/api` and `/health` to `http://localhost:8000` when using Vite dev server.

## Deployment

### Backend (Docker)

Build and run the API in a container:

```bash
cd backend
docker build -t sentinelvision-api .
docker run -p 8000:8000 --env-file .env sentinelvision-api
```

For production, use a process manager or orchestration (e.g. Kubernetes) and set `DEVICE=cuda` if GPU is available.

### Frontend (static build)

Build and serve the React app (e.g. Nginx, S3 + CloudFront):

```bash
cd frontend
npm run build
# Serve the contents of dist/; set API base URL via env if backend is on another host
```

If the backend is on a different origin, configure your frontend API base (e.g. `VITE_API_BASE=https://api.example.com`) and use it in `src/api/client.js` for `API_BASE`.

## Configuration

Backend behavior is controlled by environment variables (see `backend/.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `THRESHOLD_BLOCK` | Score ≥ this → BLOCK | 0.85 |
| `THRESHOLD_REVIEW` | Score ≥ this and &lt; block → REVIEW | 0.45 |
| `CATEGORY_BLOCK_OVERRIDES` | Per-category block threshold, e.g. `sexual_content:0.7,violence:0.8` | (none) |
| `CLIP_MODEL_ID` | Hugging Face model for moderation | openai/clip-vit-base-patch32 |
| `CAPTION_MODEL_ID` | Hugging Face model for captioning | Salesforce/blip-image-captioning-base |
| `DEVICE` | `cpu` or `cuda` | cpu |
| `MAX_UPLOAD_MB` | Max upload size (MB) | 10 |

## API

- **POST /api/analyze-image**  
  - **Body**: multipart form with `file` (image; JPEG/PNG/WebP) and optional `image_id`.  
  - **Response**: JSON with `verdict`, `verdict_reason`, `categories` (list of `{ category, score, label }`), and `description`.  
  - See `docs/example-response.json` for a full example.

- **GET /health**  
  - Returns `{ "status": "ok", "service": "SentinelVision" }`.

## Example API response

See **`docs/example-response.json`** for a full sample. Summary:

```json
{
  "verdict": "SAFE",
  "verdict_reason": "No categories exceeded review threshold.",
  "categories": [
    { "category": "nsfw", "score": 0.12, "label": "NSFW" },
    { "category": "violence", "score": 0.08, "label": "Violence" },
    ...
  ],
  "description": "a dog sitting on a couch in a living room",
  "image_id": null
}
```

## ML stack

- **Moderation**: CLIP (zero-shot) with text prompts per category; scores normalized to [0, 1] via sigmoid.
- **Captioning**: BLIP for a short image description (explainability and auditability only).

Models are loaded on first request and reused. No custom training required; suitable for resume-ready and interview discussions.

## Output
<img width="1128" height="1148" alt="Screenshot 2026-02-01 005528" src="https://github.com/user-attachments/assets/020723c0-ffc6-4c80-80e3-406544ad181b" />
<img width="1159" height="1170" alt="Screenshot 2026-02-01 005845" src="https://github.com/user-attachments/assets/94bd5e5e-73e1-4fdb-b38f-4753ecdd2ed9" />
<img width="1150" height="1080" alt="Screenshot 2026-02-01 005511" src="https://github.com/user-attachments/assets/bc6244c3-9b74-42c7-9f43-c49433b6dfe4" />


## License

MIT.
