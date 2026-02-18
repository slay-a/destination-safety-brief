from fastapi import FastAPI
from app.api.v1.router import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="BiblioHook Backend",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(v1_router, prefix="/v1")
    return app


app = create_app()
