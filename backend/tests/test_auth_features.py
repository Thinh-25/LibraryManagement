from app.db.base import Base
import app.models


def test_all_library_models_are_mapped():
    assert len(Base.metadata.tables) == 13
    assert 'auth_version' in Base.metadata.tables['nguoi_dung'].c

def test_password_hash_and_token_security():
    from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
    from app.models import User
    password = 'StrongPassword!123'
    hashed = hash_password(password)
    assert hashed.startswith('$argon2id$')
    assert verify_password(password, hashed)
    assert not verify_password('wrong', hashed)
    assert not verify_password(password, 'REPLACE_WITH_REAL_HASH')
    user = User(id=42, auth_version=3)
    claims = decode_access_token(create_access_token(user))
    assert claims['sub'] == '42'
    assert claims['ver'] == 3


def test_login_revocation_and_profile_scope(client,db,auth_headers):
    from app.models import User
    from app.services.accounts import rate_limiter
    rate_limiter.events.clear()
    headers=auth_headers('DOC_GIA')
    me=client.get('/api/v1/auth/me',headers=headers)
    assert me.status_code==200
    user=me.json()
    assert 'mat_khau_hash' not in user
    assert client.get('/api/v1/users',headers=headers).status_code==403
    assert client.patch('/api/v1/auth/me',headers=headers,json={'vai_tro':'ADMIN'}).status_code==422
    response=client.post('/api/v1/auth/login',json={'email':user['email'].upper(),'password':'ValidPassword123!'})
    assert response.status_code==200
    assert client.post('/api/v1/auth/logout',headers=headers).status_code==200
    assert client.get('/api/v1/auth/me',headers=headers).status_code==401


def test_admin_reset_forces_change_and_revokes_tokens(client,db,auth_headers):
    from app.services.accounts import rate_limiter
    rate_limiter.events.clear()
    admin=auth_headers()
    reader=auth_headers('DOC_GIA')
    user=client.get('/api/v1/auth/me',headers=reader).json()
    response=client.post(f"/api/v1/users/{user['id']}/reset-password",headers=admin,json={'new_password':'TemporaryStrong123!'})
    assert response.status_code==200
    assert client.get('/api/v1/auth/me',headers=reader).status_code==401
    login=client.post('/api/v1/auth/login',json={'email':user['email'],'password':'TemporaryStrong123!'})
    assert login.status_code==200
    forced={'Authorization':'Bearer '+login.json()['access_token']}
    assert login.json()['user']['must_change_password'] is True
    assert client.get('/api/v1/books',headers=forced).status_code==403
    assert client.patch('/api/v1/auth/me',headers=forced,json={'ho_ten':'Changed'}).status_code==403
    assert client.post('/api/v1/auth/change-password',headers=forced,json={'current_password':'TemporaryStrong123!','new_password':'FinalStrongPassword123!'}).status_code==200
    assert client.get('/api/v1/auth/me',headers=forced).status_code==401
    login=client.post('/api/v1/auth/login',json={'email':user['email'],'password':'FinalStrongPassword123!'})
    assert login.json()['user']['must_change_password'] is False


def test_reset_requests_private_and_deduplicated(client,db,auth_headers):
    from app.services.accounts import rate_limiter
    rate_limiter.events.clear()
    admin=auth_headers()
    reader=auth_headers('DOC_GIA')
    user=client.get('/api/v1/auth/me',headers=reader).json()
    known=client.post('/api/v1/auth/forgot-password',json={'email':user['email']})
    unknown=client.post('/api/v1/auth/forgot-password',json={'email':'not-exist@example.test'})
    assert known.status_code==unknown.status_code==200
    assert known.json()==unknown.json()
    client.post('/api/v1/auth/forgot-password',json={'email':user['email']})
    assert client.get('/api/v1/password-reset-requests',headers=reader).status_code==403
    listing=client.get('/api/v1/password-reset-requests',headers=admin)
    matching=[item for item in listing.json()['items'] if item['nguoi_dung_id']==user['id']]
    assert len(matching)==1
    request_id=matching[0]['id']
    assert client.post(f'/api/v1/password-reset-requests/{request_id}/resolve',headers=admin,json={}).status_code==422
    assert client.post(f'/api/v1/password-reset-requests/{request_id}/resolve',headers=admin,json={'reject':True}).status_code==200
    assert client.post(f'/api/v1/password-reset-requests/{request_id}/resolve',headers=admin,json={'reject':True}).status_code==409


