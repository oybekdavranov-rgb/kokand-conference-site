# Kokand University – Digital Technologies Conference (Flask)

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open:
- http://127.0.0.1:5000

## Edit without touching code
Open:
- http://127.0.0.1:5000/edit

### Optional protection (recommended for hosting)
Set an environment variable `EDIT_TOKEN` and open:
- http://127.0.0.1:5000/edit?token=YOUR_TOKEN

API:
- GET  /api/data
- POST /api/data  (send header `X-Edit-Token: YOUR_TOKEN` or ?token=YOUR_TOKEN)
