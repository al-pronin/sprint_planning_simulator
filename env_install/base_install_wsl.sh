#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/utils.sh"

echo -e "${MAGENTA}"
echo "=========================================="
echo "   Настройка Python окружения в Debian"
echo "=========================================="
echo -e "${NC}"

log_config "Конфигурация:"
log_config "Версия Python: ${PYTHON_VERSION}"
log_config "Версия Poetry: ${POETRY_VERSION}"
log_config "URL проверки VPN: ${VPN_CHECK_URL}"
log_config "Корень pyenv: ${PYENV_ROOT}"
log_config "Файл конфигурации shell: ${SHELL_CONFIG_FILE_BASH}"
log_config "Корень проекта: ${PROJECT_ROOT}"
log_config "Корень gcloud: ${GCLOUD_ROOT}"
echo ""

# Функция для обновления PATH в текущей сессии
update_current_session_path() {
    log_info "Обновление PATH в текущей сессии..."
    source ${SHELL_CONFIG_FILE_BASH}
    export PATH="$PATH"
}

# Функция для обновления установки python из исходников
install_python() {
    cd /tmp
    tar -xf Python-3.10.11.tgz
    cd Python-3.10.11
    sudo ./configure --enable-optimizations
    sudo make altinstall
    sudo rm -f /usr/bin/python3
    sudo ln -s /usr/local/bin/python3.10 /usr/bin/python3
}

install_allure() {
    INSTALL_DIR="/opt/allure-${ALLURE_VERSION}"

    sudo mkdir -p "$INSTALL_DIR"
    sudo tar -xf /tmp/allure.tgz -C "$INSTALL_DIR" --strip-components=1

    sudo ln -sf "${INSTALL_DIR}/bin/allure" /usr/bin/allure

    echo "Allure установлен в ${INSTALL_DIR} и доступен как /usr/bin/allure"
}

# 1. Обновление системы
log_info "Обновление пакетов системы..."
sudo apt update -y && sudo apt upgrade -y
update_current_session_path

# 2. Установка базовых инструментов
log_info "Установка зависимостей..."
sudo apt install -y git curl wget unzip build-essential zlib1g-dev \
    libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncurses5-dev libgdbm-dev libnss3-dev ca-certificates zip

# 3. Проверка подключения к VPN
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

# 4. Проверка и установка pyenv
log_info "Проверка установки pyenv..."
if command -v $PYENV_BIN &>/dev/null; then
    log_success "pyenv уже установлен: $($PYENV_BIN --version)"
else
    log_info "Установка pyenv из ${PYENV_INSTALL_URL}..."
    if ! run_command "curl -fsSL ${PYENV_INSTALL_URL} | bash" "Установка pyenv"; then
        confirm_continue "Исправьте проблему с установкой pyenv"
    fi

    # Добавление pyenv в shell
    if ! grep -q 'pyenv init' "${SHELL_CONFIG_FILE_BASH}"; then
        if ! run_command "echo 'export PYENV_ROOT=\"${PYENV_ROOT}\"' >> \"${SHELL_CONFIG_FILE_BASH}\"" "Добавление PYENV_ROOT в конфигурацию"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "echo '[[ -d ${PYENV_ROOT}/bin ]] && export PATH=\"${PYENV_ROOT}/bin:\$PATH\"' >> \"${SHELL_CONFIG_FILE_BASH}\"" "Добавление PATH pyenv"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "echo 'eval \"\$(pyenv init - bash)\"' >> \"${SHELL_CONFIG_FILE_BASH}\"" "Добавление инициализации pyenv"; then
            confirm_continue "Исправьте проблему с настройкой pyenv"
        fi

        if ! run_command "source \"${SHELL_CONFIG_FILE_BASH}\"" "Обновление конфигурации shell"; then
            confirm_continue "Исправьте проблему с обновлением конфигурации shell"
        fi
    fi

    if command -v $PYENV_BIN &>/dev/null; then
        log_success "pyenv успешно установлен: $($PYENV_BIN --version)"
    else
        log_error "Не удалось установить pyenv"
        confirm_continue "Исправьте проблему с установкой pyenv"
    fi
fi

