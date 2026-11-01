from __future__ import annotations

import os
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .database import create_database_engine, create_session_factory
from .errors import ApiError
from .mock_provider import create_generation
from .routers.projects import router as projects_router
from .schemas import GenerateRequest, GenerationResponse


logger = logging.getLogger("webverse.api")


def create_app(database_url: str | None = None) -> FastAPI:
    application = FastAPI(
        title="WebVerse AI API",
        version="0.2.0",
        description="Mock-first API for structured website generation and immutable projects.",
    )
    engine = create_database_engine(database_url)
    application.state.engine = engine
    application.state.session_factory = create_session_factory(engine)

    origins = [
        item.strip()
        for item in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if item.strip()
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-Workspace-ID"],
    )

    @application.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        body: dict = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details is not None:
            body["error"]["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=body)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "request_validation_failed",
                    "message": "The request payload is invalid.",
                    "details": exc.errors(),
                }
            },
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("Database operation failed", exc_info=exc)
        return JSONResponse(
            status_code=503,
            content={"error": {"code": "database_unavailable", "message": "The database operation failed."}},
        )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "webverse-api", "provider": "mock"}

    @application.post(
        "/api/generations",
        response_model=GenerationResponse,
        response_model_exclude_none=True,
    )
    def generate(request: GenerateRequest) -> GenerationResponse:
        result = create_generation(request.prompt, request.category, request.enable_3d)
        return GenerationResponse(**result)

    application.include_router(projects_router)
    return application


app = create_app()
