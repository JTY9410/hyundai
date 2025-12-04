#!/bin/bash
# 현대해상 중고차 상품화 책임보험 시스템 재시작 스크립트

echo "=== 현대해상 중고차 상품화 책임보험 시스템 재시작 ==="

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ ! -f "app.py" ] || [ ! -f "docker-compose.yml" ]; then
    echo "❌ 오류: 프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Docker가 설치되어 있는지 확인
if ! command -v docker &> /dev/null; then
    echo "❌ 오류: Docker가 설치되어 있지 않습니다."
    echo "📝 Docker 설치 후 다시 시도해주세요."
    exit 1
fi

# Docker Compose가 설치되어 있는지 확인
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Docker Compose v1.x 사용"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose v2.x 사용"
else
    echo "❌ 오류: Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

echo "🔽 기존 컨테이너 중지 및 제거 중..."
$DOCKER_COMPOSE_CMD down

if [ $? -ne 0 ]; then
    echo "⚠️ 경고: 컨테이너 중지에 실패했지만 계속 진행합니다."
fi

echo "🔨 캐시 없이 새로 빌드 중..."
$DOCKER_COMPOSE_CMD build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ 오류: 빌드에 실패했습니다."
    exit 1
fi

echo "🚀 백그라운드에서 컨테이너 실행 중..."
$DOCKER_COMPOSE_CMD up -d

if [ $? -ne 0 ]; then
    echo "❌ 오류: 컨테이너 실행에 실패했습니다."
    echo "📝 로그 확인: $DOCKER_COMPOSE_CMD logs"
    exit 1
fi

echo ""
echo "✅ 재시작 완료!"
echo "📱 웹사이트: http://localhost:8901"
echo "👤 관리자 로그인: hyundai / #admin1004"
echo ""
echo "📋 로그 확인 명령어:"
echo "  $DOCKER_COMPOSE_CMD logs -f"
echo ""
echo "🛑 중지 명령어:"
echo "  $DOCKER_COMPOSE_CMD down"