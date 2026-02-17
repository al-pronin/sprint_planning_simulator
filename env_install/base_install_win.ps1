Write-Host "🚀 Настройка окружения разработки через WSL." -ForegroundColor Cyan

# Проверяем наличие WSL
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Устанавливаю WSL..." -ForegroundColor Yellow
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    wsl --set-default-version 2
    Write-Host "✅ Перезагрузите компьютер и запустите скрипт снова." -ForegroundColor Green
    exit
}
Write-Host "✅ WSL уже установлен."

# Проверяем наличие Debian
$wslCmd = (Get-Command wsl).Source
$distros = & $wslCmd --list --quiet 2>&1
$distros = $distros | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
Write-Host "Найденные дистрибутивы: $($distros -join ', ')"

if (-not ($distros -contains 'Debian')) {
    Write-Host "📦 Debian не найден. Устанавливаю Debian..." -ForegroundColor Yellow
    Write-Host "После установки в консоли будет совершён переход в debian для первичной настройки пользователя.
После настройки введите exit для возвращения в PowerShell." -ForegroundColor Green
    wsl --install -d Debian
    Write-Host "✅ Установка debian завершена успешно, запустите скрипт снова.
Во время выполнения скрипта будет предложено ввести пароль для пользователя, который вы установили." -ForegroundColor Green
    exit
}
Write-Host "✅ Debian уже установлен."

# Обновляем версию WSL
wsl --update

# Проверяем наличие директории
$winPath = (Get-Location).Path
$drive = ($winPath[0].ToString()).ToLower()
$pathWithoutDrive = $winPath.Substring(2)
$unixPath = $pathWithoutDrive -replace "\\", "/"
$wslPath = "/mnt/$drive$unixPath"
$setupDir = "$wslPath/env_install"
wsl -d Debian -- bash -c "ls -la '$setupDir'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка: директория $setupDir недоступна" -ForegroundColor Red
    exit
} else {
    Write-Host "✅ Директория найдена!" -ForegroundColor Green
}

# Запускаем установку окружения внутри Debian
Write-Host "▶ Запуск установки окружения из $setupDir внутри Debian..." -ForegroundColor Cyan
wsl -d Debian -- bash -c "cd $setupDir && chmod +x base_install_wsl.sh && bash base_install_wsl.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при выполнении установки. См. лог выше." -ForegroundColor Red
    exit
} else {
    Write-Host "✅ Установка завершена успешно!" -ForegroundColor Green
}
