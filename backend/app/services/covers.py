from io import BytesIO
from pathlib import Path
import re
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import get_settings
from app.core.errors import BusinessError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
FILENAME = re.compile(r"[0-9a-f]{32}\.webp")


def cover_directory() -> Path:
    return get_settings().cover_upload_dir.resolve()


def save_cover(data: bytes) -> str:
    if len(data) > MAX_UPLOAD_BYTES:
        raise BusinessError(413, "Ảnh không được vượt quá 5 MB.")
    try:
        with Image.open(BytesIO(data)) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise BusinessError(422, "Chỉ nhận ảnh JPG, PNG hoặc WebP.")
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise BusinessError(422, "Ảnh vượt quá giới hạn 20 triệu điểm ảnh.")
            if getattr(source, "is_animated", False):
                raise BusinessError(422, "Vui lòng chọn ảnh tĩnh.")
            source.verify()
        with Image.open(BytesIO(data)) as source:
            source.load()
            oriented = ImageOps.exif_transpose(source)
            image = oriented.convert("RGBA" if "A" in oriented.getbands() or "transparency" in oriented.info else "RGB")
            image.thumbnail((2400, 2400))
            image.info.clear()
            output = BytesIO()
            image.save(output, format="WEBP", quality=85, exif=b"", icc_profile=b"", xmp=b"")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise BusinessError(422, "File không phải ảnh hợp lệ hoặc ảnh đã bị hỏng.")

    directory = cover_directory()
    directory.mkdir(parents=True, exist_ok=True)
    filename = uuid4().hex + ".webp"
    target = directory / filename
    try:
        with target.open("xb") as destination:
            destination.write(output.getvalue())
    except OSError:
        target.unlink(missing_ok=True)
        raise BusinessError(503, "Không thể lưu ảnh lúc này. Vui lòng thử lại.")
    return "/media/covers/" + filename


def find_cover(filename: str) -> Path:
    if FILENAME.fullmatch(filename) is None:
        raise BusinessError(404, "Không tìm thấy ảnh.")
    directory = cover_directory()
    target = (directory / filename).resolve()
    if target.parent != directory or not target.is_file():
        raise BusinessError(404, "Không tìm thấy ảnh.")
    return target
