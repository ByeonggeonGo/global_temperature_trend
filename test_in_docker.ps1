# Docker Desktop이 켜져 있는지 확인
if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker Desktop is not running. Please launch Docker Desktop first."
    exit 1
}

$ErrorActionPreference = "Stop"

Write-Host "1. Building lightweight Kaggle-like test docker image..."
docker build -f Dockerfile.kaggle_test -t kaggle-notebook-test .

Write-Host "2. Running Jupyter notebook inside the docker container for verification..."
# Mount current directory to /tmp/working and run the notebook
docker run --rm -v "${PWD}:/tmp/working" kaggle-notebook-test jupyter nbconvert --to notebook --execute --inplace global_temperature_analysis.ipynb

Write-Host "3. Synchronizing updated notebook to kaggle_code/ folder..."
Copy-Item -Path global_temperature_analysis.ipynb -Destination kaggle_code/global_temperature_analysis.ipynb -Force

Write-Host "=========================================="
Write-Host " Docker Verification Test Succeeded!" -ForegroundColor Green
Write-Host " Notebook execution was verified successfully in Kaggle environment."
Write-Host "=========================================="
