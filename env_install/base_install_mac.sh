#!/bin/bash
# TODO ретраи при установке pyenv

# Source configuration and utility functions
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
SHELL_CONFIG_FILE=$(get_current_shell_config)
source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/utils.sh"

# Вывод заголовка с конфигурации
echo -e "${MAGENTA}"
echo "=========================================="
echo "  Настройка Python окружения для macOS"
echo "=========================================="
echo -e "${NC}"

log_config "Конфигурация:"
log_config "Файл конфигурации shell: ${SHELL_CONFIG_FILE}"
log_config "Версия Python: ${PYTHON_VERSION}"
log_config "Версия Poetry: ${POETRY_VERSION}"
log_config "URL проверки VPN: ${VPN_CHECK_URL}"
log_config "Корень pyenv: ${PYENV_ROOT}"
log_config "Файл конфигурации shell: ${SHELL_CONFIG_FILE}"
log_config "Корень проекта: ${PROJECT_ROOT}"
log_config "Корень gcloud: ${GCLOUD_ROOT}"
echo ""


# 0. Проверка и установка zsh
log_info "Проверка установки zsh..."
if command -v zsh &>/dev/null; then
    log_success "zsh уже установлен: $(zsh --version | head -1)"
else
    log_info "Установка zsh через Homebrew..."
    if command -v brew &>/dev/null; then
        if ! run_command "brew install zsh" "Установка zsh"; then
            confirm_continue "Исправьте проблему с установкой zsh"
        fi

        # Установка zsh как оболочки по умолчанию
        if command -v zsh &>/dev/null; then
            if ! run_command "sudo sh -c 'echo \"/usr/local/bin/zsh\" >> /etc/shells'" "Добавление zsh в список разрешенных оболочек"; then
                confirm_continue "Исправьте проблему с настройкой zsh"
            fi

            if ! run_command "chsh -s /usr/local/bin/zsh" "Установка zsh как оболочки по умолчанию"; then
                confirm_continue "Исправьте проблему с установкой zsh по умолчанию"
            fi

            log_success "zsh успешно установлен и установлен как оболочка по умолчанию"
        else
            log_error "Не удалось установить zsh"
            confirm_continue "Исправьте проблему с установкой zsh"
        fi
    else
        log_error "Homebrew не установлен. Установите Homebrew или zsh вручную"
        log_info "Для установки zsh вручную:"
        echo -e "${CYAN}Установите Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
        echo -e "${CYAN}Или установите zsh через другие методы${NC}"
        confirm_continue "Установите Homebrew или zsh вручную"
    fi
fi

# Функция для определения текущего shell
get_current_shell_config() {
    local shell_name=$(basename "$SHELL")
    case "$shell_name" in
        "zsh")
            if [ -f "$HOME/.zshrc" ]; then
                echo "$HOME/.zshrc"
            elif [ -f "$HOME/.zprofile" ]; then
                echo "$HOME/.zprofile"
            else
                echo "$HOME/.zshrc"
            fi
            ;;
        "bash")
            if [ -f "$HOME/.bash_profile" ]; then
                echo "$HOME/.bash_profile"
            elif [ -f "$HOME/.bashrc" ]; then
                echo "$HOME/.bashrc"
            else
                echo "$HOME/.bash_profile"
            fi
            ;;
        *)
            if [ -f "$HOME/.profile" ]; then
                echo "$HOME/.profile"
            else
                echo "$HOME/.bash_profile"
            fi
            ;;
    esac
}

# Функция для обновления PATH в текущей сессии
update_current_session_path() {
    log_info "Обновление PATH в текущей сессии..."
    local config_file=$(get_current_shell_config)

    if [ -f "$config_file" ]; then
        # Безопасная загрузка конфигурации
        if [ -n "$ZSH_VERSION" ]; then
            # Для zsh используем source
            source "$config_file" 2>/dev/null || true
        elif [ -n "$BASH_VERSION" ]; then
            # Для bash используем source или .
            source "$config_file" 2>/dev/null || . "$config_file" 2>/dev/null || true
        fi
    else
        log_warning "Конфигурационный файл не найден: $config_file"
        log_info "Создайте файл конфигурации или продолжайте - изменения вступят после перезапуска терминала"
    fi

    # Принудительно обновляем PATH
    export PATH="$PATH"
}

