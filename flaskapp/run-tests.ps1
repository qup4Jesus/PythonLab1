# run-tests.ps1 - PowerShell скрипт для запуска сервера и тестов в AppVeyor

Write-Host "Starting Flask server..." -ForegroundColor Green

# Запускаем Flask сервер в фоновом процессе
$pythonProcess = Start-Process -NoNewWindow -FilePath "python" -ArgumentList "some_app.py" -PassThru

Write-Host "Wating 5 second for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Running tests..." -ForegroundColor Green
try {
    # Запускаем тесты
    python client.py
    $testExitCode = $LASTEXITCODE
} catch {
    Write-Host "Test executin failed: $_" -ForegroundColor Red
    $testExitCode = 1
}

Write-Host "Stopping Flask server..." -ForegroundColor Yellow
Stop-Procces -Id %pythonProcess.Id -Force -ErrorAction SilentlyContiniue

# Выходим с кодом тестов (0 = успех, 1 = ошибка)
exit $testExitCode