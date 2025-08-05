#!/bin/bash
# Pi-Jarvis Health Check Script
# Monitors the health of the Pi-Jarvis service and restarts if necessary

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/pi-jarvis/health-check.log"
SERVICE_NAME="pi-jarvis.service"
MAX_MEMORY_MB=1024  # Maximum memory usage in MB
MAX_CPU_PERCENT=90  # Maximum CPU usage percentage

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo chown raspberry:raspberry "$(dirname "$LOG_FILE")"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [HEALTH] $1" | tee -a "$LOG_FILE"
}

check_service_status() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        return 0  # Service is active
    else
        return 1  # Service is not active
    fi
}

get_service_pid() {
    systemctl show --property MainPID --value "$SERVICE_NAME" 2>/dev/null || echo "0"
}

check_memory_usage() {
    local pid="$1"
    if [ "$pid" = "0" ]; then
        return 1
    fi
    
    # Get memory usage in KB, convert to MB
    local memory_kb=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ' || echo "0")
    local memory_mb=$((memory_kb / 1024))
    
    if [ "$memory_mb" -gt "$MAX_MEMORY_MB" ]; then
        log_message "WARNING: High memory usage: ${memory_mb}MB (limit: ${MAX_MEMORY_MB}MB)"
        return 1
    fi
    
    return 0
}

check_cpu_usage() {
    local pid="$1"
    if [ "$pid" = "0" ]; then
        return 1
    fi
    
    # Get CPU usage percentage (average over 2 seconds)
    local cpu_percent=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ' || echo "0")
    local cpu_int=${cpu_percent%.*}  # Remove decimal part
    
    if [ "${cpu_int:-0}" -gt "$MAX_CPU_PERCENT" ]; then
        log_message "WARNING: High CPU usage: ${cpu_percent}% (limit: ${MAX_CPU_PERCENT}%)"
        return 1
    fi
    
    return 0
}

check_log_errors() {
    local recent_errors=$(journalctl -u "$SERVICE_NAME" --since "5 minutes ago" --grep "ERROR|CRITICAL|FATAL" --no-pager -q | wc -l)
    
    if [ "$recent_errors" -gt 5 ]; then
        log_message "WARNING: High error rate: $recent_errors errors in last 5 minutes"
        return 1
    fi
    
    return 0
}

restart_service() {
    log_message "Restarting $SERVICE_NAME due to health check failure"
    if sudo systemctl restart "$SERVICE_NAME"; then
        log_message "Service restarted successfully"
        sleep 10  # Wait for service to stabilize
        return 0
    else
        log_message "ERROR: Failed to restart service"
        return 1
    fi
}

main() {
    log_message "Starting health check"
    
    local health_issues=0
    
    # Check if service is running
    if ! check_service_status; then
        log_message "ERROR: Service is not active"
        health_issues=$((health_issues + 1))
    else
        log_message "✓ Service is active"
        
        # Get service PID for resource checks
        local pid=$(get_service_pid)
        log_message "Service PID: $pid"
        
        # Check memory usage
        if ! check_memory_usage "$pid"; then
            health_issues=$((health_issues + 1))
        else
            log_message "✓ Memory usage normal"
        fi
        
        # Check CPU usage
        if ! check_cpu_usage "$pid"; then
            health_issues=$((health_issues + 1))
        else
            log_message "✓ CPU usage normal"
        fi
    fi
    
    # Check for recent errors in logs
    if ! check_log_errors; then
        health_issues=$((health_issues + 1))
    else
        log_message "✓ Error rate normal"
    fi
    
    # Restart service if there are health issues
    if [ "$health_issues" -gt 1 ]; then
        log_message "Multiple health issues detected ($health_issues), restarting service"
        restart_service
    elif [ "$health_issues" -eq 1 ]; then
        log_message "One health issue detected, monitoring closely"
    else
        log_message "✓ All health checks passed"
    fi
    
    log_message "Health check completed"
}

# Run health check
main "$@"