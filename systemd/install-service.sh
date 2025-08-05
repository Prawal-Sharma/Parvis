#!/bin/bash
# Pi-Jarvis Production Deployment Installation Script
# Installs and configures the systemd service for always-on operation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="pi-jarvis.service"

echo "🚀 Pi-Jarvis Production Deployment Setup"
echo "======================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if running as correct user
    if [ "$USER" != "raspberry" ]; then
        log_warning "Script should be run as 'raspberry' user"
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        log_error "Python virtual environment not found at $PROJECT_DIR/venv"
        log_info "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    # Check if main components exist
    if [ ! -f "$PROJECT_DIR/assistant/parvis.py" ]; then
        log_error "Main Parvis assistant not found"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

create_directories() {
    log_info "Creating necessary directories..."
    
    # Create log directories
    mkdir -p "$PROJECT_DIR/logs"
    sudo mkdir -p "/var/log/pi-jarvis"
    sudo chown raspberry:raspberry "/var/log/pi-jarvis"
    
    # Ensure models directory exists
    mkdir -p "$PROJECT_DIR/models"
    
    log_success "Directories created"
}

install_systemd_service() {
    log_info "Installing systemd service..."
    
    # Copy service file to system location
    sudo cp "$SCRIPT_DIR/pi-jarvis.service" "/etc/systemd/system/"
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    # Enable service (will start on boot)
    sudo systemctl enable "$SERVICE_NAME"
    
    log_success "Systemd service installed and enabled"
}

install_logrotate() {
    log_info "Installing log rotation configuration..."
    
    # Copy logrotate configuration
    sudo cp "$SCRIPT_DIR/pi-jarvis-logrotate" "/etc/logrotate.d/pi-jarvis"
    
    # Test logrotate configuration
    if sudo logrotate -d /etc/logrotate.d/pi-jarvis >/dev/null 2>&1; then
        log_success "Log rotation configured"
    else
        log_warning "Log rotation configuration may have issues"
    fi
}

install_cron_jobs() {
    log_info "Installing cron jobs for health monitoring..."
    
    # Copy cron configuration
    sudo cp "$SCRIPT_DIR/pi-jarvis-cron" "/etc/cron.d/pi-jarvis"
    
    # Ensure cron service is running
    sudo systemctl enable cron
    sudo systemctl start cron
    
    log_success "Health monitoring cron jobs installed"
}

test_service() {
    log_info "Testing service installation..."
    
    # Start the service
    if sudo systemctl start "$SERVICE_NAME"; then
        log_success "Service started successfully"
        
        # Wait a moment for startup
        sleep 5
        
        # Check service status
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            log_success "Service is running properly"
            
            # Show service status
            echo ""
            log_info "Service Status:"
            systemctl status "$SERVICE_NAME" --no-pager --lines=10
            
        else
            log_error "Service failed to start properly"
            log_info "Check logs with: journalctl -u $SERVICE_NAME -f"
            return 1
        fi
    else
        log_error "Failed to start service"
        return 1
    fi
}

show_management_commands() {
    echo ""
    log_info "Service Management Commands:"
    echo "  Start service:    sudo systemctl start $SERVICE_NAME"
    echo "  Stop service:     sudo systemctl stop $SERVICE_NAME"
    echo "  Restart service:  sudo systemctl restart $SERVICE_NAME"
    echo "  Service status:   systemctl status $SERVICE_NAME"
    echo "  View logs:        journalctl -u $SERVICE_NAME -f"
    echo "  Disable service:  sudo systemctl disable $SERVICE_NAME"
    echo ""
    
    log_info "Health Monitoring:"
    echo "  Manual health check: $SCRIPT_DIR/health-check.sh"
    echo "  View health logs:    tail -f /var/log/pi-jarvis/health-check.log"
    echo "  Weekly status:       $SCRIPT_DIR/status-report.sh"
    echo ""
    
    log_info "The service will automatically start on boot."
}

main() {
    echo "This script will install Pi-Jarvis as a system service."
    echo "The service will:"
    echo "  • Start automatically on boot"
    echo "  • Run in the background continuously"
    echo "  • Monitor health and restart if needed"
    echo "  • Rotate logs to prevent disk issues"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled"
        exit 0
    fi
    
    check_requirements
    create_directories
    install_systemd_service
    install_logrotate
    install_cron_jobs
    
    if test_service; then
        echo ""
        log_success "🎉 Pi-Jarvis production deployment complete!"
        show_management_commands
    else
        log_error "Installation completed but service test failed"
        log_info "Please check the logs and configuration"
        exit 1
    fi
}

main "$@"