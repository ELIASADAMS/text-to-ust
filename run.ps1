# run.ps1 — простая обвязка для быстрого старта
param(
    [string]$Script = "hiro_ust_dev.py"
)

if (-not (Test-Path ".venv")) {
    Write-Host "Создаю виртуальное окружение .venv..."
    python -m venv .venv
}

Write-Host "Активируйте окружение: & .\.venv\Scripts\Activate.ps1"
Write-Host "Установите зависимости: pip install -r requirements.txt"
Write-Host "Запуск скрипта: python $Script"
# Для автоматического активации и запуска (может потребовать разрешения выполнения):
# & .\.venv\Scripts\Activate.ps1; python $Script

