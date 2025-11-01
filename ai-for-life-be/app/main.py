from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers import jobs, users, match


def init_db():
    Base.metadata.create_all(bind=engine)


tags_metadata = [
    {"name": "jobs", "description": "Quản lý và truy vấn Job"},
    {"name": "users", "description": "Quản lý ứng viên"},
    {"name": "match", "description": "Tính điểm phù hợp job"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description="API gợi ý việc làm dựa trên kỹ năng, vị trí mong muốn và kinh nghiệm.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

init_db()

app.include_router(jobs.router)
app.include_router(users.router)
app.include_router(match.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Custom hóa OpenAPI (tuỳ chọn)
_cached_openapi_schema = None


def custom_openapi():
    global _cached_openapi_schema
    if _cached_openapi_schema:
        return _cached_openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["info"]["contact"] = {
        "name": "AI for Life",
        "url": "https://example.com",
    }
    _cached_openapi_schema = openapi_schema
    return _cached_openapi_schema


app.openapi = custom_openapi