# 0. Проверка и установка Homebrew
log_info "Проверка установки Homebrew..."
if command -v brew &>/dev/null; then
    log_success "Homebrew уже установлен: $(brew --version | head -1)"
else
    log_info "Установка Homebrew..."
    log_info "Выполняется установка из: ${HOMEBREW_INSTALL_URL}"

    # Установка Homebrew
    if ! run_command "/bin/bash -c \"\$(curl -fsSL ${HOMEBREW_INSTALL_URL})\"" "Установка Homebrew"; then
        log_error "Не удалось установить Homebrew автоматически"
        log_info "Пожалуйста, установите Homebrew вручную:"
        echo -e "${CYAN}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
        confirm_continue "Установите Homebrew вручную и нажмите Enter для продолжения"
    fi

    # Проверка успешности установки
    if command -v brew &>/dev/null; then
        log_success "Homebrew успешно установлен: $(brew --version | head -1)"

        # Добавление Homebrew в PATH если необходимо
        if ! echo "$PATH" | grep -q "/usr/local/bin\|/opt/homebrew/bin"; then
            log_info "Добавление Homebrew в PATH..."
            if [ -d "/opt/homebrew/bin" ]; then
                # Apple Silicon
                if ! run_command "echo 'export PATH=\"/opt/homebrew/bin:\$PATH\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление Homebrew в PATH (Apple Silicon)"; then
                    confirm_continue "Исправьте проблему с настройкой Homebrew PATH"
                fi
            elif [ -d "/usr/local/bin" ]; then
                # Intel
                if ! run_command "echo 'export PATH=\"/usr/local/bin:\$PATH\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление Homebrew в PATH (Intel)"; then
                    confirm_continue "Исправьте проблему с настройкой Homebrew PATH"
                fi
            fi

            update_current_session_path
        fi
    else
        log_error "Homebrew не установлен после попытки автоматической установки"
        confirm_continue "Установите Homebrew вручную и нажмите Enter для продолжения"
    fi
fi

# 0. Проверка подключения к VPN
log_info "Проверка подключения к VPN..."
if ! check_vpn_connection; then
    echo -e "${RED}"
    echo "=========================================="
    echo "  ОШИБКА: НЕТ ПОДКЛЮЧЕНИЯ К VPN!"
    echo "=========================================="
    echo -e "${NC}"
    log_error "Пожалуйста, подключитесь к корпоративному VPN и запустите скрипт снова"
    log_info "Если VPN подключен, но скрипт не работает, проверьте:"
    log_info "1. Корректность URL: ${VPN_CHECK_URL}"
    log_info "2. Настройки прокси (если используются)"
    log_info "3. Доступность сети"
    confirm_continue "Подключитесь к VPN и нажмите Enter для продолжения"
fi

# 3. Проверка и установка pyenv
log_info "Проверка установки pyenv..."
if command -v pyenv &>/dev/null; then
    log_success "pyenv уже установлен: $(pyenv --version)"
else
    log_info "Установка pyenv из ${PYENV_INSTALL_URL}..."
    if ! run_command "curl -fsSL ${PYENV_INSTALL_URL} | bash" "Установка pyenv"; then
        confirm_continue "Исправьте проблему с установкой pyenv"
    fi

    # Добавление pyenv в shell
    if ! grep -q 'pyenv init' "${SHELL_CONFIG_FILE}"; then
        if ! run_command "echo 'export PYENV_ROOT=\"${PYENV_ROOT}\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление PYENV_ROOT в конфигурацию"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "echo 'command -v pyenv >/dev/null || export PATH=\"${PYENV_ROOT}/bin:\$PATH\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление PATH pyenv"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "echo 'eval \"\$(pyenv init -)\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление инициализации pyenv"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "source \"${SHELL_CONFIG_FILE}\"" "Обновление конфигурации shell"; then
            confirm_continue "Исправьте проблему с обновлением конфигурации shell"
        fi
    fi

    if command -v pyenv &>/dev/null; then
        log_success "pyenv успешно установлен: $(pyenv --version)"
    else
        log_error "Не удалось установить pyenv"
        confirm_continue "Исправьте проблему с установкой pyenv"
    fi