# 5. Установка Python
log_info "Проверка установки Python ${PYTHON_VERSION}..."
if command $PYTHON_BIN --version | grep -q "$PYTHON_VERSION"; then
    log_success "$($PYTHON_BIN --version) уже установлен вручную"
else
    log_info "Пробую системную установку..."
    if sudo wget "https://python.org/ftp/python/${PYTHON_VERSION_FULL}/Python-${PYTHON_VERSION_FULL}.tgz" -O "/tmp/Python-${PYTHON_VERSION_FULL}.tgz"; then
#             sudo curl -k -o /tmp/Python-3.10.11.tgz https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz # без проверки сертификатов
        install_python
        log_success "Python ${PYTHON_VERSION} установлен через wget и назначен как /usr/bin/python3"
    else
        log_warning "Скачать не удалось. Придётся скачивать вручную..."
        log_warning "Нужно самостоятельно перейти в браузере по ссылке https://python.org/ftp/python/${PYTHON_VERSION_FULL}/Python-${PYTHON_VERSION_FULL}.tgz
Скачанный файл нужно положить через проводник Windows по адресу \\wsl.localhost\Debian\tmp и перезапустить скрипт"
        install_python
        log_success "Python ${PYTHON_VERSION} установлен вручную и назначен как /usr/bin/python3"
    fi
fi

# 6. Проверка и установка pipx
log_info "Проверка установки pipx..."
if command -v pipx &>/dev/null; then
    log_success "pipx уже установлен: $(pipx --version)"
else
    log_info "Установка pipx..."
    if ! run_command "python3 -m pip install --user pipx" "Установка pipx"; then
        confirm_continue "Исправьте проблему с установкой pipx"
    fi

    if ! run_command "python3 -m pipx ensurepath" "Добавление pipx в PATH"; then
        confirm_continue "Исправьте проблему с настройкой pipx"
    fi

    update_current_session_path
    export PATH="${LOCAL_BIN}:$PATH"

    if command -v pipx &>/dev/null; then
        log_success "pipx успешно установлен: $(pipx --version)"
    else
        log_error "Не удалось установить pipx"
        confirm_continue "Исправьте проблему с установкой pipx"
    fi
fi

# 7. Проверка и установка Poetry
log_info "Проверка установки Poetry ${POETRY_VERSION}..."
if command -v poetry &>/dev/null; then
    if [[ $(poetry --version) == *"${POETRY_VERSION}"* ]]; then
        log_success "Poetry ${POETRY_VERSION} уже установлен: $(poetry --version)"
    else
        CURRENT_POETRY_VER=$(poetry --version)
        log_warning "Найден Poetry (${CURRENT_POETRY_VER}), но не версия ${POETRY_VERSION}"
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

# 8. Проверка и установка gcloud CLI
log_info "Проверка установки gcloud CLI..."
if ! command -v gcloud &>/dev/null; then
  log_info "Устанавливаю Google Cloud CLI..."
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
  sudo apt-get install -y apt-transport-https ca-certificates gnupg
  curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
  sudo apt update && sudo apt install -y google-cloud-cli
  gcloud init
else
  log_success "gcloud уже установлен: $(gcloud --version | head -1)"
fi

# 9. Настройка gcloud CLI
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

# 10. Настройка репозитория Poetry
log_info "Настройка репозитория Poetry..."
if command -v gcloud &>/dev/null && gcloud auth list --format="value(account)" | grep -q "@"; then
    if ! run_command "cd \"${PROJECT_ROOT}\" && poetry config http-basic.contactpay-python-repository oauth2accesstoken \$(gcloud auth print-access-token)" "Настройка репозитория Poetry с gcloud аутентификацией"; then
        confirm_continue "Исправьте проблему с настройкой репозитория Poetry"
    fi
else
    log_warning "gcloud не установлен или не аутентифицирован, пропускаем настройку репозитория"
fi

# 11. Установка зависимостей проекта
log_info "Установка зависимостей проекта..."
if ! run_command "cd \"${PROJECT_ROOT}\" && poetry env use $PYTHON_VERSION && poetry install" "Установка зависимостей через Poetry"; then
    confirm_continue "Исправьте проблему с установкой зависимостей"
fi

