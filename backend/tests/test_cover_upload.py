from io import BytesIO
from pathlib import Path
import struct
import zlib

import pytest


def png_bytes(width=2, height=2):
    # Small real PNG without requiring the image dependency just to collect tests.
    def chunk(kind, data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    raw = (b'\x00'+b'\xff\x00\x00'*width)*height
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')


@pytest.fixture
def upload_dir(monkeypatch, tmp_path):
    from app.core.config import get_settings
    monkeypatch.setenv('COVER_UPLOAD_DIR',str(tmp_path/'covers'))
    get_settings.cache_clear()
    return tmp_path/'covers'


@pytest.mark.parametrize('role',['ADMIN','THU_THU'])
def test_staff_upload_is_reencoded_and_publicly_readable(client, auth_headers, upload_dir, role):
    response = client.post('/api/v1/uploads/covers',headers=auth_headers(role), files={'file':('../../name.png',png_bytes(),'image/png')})
    assert response.status_code == 201, response.text
    url = response.json()['url']
    assert url.startswith('/media/covers/') and url.endswith('.webp') and '..' not in url
    saved = list(upload_dir.iterdir())
    assert len(saved)==1 and saved[0].name == url.rsplit('/',1)[1]
    media = client.get(url)
    assert media.status_code == 200 and media.headers['content-type']=='image/webp'
    assert media.content.startswith(b'RIFF') and media.content[8:12] == b'WEBP'


def test_reader_and_anonymous_cannot_upload(client, auth_headers, upload_dir):
    files={'file':('cover.png',png_bytes(),'image/png')}
    assert client.post('/api/v1/uploads/covers',files=files).status_code==401
    assert client.post('/api/v1/uploads/covers',headers=auth_headers('DOC_GIA'),files=files).status_code==403
    assert not upload_dir.exists()


@pytest.mark.parametrize('payload,mime',[(b'<svg><script>alert(1)</script></svg>','image/svg+xml'),(b'not a real picture','image/png'),(png_bytes()[:35],'image/png')])
def test_fake_or_corrupt_images_rejected_without_files(client, auth_headers, upload_dir, payload, mime):
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('cover.png',payload,mime)})
    assert response.status_code==422
    assert not upload_dir.exists() or not list(upload_dir.iterdir())


def test_oversized_upload_rejected(client, auth_headers, upload_dir):
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('cover.png',b'x'*(5*1024*1024+1),'image/png')})
    assert response.status_code==413
    assert not upload_dir.exists() or not list(upload_dir.iterdir())


def test_media_rejects_missing_and_non_generated_filename(client, upload_dir):
    assert client.get('/media/covers/secret.txt').status_code==404
    assert client.get('/media/covers/'+'a'*32+'.webp').status_code==404


@pytest.mark.parametrize('format,mime',[('JPEG','image/jpeg'),('WEBP','image/webp')])
def test_jpeg_and_webp_supported(client, auth_headers, upload_dir, format, mime):
    from PIL import Image
    stream=BytesIO()
    Image.new('RGB',(4,4),'blue').save(stream,format=format)
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('cover',stream.getvalue(),mime)})
    assert response.status_code==201


def test_pixel_limit_is_checked_before_decoding_large_image(client, auth_headers, upload_dir):
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    payload=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',5000,4001,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''))+chunk(b'IEND',b'')
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('huge.png',payload,'image/png')})
    assert response.status_code==422
    assert not upload_dir.exists()


def test_jpeg_metadata_removed_and_output_dimensions_bounded(client, auth_headers, upload_dir):
    from PIL import Image
    stream=BytesIO()
    photo=Image.new('RGB',(2600,20),'blue')
    exif=photo.getexif(); exif[0x010e]='private photo metadata'
    photo.save(stream,format='JPEG',exif=exif)
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('camera.jpg',stream.getvalue(),'image/jpeg')})
    assert response.status_code==201
    with Image.open(BytesIO(client.get(response.json()['url']).content)) as image:
        assert max(image.size)<=2400
        assert not image.getexif()


def test_local_cover_path_can_be_saved_updated_removed_and_rejects_unsafe_paths(client, auth_headers, upload_dir):
    from app.schemas.catalog import BookCreate
    from pydantic import ValidationError
    body=dict(ten_sach='Sách có bìa',the_loai_id=1,nha_xuat_ban_id=1)
    with pytest.raises(ValidationError):
        BookCreate(**body,anh_bia='/media/covers/../../.env')
    response=client.post('/api/v1/uploads/covers',headers=auth_headers(),files={'file':('cover.png',png_bytes(),'image/png')})
    assert response.status_code==201
    url=response.json()['url']
    created=client.post('/api/v1/books',headers=auth_headers(),json={**body,'anh_bia':url})
    assert created.status_code==201, created.text
    assert created.json()['anh_bia']==url
    book_id=created.json()['id']
    removed=client.patch(f'/api/v1/books/{book_id}',headers=auth_headers(),json={'anh_bia':None})
    assert removed.status_code==200 and removed.json()['anh_bia'] is None