fi

# 2. Проверка и установка Python (точная версия)
log_info "Проверка установки Python ${PYTHON_VERSION_FULL}..."
if pyenv versions | grep -q "${PYTHON_VERSION_FULL}"; then
    log_success "Python ${PYTHON_VERSION_FULL} уже установлен"
else
    log_info "Установка Python ${PYTHON_VERSION_FULL}..."
    if ! run_command "pyenv install \"${PYTHON_VERSION_FULL}\"" "Установка Python ${PYTHON_VERSION_FULL}"; then
        confirm_continue "Исправьте проблему с установкой Python"
    fi

    if pyenv versions | grep -q "${PYTHON_VERSION_FULL}"; then
        log_success "Python ${PYTHON_VERSION_FULL} успешно установлен"
        if ! run_command "pyenv global \"${PYTHON_VERSION_FULL}\"" "Установка Python ${PYTHON_VERSION_FULL} как глобальной версии"; then
            confirm_continue "Исправьте проблему с настройкой Python"
        fi
    else
        log_error "Не удалось установить Python ${PYTHON_VERSION_FULL}"
        confirm_continue "Исправьте проблему с установкой Python"
    fi
fi

# 3. Проверка и установка pipx
log_info "Проверка установки pipx..."
if command -v pipx &>/dev/null; then
    log_success "pipx уже установлен: $(pipx --version)"
else
    log_info "Установка pipx..."

    # Пробуем установить через pip
    if ! run_command "python -m pip install --user pipx" "Установка pipx"; then
        # Если не сработало, пробуем через brew
        log_info "Попытка установки pipx через Homebrew..."
        if ! run_command "brew install pipx" "Установка pipx через Homebrew"; then
            confirm_continue "Исправьте проблему с установкой pipx"
        fi
    fi

    # Добавляем pipx в PATH
    log_info "Выполняется: Добавление pipx в PATH"

    # Сначала попробуем через ensurepath
    if command -v python &>/dev/null; then
        if python -m pipx ensurepath >/dev/null 2>&1; then
            log_success "pipx добавлен в PATH через ensurepath"
        fi
    fi

    # Вручную добавляем в PATH если нужно
    local pipx_bin_dir="$HOME/.local/bin"
    if [ -d "$pipx_bin_dir" ] && [[ ":$PATH:" != *":$pipx_bin_dir:"* ]]; then
        export PATH="$pipx_bin_dir:$PATH"
        log_info "Добавлен $pipx_bin_dir в PATH текущей сессии"
    fi

    # Проверяем успешность установки
    if command -v pipx &>/dev/null; then
        log_success "pipx успешно установлен: $(pipx --version)"
        INSTALL_SUCCESS=true
    else
        log_error "Не удалось установить pipx"
        # Не завершаем скрипт, продолжаем с предупреждением
        log_warning "Продолжаем без pipx. Установите его вручную позже."
        INSTALL_SUCCESS=false
    fi
fi

# 4. Проверка и установка Poetry
log_info "Проверка установки Poetry ${POETRY_VERSION}..."
if command -v poetry &>/dev/null; then
    if [[ $(poetry --version) == *"${POETRY_VERSION}"* ]]; then
        log_success "Poetry ${POETRY_VERSION} уже установлен: $(poetry --version)"
    else
        CURRENT_POETRY_VER=$(poetry --version)
        log_warning "Найден Poetry (${CURRENT_POETRY_VER}) но не версия ${POETRY_VERSION}"
        log_info "Установка Poetry ${POETRY_VERSION}..."
        if ! run_command "pipx install poetry==\"${POETRY_VERSION}\"" "Установка Poetry ${POETRY_VERSION}"; then
            confirm_continue "Исправьте проблему с установкой Poetry"
        fi
        log_success "Poetry ${POETRY_VERSION} успешно установлен"
    fi