def test_self_admin_protection_and_email_uniqueness(client,db,auth_headers):
    from app.models import User
    admin=auth_headers()
    me=client.get('/api/v1/auth/me',headers=admin).json()
    assert client.patch(f"/api/v1/users/{me['id']}",headers=admin,json={'trang_thai':False}).status_code==409
    assert client.patch(f"/api/v1/users/{me['id']}",headers=admin,json={'vai_tro':'DOC_GIA'}).status_code==409
    payload=dict(ho_ten='Reader',email='unique-user@example.test',vai_tro='DOC_GIA',password='ValidPassword123!')
    response=client.post('/api/v1/users',headers=admin,json=payload)
    assert response.status_code==201
    payload['email']=payload['email'].upper()
    assert client.post('/api/v1/users',headers=admin,json=payload).status_code==409


def test_login_rate_limit_and_disabled_seed(client,monkeypatch):
    from app.core.config import get_settings
    from app.services.accounts import rate_limiter
    monkeypatch.setenv('AUTH_RATE_LIMIT','2')
    get_settings.cache_clear()
    rate_limiter.events.clear()
    payload={'email':'admin@library.example','password':'not-real-password'}
    assert client.post('/api/v1/auth/login',json=payload).status_code==401
    assert client.post('/api/v1/auth/login',json=payload).status_code==401
    assert client.post('/api/v1/auth/login',json=payload).status_code==429
    rate_limiter.events.clear()


def test_expired_and_tampered_tokens_rejected(client,auth_headers):
    from datetime import datetime,timedelta,timezone
    import jwt
    from app.core.config import get_settings
    headers=auth_headers()
    token=headers['Authorization'].split()[1]
    assert client.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+token+'corrupt'}).status_code==401
    claims=jwt.decode(token,get_settings().jwt_secret.get_secret_value(),algorithms=['HS256'])
    claims['exp']=datetime.now(timezone.utc)-timedelta(seconds=5)
    expired=jwt.encode(claims,get_settings().jwt_secret.get_secret_value(),algorithm='HS256')
    assert client.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+expired}).status_code==401


def test_disabled_and_role_changed_tokens_revoked(client,auth_headers):
    admin=auth_headers()
    other=auth_headers('DOC_GIA')
    user=client.get('/api/v1/auth/me',headers=other).json()
    assert client.patch(f"/api/v1/users/{user['id']}",headers=admin,json={'vai_tro':'THU_THU'}).status_code==200
    assert client.get('/api/v1/auth/me',headers=other).status_code==401
    login=client.post('/api/v1/auth/login',json={'email':user['email'],'password':'ValidPassword123!'})
    active={'Authorization':'Bearer '+login.json()['access_token']}
    assert client.patch(f"/api/v1/users/{user['id']}",headers=admin,json={'trang_thai':False}).status_code==200
    assert client.get('/api/v1/auth/me',headers=active).status_code==401
    assert client.post('/api/v1/auth/login',json={'email':user['email'],'password':'ValidPassword123!'}).status_code==401


def test_password_preserves_whitespace():
    from app.schemas.auth import Login, PasswordChange
    assert Login(email='reader@example.test',password='  secret  ').password=='  secret  '
    assert PasswordChange(current_password='  secret  ',new_password='  longer-secret-password  ').new_password=='  longer-secret-password  '
