#!/bin/bash
# Configuration variables for the installation script

# Python and package versions
PYTHON_VERSION="3.10"
PYTHON_VERSION_FULL="3.10.11"
POETRY_VERSION="1.6.1"
PLAYWRIGHT_VERSION="1.56.0"
ALLURE_VERSION="2.35.1"

# Installation URLs
PYENV_INSTALL_URL="https://pyenv.run"
GCLOUD_INSTALL_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz"
VPN_CHECK_URL="https://my.sandbox.m3ii.tech/auth"  # URL for VPN check
HOMEBREW_INSTALL_URL="https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"

# Path configurations
PYENV_ROOT="$HOME/.pyenv"
#PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
SHELL_CONFIG_FILE="$HOME/.zshrc"
#SHELL_CONFIG_FILE_BASH="$HOME/.bashrc" # for interactive sessions
SHELL_CONFIG_FILE_BASH="$HOME/.bash_profile" # for non-interactive sessions
PYENV_BIN="$PYENV_ROOT/bin/pyenv"
LOCAL_BIN="$HOME/.local/bin"
PYTHON_BIN="/usr/bin/python3"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GCLOUD_ROOT="$HOME/google-cloud-sdk"

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Spinner animation characters
SPINNER=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
