#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Check if script is run as root
if [ "$(id -u)" -eq 0 ]; then
    warn "This script should not be run as root. Please run as a normal user."
    exit 1
fi

info "Starting ai.cli installation..."

# Check for required system commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 is required but not installed. Please install it and try again."
    fi
}

# Check for Python 3.8+
check_python_version() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3.8 or higher is required but not installed."
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ $PYTHON_MAJOR -lt 3 ] || [ $PYTHON_MAJOR -eq 3 -a $PYTHON_MINOR -lt 8 ]; then
        error "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
    fi
    
    info "Found Python $PYTHON_VERSION"
}

# Check for pip
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        warn "pip3 not found. Attempting to install..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-pip
        else
            error "Could not install pip. Please install pip3 manually and try again."
        fi
    fi
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
}

# Check for virtualenv
check_virtualenv() {
    if ! python3 -m pip show virtualenv &> /dev/null; then
        info "Installing virtualenv..."
        python3 -m pip install --user virtualenv
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

# Create and activate virtual environment
setup_venv() {
    VENV_DIR="$PWD/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        error "Failed to create virtual environment"
    fi
}

# Install Python dependencies
install_dependencies() {
    info "Installing Python dependencies..."
    
    # Check if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        warn "requirements.txt not found. Installing default dependencies..."
        pip install rich pyyaml
    fi
    
    # Install the package in development mode
    pip install -e .
}

# Create configuration directory
setup_config() {
    CONFIG_DIR="$HOME/.ai.cli"
    if [ ! -d "$CONFIG_DIR" ]; then
        info "Creating configuration directory..."
        mkdir -p "$CONFIG_DIR"
        # Set appropriate permissions
        chmod 700 "$CONFIG_DIR"
    fi
}

# Add to PATH if not already there
add_to_path() {
    local shell_rc=""
    local export_line="export PATH=\"$HOME/.local/bin:$PATH\""
    
    if [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.bashrc"
    fi
    
    if ! grep -q "$export_line" "$shell_rc" 2>/dev/null; then
        info "Adding ai.cli to PATH in $shell_rc..."
        echo "$export_line" >> "$shell_rc"
        info "Please run 'source $shell_rc' or restart your terminal to update PATH"
    fi
}

# Main installation process
main() {
    # Check system dependencies
    check_command python3
    check_python_version
    check_pip
    check_virtualenv
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup configuration
    setup_config
    
    # Add to PATH
    add_to_path
    
    info "\nInstallation complete! 🎉"
    info "To start using ai.cli, run:"
    echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
    echo -e "  ${YELLOW}ai.cli --help${NC}"
    echo -e "\nTo deactivate the virtual environment when done, run:\n  ${YELLOW}deactivate${NC}"
}

# Run the installation
main
