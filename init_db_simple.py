#!/usr/bin/env python3
"""
간단한 데이터베이스 초기화 스크립트
"""

import sqlite3
import os

def init_database():
    """데이터베이스와 기본 테이블 생성"""

    # 데이터베이스 경로
    db_path = 'data/busan.db'

    # data 디렉토리가 없으면 생성
    os.makedirs('data', exist_ok=True)

    print("데이터베이스 초기화 시작...")

    # SQLite 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # PartnerGroup 테이블 생성
        cursor.execute('''
            CREATE TABLE partner_group (
                id INTEGER NOT NULL,
                name VARCHAR(255),
                business_number VARCHAR(64),
                corporation_number VARCHAR(64),
                representative VARCHAR(128),
                phone VARCHAR(64),
                mobile VARCHAR(64),
                address VARCHAR(255),
                bank_name VARCHAR(64),
                account_number VARCHAR(64),
                logo_path VARCHAR(512),
                created_at DATETIME,
                PRIMARY KEY (id)
            )
        ''')

        # Member 테이블 생성
        cursor.execute('''
            CREATE TABLE member (
                id INTEGER NOT NULL,
                partner_group_id INTEGER,
                username VARCHAR(120) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                position VARCHAR(128) NOT NULL,
                full_name VARCHAR(128) NOT NULL,
                license_number VARCHAR(64) NOT NULL,
                address VARCHAR(255),
                business_number VARCHAR(64) NOT NULL,
                car_dealership_number VARCHAR(64) NOT NULL,
                corporation_number VARCHAR(64),
                representative VARCHAR(128) NOT NULL,
                phone VARCHAR(64),
                mobile VARCHAR(64),
                email VARCHAR(255),
                registration_cert_path VARCHAR(512),
                license_attachment_path VARCHAR(512),
                member_type VARCHAR(32) NOT NULL,
                privacy_agreement BOOLEAN DEFAULT 0,
                approval_status VARCHAR(32) DEFAULT '신청',
                role VARCHAR(32) DEFAULT 'member',
                memo VARCHAR(255),
                point_balance INTEGER DEFAULT 0,
                settlement_method VARCHAR(16) DEFAULT '포인트',
                claim_amount INTEGER DEFAULT 0,
                created_at DATETIME,
                PRIMARY KEY (id),
                CONSTRAINT ck_member_approval_status CHECK (approval_status IN ('신청','승인')),
                CONSTRAINT ck_member_role CHECK (role IN ('member','admin','partner_admin')),
                CONSTRAINT ck_member_type CHECK (member_type IN ('법인사업자','개인사업자')),
                CONSTRAINT ck_member_settlement_method CHECK (settlement_method IN ('포인트','후불정산')),
                CONSTRAINT uq_member_username_partner UNIQUE (username, partner_group_id),
                FOREIGN KEY(partner_group_id) REFERENCES partner_group (id)
            )
        ''')

        # 기본 파트너 그룹 생성 (부산광역시자동차매매사업조합)
        cursor.execute('''
            INSERT INTO partner_group (id, name, business_number, representative, phone, mobile, address, created_at)
            VALUES (1, '부산광역시자동차매매사업조합', '123-45-67890', '홍길동', '051-123-4567', '010-1234-5678', '부산시 중구', datetime('now'))
        ''')

        # 기본 관리자 계정 생성
        import hashlib
        from werkzeug.security import generate_password_hash

        admin_password_hash = generate_password_hash('#admin1004', method='pbkdf2:sha256')
        wecar_password_hash = generate_password_hash('#wecarm1004', method='pbkdf2:sha256')

        cursor.execute('''
            INSERT INTO member (
                id, username, password_hash, company_name, position, full_name, license_number,
                business_number, car_dealership_number, representative, phone, mobile, email,
                member_type, privacy_agreement, approval_status, role, created_at
            ) VALUES (
                1, 'hyundai', ?, '현대해상', '관리자', '관리자', '1234567890',
                '123-45-67890', '9876543210', '김관리', '02-123-4567', '010-9876-5432', 'admin@hyundai.com',
                '법인사업자', 1, '승인', 'admin', datetime('now')
            )
        ''', (admin_password_hash,))

        cursor.execute('''
            INSERT INTO member (
                id, username, password_hash, company_name, position, full_name, license_number,
                business_number, car_dealership_number, representative, phone, mobile, email,
                member_type, privacy_agreement, approval_status, role, partner_group_id, created_at
            ) VALUES (
                2, 'wecar1004', ?, '위탁운영파트너', '관리자', '파트너관리자', '1111111111',
                '111-11-11111', '2222222222', '박파트너', '02-111-1111', '010-1111-1111', 'partner@wecar.com',
                '법인사업자', 1, '승인', 'partner_admin', 1, datetime('now')
            )
        ''', (wecar_password_hash,))

        # 인덱스 생성
        cursor.execute("CREATE INDEX idx_member_business_number ON member (business_number)")
        cursor.execute("CREATE INDEX idx_member_created_at ON member (created_at)")
        cursor.execute("CREATE INDEX idx_member_partner_group ON member (partner_group_id)")
        cursor.execute("CREATE INDEX idx_member_username_partner ON member (username, partner_group_id)")

        # 커밋
        conn.commit()

        print("✅ 데이터베이스 초기화 완료!")
        print("📊 생성된 데이터:")
        print("   - 파트너그룹: 부산광역시자동차매매사업조합")
        print("   - 관리자 계정: hyundai / #admin1004")
        print("   - 파트너관리자: wecar1004 / #wecarm1004")

        return True

    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 데이터베이스가 성공적으로 초기화되었습니다!")
        print("이제 애플리케이션을 시작할 수 있습니다.")
    else:
        print("\n❌ 데이터베이스 초기화에 실패했습니다.")


