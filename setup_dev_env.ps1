# Home Assistant 커스텀 통합구성요소 개발 환경 설정 스크립트

Write-Host "Home Assistant 커스텀 통합구성요소 개발 환경을 설정합니다..." -ForegroundColor Green

# Python 가상환경 생성
Write-Host "Python 가상환경을 생성합니다..." -ForegroundColor Yellow
python -m venv venv

# 가상환경 활성화
Write-Host "가상환경을 활성화합니다..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 필요한 패키지 설치
Write-Host "필요한 패키지들을 설치합니다..." -ForegroundColor Yellow
pip install -r requirements.txt

# 추가 개발 도구 설치
Write-Host "개발 도구들을 설치합니다..." -ForegroundColor Yellow
pip install homeassistant
pip install pytest
pip install black
pip install flake8
pip install pytest-asyncio
pip install pytest-cov

Write-Host "개발 환경 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host "가상환경을 활성화하려면: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "테스트를 실행하려면: pytest tests/" -ForegroundColor Cyan 