else
    log_info "Установка Poetry ${POETRY_VERSION}..."
    if ! run_command "pipx install poetry==\"${POETRY_VERSION}\"" "Установка Poetry ${POETRY_VERSION}"; then
        confirm_continue "Исправьте проблему с установкой Poetry"
    fi

    if command -v poetry &>/dev/null; then
        log_success "Poetry успешно установлен: $(poetry --version)"
    else
        log_error "Не удалось установить Poetry"
        confirm_continue "Исправьте проблему с установкой Poetry"
    fi
fi

# 5. Проверка и установка gcloud CLI
log_info "Проверка установки gcloud CLI..."
if command -v gcloud &>/dev/null; then
    log_success "gcloud уже установлен: $(gcloud --version | head -1)"
else
    log_info "Установка gcloud CLI..."

    # Скачивание и распаковка gcloud CLI
    if ! run_command "curl -O ${GCLOUD_INSTALL_URL}" "Скачивание gcloud CLI"; then
        confirm_continue "Исправьте проблему со скачиванием gcloud CLI"
    fi

    if ! run_command "tar -xf google-cloud-cli-linux-x86_64.tar.gz -C \$HOME" "Распаковка gcloud CLI"; then
        confirm_continue "Исправьте проблему с распаковкой gcloud CLI"
    fi

    if ! run_command "rm google-cloud-cli-linux-x86_64.tar.gz" "Удаление архива gcloud"; then
        log_warning "Не удалось удалить архив gcloud, продолжаем..."
    fi

    # Добавление gcloud в PATH
    if ! grep -q 'google-cloud-sdk' "${SHELL_CONFIG_FILE}"; then
        if ! run_command "echo 'export PATH=\"\$HOME/google-cloud-sdk/bin:\$PATH\"' >> \"${SHELL_CONFIG_FILE}\"" "Добавление gcloud в PATH"; then
            confirm_continue "Исправьте проблему с настройкой gcloud"
        fi

        if ! run_command "source \"${SHELL_CONFIG_FILE}\"" "Обновление конфигурации shell"; then
            confirm_continue "Исправьте проблему с обновлением конфигурации shell"
        fi
    fi

    # Запуск инсталляционного скрипта
    if ! run_command "CLOUDSDK_PYTHON=$(which python3) \$HOME/google-cloud-sdk/install.sh --quiet --path-update true" "Запуск инсталляционного скрипта gcloud"; then
        confirm_continue "Исправьте проблему с установкой gcloud"
    fi

    if command -v gcloud &>/dev/null; then
        log_success "gcloud CLI успешно установлен: $(gcloud --version | head -1)"
    else
        log_error "Не удалось установить gcloud CLI"
        confirm_continue "Исправьте проблему с установкой gcloud CLI"
    fi
fi

# 6. Настройка gcloud CLI
log_info "Настройка gcloud CLI..."
if gcloud auth list --format="value(account)" | grep -q "@"; then
    log_success "gcloud уже аутентифицирован: $(gcloud auth list --format='value(account)')"
else
    log_warning "gcloud не аутентифицирован"
    log_info "Сейчас откроется окно браузера для логина в корпоративный Google-аккаунт"
    if ! run_command "gcloud auth login" "Аутентификация в gcloud"; then
        confirm_continue "Исправьте проблему с аутентификацией в gcloud"
    fi
    confirm_continue "Завершите аутентификацию в gcloud"
fi

# 7. Настройка репозитория Poetry
log_info "Настройка репозитория Poetry..."
if command -v gcloud &>/dev/null && gcloud auth list --format="value(account)" | grep -q "@"; then
    if ! run_command "cd \"${PROJECT_ROOT}\" && poetry config http-basic.contactpay-python-repository oauth2accesstoken \$(gcloud auth print-access-token)" "Настройка репозитория Poetry с gcloud аутентификацией"; then
        confirm_continue "Исправьте проблему с настройкой репозитория Poetry"
    fi
