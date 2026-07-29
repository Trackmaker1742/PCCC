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
app.mount("/stored_files", StaticFiles(directory=STORED_FILES_DIR), name="stored_files")

# Register use-case API routers
app.include_router(api_router)

# Route to serve the rich Web UI client
TEMPLATE_FILE = os.path.join("templates", "index.html")

@app.get("/")
def serve_home():
    if not os.path.exists(TEMPLATE_FILE):
        return {"error": "Frontend template index.html not found"}
    return FileResponse(TEMPLATE_FILE)
