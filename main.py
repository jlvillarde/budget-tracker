import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse

from app.core.logger import logger
from app.core.exceptions_handler import (
    global_exception_handler,
    validation_exception_handler
)
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    from app.core.database import init_db
    await init_db()
    
    yield
    
    # Shutdown
    from app.core.database import close_db
    await close_db()
    logger.info("Shutting down application")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(request, exc)

@app.exception_handler(Exception)
async def handle_global_exception(request: Request, exc: Exception):
    return await global_exception_handler(request, exc)

# IMPORTANT: SessionMiddleware must be added AFTER the auth_middleware
# because middleware is executed in reverse order of registration
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY # Consider moving this to settings
)

# Include API routers
from app.api import all_routes
for route in all_routes:
    app.include_router(route, prefix='/api')


# Serve static assets (JS, CSS, images) from /static path
static_dir = os.path.join("app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    logger.info(f"Static files mounted from: {static_dir}")

# Catch-all route for React client-side routing
@app.get("/{full_path:path}")
def serve_react_app(request: Request, full_path: str):
    # Don't serve API routes through React
    if full_path.startswith("api/"):
        logger.warning(f"API route not found: {full_path}")
        return {"error": "API endpoint not found"}

    # Don't serve static files through this route
    if full_path.startswith("static/") or full_path.startswith("assets/"):
        logger.warning(f"Static file not found: {full_path}")
        return {"error": "Static file not found"}

    # Serve React index.html for all other routes (like /signin, /signup, etc.)
    index_path = os.path.join("app", "static", "index.html")
    if os.path.exists(index_path):
        logger.info(f"Serving React app for route: {full_path}")
        return FileResponse(index_path)

    logger.error("React build not found")
    return {"message": "React build not found. Please run: pipenv run build-react"}