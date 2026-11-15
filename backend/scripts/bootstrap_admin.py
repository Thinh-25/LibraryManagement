"""Run from backend: python -m scripts.bootstrap_admin --email admin@library.example"""
import argparse
from getpass import getpass
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.session import get_engine
from app.core.security import hash_password
from app.models import User


def main():
    parser=argparse.ArgumentParser(description='Set a local administrator password securely.')
    parser.add_argument('--email',required=True)
    args=parser.parse_args()
    password=getpass('Mật khẩu mới (ít nhất 12 ký tự): ')
    confirmation=getpass('Nhập lại mật khẩu: ')
    if len(password)<12 or len(password)>256 or password!=confirmation:
        parser.error('Mật khẩu không hợp lệ hoặc không khớp.')
    with Session(get_engine()) as db:
        user=db.scalar(select(User).where(func.lower(User.email)==args.email.strip().lower()).with_for_update())
        if not user or user.vai_tro!='ADMIN':
            parser.error('Không tìm thấy tài khoản ADMIN có email này.')
        user.mat_khau_hash=hash_password(password)
        user.auth_version+=1
        user.must_change_password=False
        user.trang_thai=True
        db.commit()
    print('Đã cập nhật mật khẩu quản trị viên.')

if __name__=='__main__':
    main()
