"""Run from backend: python -m scripts.seed_demo_accounts [--reset-passwords]

Creates one demo account per role. Passwords are random, printed once and never stored in plaintext.
Existing accounts are left untouched unless --reset-passwords is given.
"""
import argparse
import secrets
from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.session import get_engine
from app.core.security import hash_password
from app.models import User, LibraryCard

DEMO_ACCOUNTS = [
    dict(ho_ten='Quản trị viên mẫu', email='admin.demo@library.example', vai_tro='ADMIN'),
    dict(ho_ten='Thủ thư mẫu', email='thuthu.demo@library.example', vai_tro='THU_THU'),
    dict(ho_ten='Độc giả mẫu', email='docgia.demo@library.example', vai_tro='DOC_GIA'),
]


def main():
    parser = argparse.ArgumentParser(description='Tạo tài khoản mẫu cho từng vai trò.')
    parser.add_argument('--reset-passwords', action='store_true', help='Đặt lại mật khẩu cho tài khoản mẫu đã tồn tại.')
    args = parser.parse_args()
    results = []
    with Session(get_engine()) as db:
        for item in DEMO_ACCOUNTS:
            user = db.scalar(select(User).where(func.lower(User.email) == item['email']).with_for_update())
            if user is not None and not args.reset_passwords:
                results.append((item['vai_tro'], item['email'], None))
                continue
            password = secrets.token_urlsafe(12)
            if user is None:
                user = User(**item, mat_khau_hash=hash_password(password), trang_thai=True, must_change_password=False)
                db.add(user)
                db.flush()
            else:
                user.mat_khau_hash = hash_password(password)
                user.vai_tro = item['vai_tro']
                user.trang_thai = True
                user.must_change_password = False
                user.auth_version += 1
            if item['vai_tro'] == 'DOC_GIA' and not db.scalar(select(LibraryCard).where(LibraryCard.nguoi_dung_id == user.id)):
                db.add(LibraryCard(nguoi_dung_id=user.id, ma_the=f'DEMO{user.id:06d}', ngay_het_han=date.today() + timedelta(days=365)))
            results.append((item['vai_tro'], item['email'], password))
        db.commit()
    for role, email, password in results:
        print(f'{role:8} {email:30} {password or "(đã tồn tại, giữ nguyên mật khẩu)"}')


if __name__ == '__main__':
    main()

