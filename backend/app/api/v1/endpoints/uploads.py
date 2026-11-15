from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from app.dependencies.auth import require_roles
from app.services.covers import MAX_UPLOAD_BYTES, save_cover, find_cover

router = APIRouter(prefix="/uploads", tags=["Ảnh bìa"])
media_router = APIRouter(tags=["Ảnh bìa công khai"])


@router.post("/covers", status_code=201, dependencies=[Depends(require_roles("ADMIN", "THU_THU"))])
async def upload_cover(file: Annotated[UploadFile, File()]):
    try:
        data = await file.read(MAX_UPLOAD_BYTES + 1)
        url = await run_in_threadpool(save_cover, data)
        return {"url": url}
    finally:
        await file.close()


@media_router.get("/media/covers/{filename}")
def cover_file(filename: str):
    return FileResponse(find_cover(filename), media_type="image/webp", headers={
        "Cache-Control": "public, max-age=31536000, immutable",
        "X-Content-Type-Options": "nosniff",
    })
