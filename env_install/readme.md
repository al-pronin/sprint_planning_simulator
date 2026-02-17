## Установки локального Python-окружения
Запуск скрипта установки Python-окружения.

MacOS:
Предостатвить скрипту права на запуск и запустить
```bash
 chmod +x base_install_mac.sh && ./base_install_mac.sh
```
Windows:
Открыть PowerShell в pycharm и выполнить:
```bash
 cd C:\Users\your_user_name\PycharmProjects\autotests
 Set-ExecutionPolicy Bypass -Scope Process -Force
 env_install\base_install_win.ps1
```
в случае ошибки как эта
./config.sh: line 3: $'\r': command not found
нужно в файле, который указан в ошибке изменить каретку с CRLF на LF


Скрипт выполнит следующие действия:
- Проверка VPN подключения
- Установка и настройка zsh
- Установка pyenv
- Установка Python 3.10
- Установка pipx
- Установка Poetry
- Установка Google Cloud CLI
- Аутентификация в GCP
- Настройка Poetry репозитория
- Установка зависимостей проекта
- Установка Playwright браузеров
- Установка PostgreSQL
- Установка Allure

# Notes
### Логин в корпоративный репозиторий Python-пакетов
[Обсуждение в Slack](https://contactpay.slack.com/archives/CKVUFTLKH/p1734091916532089)

### 123


### .env

###
settings.local.yaml