# 12. Установка Playwright
log_info "Установка Playwright..."
if ! command -v playwright &>/dev/null; then
    if [[ $(playwright --version) == *"${PLAYWRIGHT_VERSION}"* ]]; then
        log_success "Playwright установлен: $(playwright --version)"
    else
        run_command "python3 -m pip install playwright==${PLAYWRIGHT_VERSION}" "Устанавливаю Playwright ${PLAYWRIGHT_VERSION}"
        playwright install-deps
        playwright install
        log_success "Playwright установлен: $(playwright --version)"
    fi
else
    log_success "Playwright уже установлен: $(playwright --version)"
fi

# 13. PostgreSQL
log_info "Проверка установки PostgreSQL..."
if ! command -v psql &>/dev/null; then
  log_info "Устанавливаю PostgreSQL..."
  sudo apt install -y postgresql postgresql-contrib
else
  log_success "PostgreSQL уже установлен: $(psql --version)"
fi

# 14. JAVA
log_info "Проверка и установка Java (для Allure)..."
if ! command -v java &>/dev/null; then
    if ! run_command "sudo apt-get install -y openjdk-25-jre" "Устанавливка OpenJDK 25"; then
        confirm_continue "Откройте терминал Debian и выполните команду apt search openjdk | grep jre. Затем укажите в команде выше (openjdk-25-jre) цифру из последнее версии результата"
    fi
    JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
    export JAVA_HOME
    export PATH="$JAVA_HOME/bin:$PATH"

    log_success "Java установлена: $(java --version)"
    log_info "JAVA_HOME=$JAVA_HOME"
fi

# 15. Allure
if ! command -v allure &>/dev/null; then
    log_info "Устанавливаю Allure..."
    if wget "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" -O /tmp/allure.tgz; then
        install_allure
    else
        log_warning "Скачать не удалось. Придётся скачивать вручную..."
        log_warning "Нужно самостоятельно перейти в браузере по ссылке https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz.
Скачанный файл нужно положить через проводник Windows по адресу \\wsl.localhost\Debian\tmp и перезапустить скрипт"
        install_allure
    fi
    log_success "Allure установлен через wget и назначен как /usr/bin/allure"
else
  log_success "Allure уже установлен: $(allure --version)"
fi

# 16. Проверка и создание .env файла
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

# 17. Проверка и создание settings.local.yaml
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

log_success "Python ${PYTHON_VERSION_FULL} с Poetry ${POETRY_VERSION} готов к использованию!"
log_success "gcloud CLI установлен и настроен"
log_success "Все конфигурационные файлы созданы и настроены"
echo ""

PYTHON_PATH=$(poetry run which python)

log_info "1. В правом нижнем углу нажми на интерпретатор."
log_info "Add New Interpreter -> On WSL -> Linux Distribution: Debian -> Next -> Existing -> ... -> "
log_info "Вручную перейдите по адресу ${CYAN}${PYTHON_PATH}${NC} выберите и примените настройку"
echo ""

log_info "2. Проверьте настройки в .env файле:"
echo -e "${CYAN}${PROJECT_ROOT}/.env${NC}"
log_info "   По умолчанию установлен ENV_FOR_DYNACONF=testing"
log_info "   Для staging окружения раскомментируйте соответствующую строку"
echo ""

log_info "3. Откройте терминал в pycharm, выбрав Debian. Введите:"
echo -e "${CYAN}cd ${PROJECT_ROOT}${NC}"
echo -e "${CYAN}poetry shell${NC}"
echo ""

log_info "4. Запустите тесты для проверки окружения:"
echo -e "${CYAN}poetry run pytest cpay_autotests/smoke/invoice/acquiring/test_success_scenarios.py::TestHappyCardDataParameters::test_happy_card_data_parametrization${NC}"

log_info "5. Запустите тест ${CYAN}TestCardIcons${NC} из директории ниже через GUI (зелёная стрелочка в pycharm):"
echo -e "${CYAN}cpay_autotests/web_ui/card_ui/angra/test_default_template/test_card_form.py${NC}"

echo -e "${GREEN}"
echo "=========================================="
echo "  ПРОЧИТАЙТЕ В ЛОГЕ ВЫШЕ ПУНКТЫ 1-5 И ВЫПОЛНИТЕ ДЕЙСТВИЯ ИЗ НИХ! 🚀"
echo "=========================================="
echo -e "${NC}"
