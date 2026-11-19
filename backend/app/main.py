from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError

from app.api.v1.router import router
from app.core.config import get_settings
from app.core.errors import BusinessError
from app.api.v1.endpoints.uploads import media_router

app = FastAPI(title="Library Management System API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(router, prefix="/api/v1")
app.include_router(media_router)


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Dữ liệu bị trùng hoặc đang được tham chiếu."})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # FastAPI's default response includes raw inputs, which can contain passwords.
    fields = sorted({".".join(str(part) for part in error["loc"] if part != "body") for error in exc.errors()})
    return JSONResponse(status_code=422, content={"detail": "Dữ liệu không hợp lệ: " + ", ".join(fields)})
