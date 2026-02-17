#!/bin/bash
# Utility functions for the installation script

# Source the configuration file
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# Function for displaying spinner animation
spinner() {
    local pid=$!
    local delay=0.1
    local i=0
    while kill -0 $pid 2>/dev/null; do
        printf "\r[${BLUE}${SPINNER[i]}${NC}] $1"
        i=$(( (i+1) % 8 ))
        sleep $delay
    done
    printf "\r\033[K"
}

# Function for logging information messages
log_info() {
    printf "[${BLUE}INFO${NC}] $1\n"
}

# Function for logging success messages
log_success() {
    printf "[${GREEN}SUCCESS${NC}] $1\n"
}

# Function for logging warning messages
log_warning() {
    printf "[${YELLOW}WARNING${NC}] $1\n"
}

# Function for logging error messages
log_error() {
    printf "[${RED}ERROR${NC}] $1\n"
}

# Function for logging configuration
log_config() {
    printf "[${CYAN}CONFIG${NC}] $1\n"
}

# Function for executing commands with logging and error handling
run_command() {
    local cmd="$1"
    local description="$2"

    log_info "Выполняется: $description"
    echo -e "${CYAN}Команда: $cmd${NC}"

    eval $cmd
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_success "$description завершено успешно"
        return 0
    else
        log_error "$description завершено с ошибкой (код: $exit_code)"

        echo -e "${RED}"
        echo "=========================================="
        echo "  ОШИБКА ВЫПОЛНЕНИЯ!"
        echo "=========================================="
        echo -e "${NC}"
        log_error "Не удалось выполнить: $description"
        log_error "Код ошибки: $exit_code"
        log_info "Пожалуйста, исправьте проблему и перезапустите скрипт"
        log_info "Для продолжения нажмите Enter после исправления..."
        read -p "Или нажмите Ctrl+C для выхода" </dev/tty

        return $exit_code
    fi
}

# Function for checking VPN connection
check_vpn_connection() {
    log_info "Проверка подключения к VPN..."
    log_info "Выполняется запрос к: ${VPN_CHECK_URL}"

    # Try to execute request with timeout
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 15 "${VPN_CHECK_URL}" 2>/dev/null)
    local curl_exit_code=$?

    if [ $curl_exit_code -eq 0 ]; then
        if [ "$response" = "200" ] || [ "$response" = "301" ] || [ "$response" = "302" ] ; then
            log_success "VPN подключение активно (HTTP код: $response)"
            return 0
        else
            log_error "VPN недоступен. Получен HTTP код: $response"
            return 1
        fi
    else
        case $curl_exit_code in
            6)  log_error "VPN недоступен: Не удается разрешить хост (DNS ошибка)" ;;
            7)  log_error "VPN недоступен: Не удается подключиться к хосту" ;;
            28) log_error "VPN недоступен: Таймаут подключения" ;;
            *)  log_error "VPN недоступен: Ошибка curl (код: $curl_exit_code)" ;;
        esac
        return 1
    fi
}

# Function for user confirmation
confirm_continue() {
    local message="$1"
    echo -e "${YELLOW}"
    echo "=========================================="
    echo "  $message"
    echo "=========================================="
    echo -e "${NC}"
    read -p "Нажмите Enter после завершения, или Ctrl+C для выхода..." </dev/tty
}
