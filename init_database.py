#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
기존 데이터베이스를 백업하고 새로 생성합니다.
"""

import os
import shutil
from datetime import datetime
from app import app, db, init_db_and_assets, ensure_initialized

def init_database():
    """데이터베이스를 초기화합니다."""
    db_path = os.path.join('data', 'busan.db')
    
    # 백업 디렉토리 생성
    backup_dir = os.path.join('data', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # 기존 데이터베이스 백업
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'busan_backup_{timestamp}.db')
        shutil.copy2(db_path, backup_path)
        print(f"✅ 기존 데이터베이스 백업 생성: {backup_path}")
        
        # 기존 데이터베이스 삭제
        os.remove(db_path)
        print(f"✅ 기존 데이터베이스 삭제: {db_path}")
    else:
        print("ℹ️  기존 데이터베이스 파일이 없습니다. 새로 생성합니다.")
    
    # 데이터 디렉토리 확인
    data_dir = os.path.dirname(db_path)
    os.makedirs(data_dir, exist_ok=True)
    
    # Flask 앱 컨텍스트 내에서 초기화
    with app.app_context():
        print("🔄 데이터베이스 초기화 중...")
        
        # 데이터베이스 초기화
        ensure_initialized()
        init_db_and_assets()
        
        print("✅ 데이터베이스 초기화 완료!")
        print(f"   데이터베이스 경로: {os.path.abspath(db_path)}")
        
        # 테이블 목록 확인
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   생성된 테이블: {', '.join(tables)}")
        except Exception as e:
            print(f"   ⚠️  테이블 목록 확인 실패: {e}")

if __name__ == '__main__':
    init_database()

