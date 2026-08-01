import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.seed import seed_db
from app.api.router import router as api_router
from app.config import STORED_FILES_DIR

app = FastAPI(
    title="PCCC Document Management",
    description="Multi-tenant Regulatory Document Management System"
)

# Initialize database schemas and seed default entries on launch
@app.on_event("startup")
def startup_event():
    seed_db()

# Mount local upload folder to allow viewing/downloading PDFs directly
os.makedirs(STORED_FILES_DIR, exist_ok=True)
app.mount("/stored_files", StaticFiles(directory=STORED_FILES_DIR), name="stored_files")

# Mount static assets (CSS, JS, Vite-built bundles)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Register use-case API routers
app.include_router(api_router)

# Serve the Vite-built frontend (after `npm run build` inside /frontend)
# The build output lands at static/dist/index.html
BUILT_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "dist", "index.html")
# Fallback to the legacy template when the built file doesn't exist yet
LEGACY_TEMPLATE = os.path.join("templates", "index.html")

@app.get("/")
def serve_home():
    if os.path.exists(BUILT_TEMPLATE):
        return FileResponse(BUILT_TEMPLATE)
    if os.path.exists(LEGACY_TEMPLATE):
        return FileResponse(LEGACY_TEMPLATE)
    return {"error": "Frontend not built. Run `npm run build` inside /frontend."}