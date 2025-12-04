#!/usr/bin/env python3
"""
간단한 회원 필드 마이그레이션 스크립트
ALTER TABLE을 사용하여 단계별로 마이그레이션 진행
"""

import sqlite3
import os

def simple_migrate():
    db_path = 'data/busan.db'

    if not os.path.exists(db_path):
        print("데이터베이스 파일을 찾을 수 없습니다.")
        return False

    try:
        # 백업 생성
        backup_path = f"{db_path}.simple_backup"
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print(f"백업 생성: {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 트랜잭션 시작
        cursor.execute("BEGIN TRANSACTION")

        try:
            # 1. 기존 제약조건이 없는 임시 테이블 생성
            print("제약조건 없는 임시 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE member_temp (
                    id INTEGER NOT NULL,
                    partner_group_id INTEGER,
                    username VARCHAR(120),
                    password_hash VARCHAR(255),
                    company_name VARCHAR(255),
                    address VARCHAR(255),
                    business_number VARCHAR(64),
                    corporation_number VARCHAR(64),
                    representative VARCHAR(128),
                    phone VARCHAR(64),
                    mobile VARCHAR(64),
                    email VARCHAR(255),
                    registration_cert_path VARCHAR(512),
                    member_type VARCHAR(32),
                    position VARCHAR(128),
                    full_name VARCHAR(128),
                    license_number VARCHAR(64),
                    license_attachment_path VARCHAR(512),
                    privacy_agreement BOOLEAN,
                    approval_status VARCHAR(32),
                    role VARCHAR(32),
                    memo VARCHAR(255),
                    point_balance INTEGER,
                    settlement_method VARCHAR(16),
                    claim_amount INTEGER,
                    created_at DATETIME,
                    PRIMARY KEY (id),
                    FOREIGN KEY(partner_group_id) REFERENCES partner_group (id)
                )
            """)

            # 2. 데이터 복사 및 변환
            print("데이터 복사 및 변환 중...")
            cursor.execute("""
                INSERT INTO member_temp (
                    id, partner_group_id, username, password_hash, company_name, address,
                    business_number, corporation_number, representative, phone, mobile, email,
                    registration_cert_path, member_type, privacy_agreement, approval_status,
                    role, memo, point_balance, settlement_method, claim_amount, created_at,
                    position, full_name, license_number, license_attachment_path
                )
                SELECT
                    id, partner_group_id, username, password_hash, company_name, address,
                    business_number, corporation_number, representative, phone, mobile, email,
                    registration_cert_path,
                    CASE
                        WHEN member_type = '법인' THEN '법인사업자'
                        WHEN member_type = '개인' THEN '개인사업자'
                        ELSE member_type
                    END as member_type,
                    privacy_agreement, approval_status, role, memo, point_balance,
                    settlement_method, claim_amount, created_at,
                    '' as position, '' as full_name, '' as license_number, '' as license_attachment_path
                FROM member
            """)

            # 3. 기존 테이블 삭제 및 새 테이블로 교체
            print("테이블 교체 중...")
            cursor.execute("DROP TABLE member")
            cursor.execute("ALTER TABLE member_temp RENAME TO member")

            # 4. 새로운 제약조건이 있는 최종 테이블 생성
            print("최종 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE member_final (
                    id INTEGER NOT NULL,
                    partner_group_id INTEGER,
                    username VARCHAR(120) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    address VARCHAR(255),
                    business_number VARCHAR(64) NOT NULL,
                    corporation_number VARCHAR(64),
                    representative VARCHAR(128) NOT NULL,
                    phone VARCHAR(64),
                    mobile VARCHAR(64),
                    email VARCHAR(255),
                    registration_cert_path VARCHAR(512),
                    member_type VARCHAR(32) NOT NULL DEFAULT '법인사업자',
                    position VARCHAR(128) NOT NULL DEFAULT '',
                    full_name VARCHAR(128) NOT NULL DEFAULT '',
                    license_number VARCHAR(64) NOT NULL DEFAULT '',
                    license_attachment_path VARCHAR(512),
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
            """)

            # 5. 최종 데이터 복사
            print("최종 데이터 복사 중...")
            cursor.execute("""
                INSERT INTO member_final SELECT * FROM member
            """)

            # 6. 최종 테이블 교체
            cursor.execute("DROP TABLE member")
            cursor.execute("ALTER TABLE member_final RENAME TO member")

            # 인덱스 재생성
            cursor.execute("CREATE INDEX idx_member_business_number ON member (business_number)")
            cursor.execute("CREATE INDEX idx_member_created_at ON member (created_at)")
            cursor.execute("CREATE INDEX idx_member_partner_group ON member (partner_group_id)")
            cursor.execute("CREATE INDEX idx_member_username_partner ON member (username, partner_group_id)")

            # 트랜잭션 커밋
            conn.commit()

            # 결과 확인
            cursor.execute("SELECT COUNT(*) FROM member")
            total_members = cursor.fetchone()[0]
            print(f"총 회원 수: {total_members}")

            cursor.execute("SELECT member_type, COUNT(*) FROM member GROUP BY member_type")
            member_types = cursor.fetchall()
            print("회원유형별 분포:")
            for member_type, count in member_types:
                print(f"  {member_type}: {count}")

            cursor.execute("PRAGMA table_info(member)")
            columns = cursor.fetchall()
            print("\n새로운 테이블 구조:")
            for col in columns:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                print(f"  {col[1]} {col[2]} {nullable}")

            print("마이그레이션 완료!")

        except Exception as e:
            print(f"마이그레이션 중 오류 발생: {e}")
            conn.rollback()
            raise e

        finally:
            conn.close()

        return True

    except Exception as e:
        print(f"마이그레이션 실패: {e}")
        return False

if __name__ == "__main__":
    success = simple_migrate()
    if success:
        print("✅ 회원 필드 마이그레이션이 성공적으로 완료되었습니다.")
    else:
        print("❌ 회원 필드 마이그레이션에 실패했습니다.")
