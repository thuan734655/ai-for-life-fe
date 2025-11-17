from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.routers import jobs, match


tags_metadata = [
    {"name": "jobs", "description": "Quản lý và truy vấn Job"},
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.include_router(jobs.router)
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