else
    log_warning "gcloud не установлен или не аутентифицирован, пропускаем настройку репозитория"
fi

# Получаем информацию о текущем окружении Poetry (если оно есть)
CURRENT_ENV_PATH=$(cd "${PROJECT_ROOT}" && poetry env info -p 2>/dev/null || true)
CURRENT_PY_VER=""
if [ -n "${CURRENT_ENV_PATH}" ]; then
    CURRENT_PY_VER=$(cd "${PROJECT_ROOT}" && poetry run python -c 'import platform;print(platform.python_version())' 2>/dev/null || true)
fi

# Если окружения нет или версия Python отличается — пересоздаем
if [ -z "${CURRENT_ENV_PATH}" ] || [ "${CURRENT_PY_VER}" != "${PYTHON_VERSION_FULL}" ]; then
    if [ -n "${CURRENT_ENV_PATH}" ]; then
        log_warning "Найдено Poetry-окружение с Python ${CURRENT_PY_VER:-unknown}, требуется ${PYTHON_VERSION_FULL}. Пересоздаем..."
        if ! run_command "cd \"${PROJECT_ROOT}\" && poetry env remove \"$(basename \"${CURRENT_ENV_PATH}\")" "Удаление текущего Poetry-окружения проекта"; then
            confirm_continue "Исправьте проблему с удалением Poetry-окружения"
        fi
    else
        log_info "Poetry-окружение не найдено. Будет создано новое."
    fi

    # Создаем окружение с нужным интерпретатором
    if [ -x "${DESIRED_PY}" ]; then
        if ! run_command "cd \"${PROJECT_ROOT}\" && poetry env use \"${DESIRED_PY}\"" "Создание Poetry-окружения с Python ${PYTHON_VERSION_FULL}"; then
            confirm_continue "Исправьте проблему с созданием Poetry-окружения"
        fi
    else
        # В крайнем случае укажем версию как строку — Poetry попытается найти подходящий интерпретатор в PATH
        log_warning "Не удалось найти бинарник Python по пути ${DESIRED_PY}. Попытка выбрать по версии ${PYTHON_VERSION_FULL} через PATH"
        if ! run_command "cd \"${PROJECT_ROOT}\" && poetry env use ${PYTHON_VERSION_FULL}" "Выбор интерпретатора Python по версии"; then
            confirm_continue "Исправьте проблему с выбором интерпретатора Python"
        fi
    fi

    # Обновляем переменные состояния после пересоздания
    CURRENT_ENV_PATH=$(cd "${PROJECT_ROOT}" && poetry env info -p 2>/dev/null || true)
    CURRENT_PY_VER=$(cd "${PROJECT_ROOT}" && poetry run python -c 'import platform;print(platform.python_version())' 2>/dev/null || true)
fi

log_success "Poetry-окружение: ${CURRENT_ENV_PATH:-unknown}, Python: ${CURRENT_PY_VER:-unknown}"

# Установка зависимостей
log_info "Установка зависимостей проекта..."
if ! run_command "cd \"${PROJECT_ROOT}\" && poetry install" "Установка зависимостей через Poetry"; then
    confirm_continue "Исправьте проблему с установкой зависимостей"
fi

# 9. Установка Playwright
log_info "Установка Playwright..."
if ! run_command "cd \"${PROJECT_ROOT}\" && poetry run playwright install" "Установка браузеров для Playwright"; then
    confirm_continue "Исправьте проблему с установкой Playwright"
fi

# 10. Установка PostgreSQL через Homebrew
log_info "Проверка установки PostgreSQL..."
if command -v psql &>/dev/null; then
    log_success "PostgreSQL уже установлен: $(psql --version)"
else
    log_info "Установка PostgreSQL через Homebrew..."
    if ! run_command "brew install postgresql" "Установка PostgreSQL"; then
        confirm_continue "Исправьте проблему с установкой PostgreSQL"
    fi
fi

# 11. Установка Allure через Homebrew
log_info "Проверка установки Allure..."
if command -v allure &>/dev/null; then
    log_success "Allure уже установлен: $(allure --version)"
