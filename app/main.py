from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, clean up on shutdown."""
    init_db()
    yield


from app.api import auth, import_data, budgets, analytics, frontend, chat

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered personal finance advisor",
    lifespan=lifespan,
)

# Include API routers
app.include_router(auth.router)
app.include_router(import_data.router)
app.include_router(budgets.router)
app.include_router(analytics.router)
app.include_router(chat.router)

# Include Frontend routers
app.include_router(frontend.router)

# Static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.app_name, "env": settings.app_env}
