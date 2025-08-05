#!/bin/bash
# Pi-Jarvis Daily Maintenance Script
# Performs routine maintenance tasks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/pi-jarvis/maintenance.log"
SERVICE_NAME="pi-jarvis.service"

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo chown raspberry:raspberry "$(dirname "$LOG_FILE")"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [MAINTENANCE] $1" | tee -a "$LOG_FILE"
}

cleanup_old_logs() {
    log_message "Cleaning up old log files..."
    
    # Remove logs older than 30 days from project logs directory
    find "$PROJECT_DIR/logs" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Clean up old journal entries (keep last 2 weeks)
    sudo journalctl --vacuum-time=2weeks >/dev/null 2>&1 || true
    
    log_message "Log cleanup completed"
}

check_disk_space() {
    log_message "Checking disk space..."
    
    local disk_usage=$(df /home | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 80 ]; then
        log_message "WARNING: Disk usage high: ${disk_usage}%"
        
        # Try to free up space
        sudo apt-get autoremove -y >/dev/null 2>&1 || true
        sudo apt-get autoclean >/dev/null 2>&1 || true
        
        log_message "Disk cleanup attempted"
    else
        log_message "✓ Disk space OK: ${disk_usage}% used"
    fi
}

update_models() {
    log_message "Checking for model updates..."
    
    cd "$PROJECT_DIR"
    
    # Check if models directory exists and has reasonable size
    if [ -d "models" ]; then
        local models_size=$(du -sm models/ 2>/dev/null | cut -f1 || echo "0")
        if [ "$models_size" -lt 100 ]; then
            log_message "WARNING: Models directory seems incomplete (${models_size}MB)"
        else
            log_message "✓ Models directory OK (${models_size}MB)"
        fi
    else
        log_message "WARNING: Models directory missing"
    fi
}

restart_if_needed() {
    log_message "Checking if service restart is needed..."
    
    # Check if service has been running for more than 7 days
    local start_time=$(systemctl show --property ActiveEnterTimestamp --value "$SERVICE_NAME" 2>/dev/null || echo "")
    
    if [ -n "$start_time" ]; then
        local start_epoch=$(date -d "$start_time" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local uptime_days=$(( (current_epoch - start_epoch) / 86400 ))
        
        if [ "$uptime_days" -gt 7 ]; then
            log_message "Service has been running for $uptime_days days, restarting for maintenance"
            sudo systemctl restart "$SERVICE_NAME"
            sleep 10
            log_message "Maintenance restart completed"
        else
            log_message "✓ Service uptime OK ($uptime_days days)"
        fi
    fi
}

check_memory_leaks() {
    log_message "Checking for memory leaks..."
    
    local pid=$(systemctl show --property MainPID --value "$SERVICE_NAME" 2>/dev/null || echo "0")
    
    if [ "$pid" != "0" ]; then
        local memory_mb=$(ps -o rss= -p "$pid" 2>/dev/null | awk '{print int($1/1024)}' || echo "0")
        
        if [ "$memory_mb" -gt 800 ]; then
            log_message "WARNING: High memory usage detected: ${memory_mb}MB"
        else
            log_message "✓ Memory usage normal: ${memory_mb}MB"
        fi
    fi
}

main() {
    log_message "Starting daily maintenance"
    
    cleanup_old_logs
    check_disk_space
    update_models
    check_memory_leaks
    restart_if_needed
    
    log_message "Daily maintenance completed"
}

# Run maintenance
main "$@"