else
    log_info "Установка Allure через Homebrew..."
    if ! run_command "brew install allure" "Установка Allure"; then
        confirm_continue "Исправьте проблему с установкой Allure"
    fi
fi

# 12. Проверка и создание .env файла
log_info "Проверка наличия .env файла..."
if [ -f "${PROJECT_ROOT}/.env" ]; then
    log_success ".env файл уже существует"
else
    log_info "Создание .env файла..."
    if ! run_command "touch ${PROJECT_ROOT}/.env && echo > \"${PROJECT_ROOT}/.env\" << EOF
ENV_FOR_DYNACONF=testing
&& echo >> \"${PROJECT_ROOT}/.env\" << EOF
\# ENV_FOR_DYNACONF=staging
" "Создание .env файла"; then
        confirm_continue "Исправьте проблему с созданием .env файла"
    fi
    log_success ".env файл создан с настройками по умолчанию"
fi

# 13. Проверка и создание settings.local.yaml
SETTINGS_CREATED=false
log_info "Проверка наличия settings.local.yaml..."
if [ -f "${PROJECT_ROOT}/settings.local.yaml" ]; then
    log_success "settings.local.yaml файл уже существует"
else
    log_info "Создание пустого settings.local.yaml файла..."
    if ! run_command "touch \"${PROJECT_ROOT}/settings.local.yaml\"" "Создание settings.local.yaml"; then
        confirm_continue "Исправьте проблему с созданием settings.local.yaml"
    fi
    log_success "Пустой settings.local.yaml файл создан"
    SETTINGS_CREATED=true
fi

# Если settings.local.yaml был только что создан, ждем подтверждения пользователя
if [ "$SETTINGS_CREATED" = true ]; then
    echo -e "${YELLOW}"
    echo "=========================================="
    echo "  НАСТРОЙКА settings.local.yaml"
    echo "=========================================="
    echo -e "${NC}"
    log_info "Заполните файл settings.local.yaml необходимыми настройками"
    echo -e "${CYAN}https://www.notion.so/contactpay/settings-local-yaml-2259bf7184de80e8abe9c033ac74b56a?source=copy_link#2259bf7184de8033adcbd8986ab75ece${NC}"
    echo ""
    log_info "Текущий путь к файлу: ${PROJECT_ROOT}/settings.local.yaml"
    confirm_continue "Заполните settings.local.yaml и нажмите Enter для продолжения"
fi

echo -e "${MAGENTA}"
echo "=========================================="
echo "  Настройка завершена успешно! 🎉"
echo "=========================================="
echo -e "${NC}"

log_success "Python ${PYTHON_VERSION} с Poetry ${POETRY_VERSION} готов к использованию!"
log_success "gcloud CLI установлен и настроен"
log_success "Все конфигурационные файлы созданы и настроены"

echo -e "${YELLOW}"
echo "=========================================="
echo "  ДАЛЬНЕЙШИЕ ШАГИ ДЛЯ НАСТРОЙКИ"
echo "=========================================="
echo -e "${NC}"

log_info "1. Настройте интерпретатор созданного Poetry-окружения в PyCharm:"
echo -e "${CYAN}$(poetry env info --path)/bin/python${NC}"
echo "или"
echo -e "${CYAN}$(poetry run which python)${NC}"
echo ""

log_info "2. Проверьте настройки в .env файле:"
echo -e "${CYAN}${PROJECT_ROOT}/.env${NC}"
log_info "   По умолчанию установлен ENV_FOR_DYNACONF=testing"
log_info "   Для staging окружения раскомментируйте соответствующую строку"
echo ""

log_info "3. Запустите тесты для проверки окружения:"
echo -e "${CYAN}cd ${PROJECT_ROOT} && poetry run pytest${NC}"

echo -e "${GREEN}"
echo "=========================================="
echo "  ОКРУЖЕНИЕ ГОТОВО К РАБОТЕ! 🚀"
echo "=========================================="
echo -e "${NC}"
