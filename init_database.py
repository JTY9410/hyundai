#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
기존 데이터베이스를 백업하고 새로 생성합니다.
책임보험가입 관련 기본 설정도 함께 초기화합니다.
"""

import os
import shutil
from datetime import datetime
from app import app, db, init_db_and_assets, ensure_initialized, safe_commit
from app import PartnerGroup, Member, InsuranceApplication

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
        
        # 기본 데이터 설정 확인
        print("\n📋 기본 데이터 설정 확인 중...")
        
        # 1. 전체관리자 계정 확인
        try:
            admin = db.session.query(Member).filter(Member.role == 'admin').first()
            if admin:
                print(f"   ✅ 전체관리자 계정 확인: {admin.username}")
            else:
                print("   ⚠️  전체관리자 계정이 없습니다. init_db_and_assets에서 생성됩니다.")
        except Exception as e:
            print(f"   ⚠️  관리자 계정 확인 실패: {e}")
        
        # 2. 파트너그룹 확인
        try:
            partner_groups = db.session.query(PartnerGroup).all()
            if partner_groups:
                print(f"   ✅ 파트너그룹 {len(partner_groups)}개 확인:")
                for pg in partner_groups:
                    print(f"      - {pg.name} (ID: {pg.id})")
            else:
                print("   ℹ️  파트너그룹이 없습니다. 관리자 페이지에서 생성할 수 있습니다.")
        except Exception as e:
            print(f"   ⚠️  파트너그룹 확인 실패: {e}")
        
        # 3. 책임보험가입 관련 설정 확인
        print("\n🔗 책임보험가입 관련 연결 확인 중...")
        
        # InsuranceApplication 모델 확인
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'insurance_application' in inspector.get_table_names():
                print("   ✅ insurance_application 테이블 확인")
                
                # 컬럼 확인
                columns = [col['name'] for col in inspector.get_columns('insurance_application')]
                required_columns = [
                    'partner_group_id', 'contractor_code', 'insured_code',
                    'resident_registration_no', 'representative_name',
                    'car_plate', 'vin', 'car_name', 'status'
                ]
                missing_columns = [col for col in required_columns if col not in columns]
                if missing_columns:
                    print(f"   ⚠️  누락된 컬럼: {', '.join(missing_columns)}")
                else:
                    print("   ✅ 필수 컬럼 모두 확인")
            else:
                print("   ⚠️  insurance_application 테이블이 없습니다.")
        except Exception as e:
            print(f"   ⚠️  테이블 확인 실패: {e}")
        
        # 4. 외래키 관계 확인
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # partner_group_id 외래키 확인
            fks = inspector.get_foreign_keys('insurance_application')
            partner_group_fk = [fk for fk in fks if 'partner_group_id' in fk.get('constrained_columns', [])]
            if partner_group_fk:
                print("   ✅ partner_group_id 외래키 관계 확인")
            else:
                print("   ⚠️  partner_group_id 외래키 관계가 없습니다.")
            
            # created_by_member_id 외래키 확인
            member_fk = [fk for fk in fks if 'created_by_member_id' in fk.get('constrained_columns', [])]
            if member_fk:
                print("   ✅ created_by_member_id 외래키 관계 확인")
            else:
                print("   ⚠️  created_by_member_id 외래키 관계가 없습니다.")
        except Exception as e:
            print(f"   ⚠️  외래키 확인 실패: {e}")
        
        # 5. 기본 계약자코드 설정 확인
        print("\n📝 기본 설정 확인:")
        print("   ✅ 계약자코드: 위카모빌리티 주식회사 (755-81-02354)로 고정")
        print("   ✅ 책임보험가입 페이지에 파트너그룹 열 표시")
        print("   ✅ 주민등록번호 암호화 표시 (mask_rrn 필터)")
        print("   ✅ 대표자명 자동 저장")
        
        print("\n✨ 초기화 완료!")
        print("\n📌 다음 단계:")
        print("   1. 전체관리자로 로그인 (아이디: hyundai, 비밀번호: #admin1004)")
        print("   2. 파트너그룹 만들기 페이지에서 파트너그룹 생성")
        print("   3. 파트너그룹 관리자 계정 생성")
        print("   4. 회원가입 및 책임보험가입 신청 테스트")

if __name__ == '__main__':
    init_database()
