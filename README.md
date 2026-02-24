# ReAct RAG Web App (FastAPI + Vanilla JS)

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open: http://localhost:8000

Set API key in browser console:
```js
localStorage.setItem('apiKey','dev-key')
```

## API
Base path: `/api/v1`
- `GET /healthz`
- `GET /readyz`
- Collections CRUD
- Document upload/list/delete
- `POST /react/query`
- `GET /react/stream` (SSE)
