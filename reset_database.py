#!/usr/bin/env python3
"""
데이터베이스 완전 초기화 스크립트
기존 데이터를 모두 삭제하고 처음부터 시작합니다.
"""

import os
import sqlite3
from datetime import datetime

def reset_database():
    """데이터베이스를 완전히 초기화합니다."""
    db_path = 'data/busan.db'

    print("=== 데이터베이스 초기화 시작 ===")

    # 1. 기존 데이터베이스 백업
    if os.path.exists(db_path):
        backup_name = f"data/busan.db.full_backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with open(db_path, 'rb') as src, open(backup_name, 'wb') as dst:
                dst.write(src.read())
            print(f"✅ 기존 데이터베이스 백업 완료: {backup_name}")
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            return False

    # 2. 데이터베이스 파일 삭제
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ 기존 데이터베이스 파일 삭제 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 파일 삭제 실패: {e}")
        return False

    # 3. uploads 디렉토리 정리 (선택사항)
    uploads_dir = 'static/uploads'
    if os.path.exists(uploads_dir):
        try:
            for filename in os.listdir(uploads_dir):
                if filename not in ['.gitkeep']:  # .gitkeep은 유지
                    file_path = os.path.join(uploads_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            print("✅ 업로드 파일 정리 완료")
        except Exception as e:
            print(f"⚠️ 업로드 파일 정리 실패 (무시): {e}")

    print("✅ 데이터베이스 초기화 완료!")
    print("📝 다음 단계:")
    print("   1. 애플리케이션 재시작")
    print("   2. 첫 접속 시 자동으로 테이블 생성 및 초기 데이터 삽입")
    print("   3. 관리자 계정으로 로그인: hyundai / #admin1004")

    return True

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("\n🎉 데이터베이스가 성공적으로 초기화되었습니다!")
    else:
        print("\n❌ 데이터베이스 초기화에 실패했습니다.")


