#!/bin/bash
# Pi-Jarvis Weekly Status Report Script
# Generates a comprehensive status report

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/pi-jarvis/status-report.log"
SERVICE_NAME="pi-jarvis.service"

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo chown raspberry:raspberry "$(dirname "$LOG_FILE")"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [STATUS] $1" | tee -a "$LOG_FILE"
}

generate_system_info() {
    log_message "=== SYSTEM INFORMATION ==="
    log_message "Hostname: $(hostname)"
    log_message "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    log_message "Kernel: $(uname -r)"
    log_message "Uptime: $(uptime -p)"
    log_message "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
    log_message ""
}

generate_service_status() {
    log_message "=== SERVICE STATUS ==="
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_message "✓ Service Status: ACTIVE"
        
        local start_time=$(systemctl show --property ActiveEnterTimestamp --value "$SERVICE_NAME")
        log_message "Start Time: $start_time"
        
        local pid=$(systemctl show --property MainPID --value "$SERVICE_NAME")
        log_message "Process ID: $pid"
        
        if [ "$pid" != "0" ]; then
            local memory_mb=$(ps -o rss= -p "$pid" 2>/dev/null | awk '{print int($1/1024)}' || echo "0")
            local cpu_percent=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ' || echo "0")
            
            log_message "Memory Usage: ${memory_mb}MB"
            log_message "CPU Usage: ${cpu_percent}%"
        fi
    else
        log_message "❌ Service Status: INACTIVE"
        local failed_time=$(systemctl show --property InactiveEnterTimestamp --value "$SERVICE_NAME")
        log_message "Failed Time: $failed_time"
    fi
    
    log_message ""
}

generate_resource_usage() {
    log_message "=== RESOURCE USAGE ==="
    
    # Disk usage
    local disk_info=$(df -h /home | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')
    log_message "Disk Usage: $disk_info"
    
    # Memory usage
    local mem_info=$(free -h | awk 'NR==2{printf "Memory: %s/%s (%.2f%% used)", $3,$2,$3*100/$2}')
    log_message "$mem_info"
    
    # Temperature (if available)
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        local temp_c=$(echo "scale=1; $temp/1000" | bc -l 2>/dev/null || echo "unknown")
        log_message "CPU Temperature: ${temp_c}°C"
    fi
    
    log_message ""
}

generate_log_analysis() {
    log_message "=== LOG ANALYSIS (Last 7 Days) ==="
    
    # Count different log levels
    local error_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "ERROR" --no-pager -q | wc -l)
    local warning_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "WARNING" --no-pager -q | wc -l)
    local info_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "INFO" --no-pager -q | wc -l)
    
    log_message "Errors: $error_count"
    log_message "Warnings: $warning_count"
    log_message "Info Messages: $info_count"
    
    # Show recent errors if any
    if [ "$error_count" -gt 0 ]; then
        log_message ""
        log_message "Recent Errors:"
        journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "ERROR" --no-pager -q | tail -5 | while read line; do
            log_message "  $line"
        done
    fi
    
    log_message ""
}

generate_performance_stats() {
    log_message "=== PERFORMANCE STATISTICS ==="
    
    # Service restart count
    local restart_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "Started\|Stopped" --no-pager -q | grep "Started" | wc -l)
    log_message "Service Restarts (7 days): $restart_count"
    
    # Check for performance issues
    local high_cpu_events=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "High CPU usage" --no-pager -q | wc -l)
    local high_mem_events=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "High memory usage" --no-pager -q | wc -l)
    
    log_message "High CPU Events: $high_cpu_events"
    log_message "High Memory Events: $high_mem_events"
    
    log_message ""
}

generate_intent_stats() {
    log_message "=== INTENT USAGE STATISTICS ==="
    
    # Look for intent classification logs
    local intent_logs=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "Intent classified" --no-pager -q | wc -l)
    
    if [ "$intent_logs" -gt 0 ]; then
        log_message "Total Intent Classifications: $intent_logs"
        
        # Count different intent types
        journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "Intent classified" --no-pager -q | \
        awk '{for(i=1;i<=NF;i++) if($i~/timer|weather|time|translation|vision|general_chat/) print $i}' | \
        sort | uniq -c | while read count intent; do
            log_message "  $intent: $count uses"
        done
    else
        log_message "No intent usage recorded"
    fi
    
    log_message ""
}

generate_recommendations() {
    log_message "=== RECOMMENDATIONS ==="
    
    local recommendations=0
    
    # Check disk space
    local disk_usage=$(df /home | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        log_message "⚠️  Disk space is ${disk_usage}% full - consider cleanup"
        recommendations=$((recommendations + 1))
    fi
    
    # Check service restarts
    local restart_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "Started" --no-pager -q | wc -l)
    if [ "$restart_count" -gt 10 ]; then
        log_message "⚠️  High restart count ($restart_count) - investigate stability issues"
        recommendations=$((recommendations + 1))
    fi
    
    # Check error rate
    local error_count=$(journalctl -u "$SERVICE_NAME" --since "7 days ago" --grep "ERROR" --no-pager -q | wc -l)
    if [ "$error_count" -gt 50 ]; then
        log_message "⚠️  High error count ($error_count) - check logs for issues"
        recommendations=$((recommendations + 1))
    fi
    
    if [ "$recommendations" -eq 0 ]; then
        log_message "✓ No issues detected - system running well"
    fi
    
    log_message ""
}

main() {
    log_message "=== PI-JARVIS WEEKLY STATUS REPORT ==="
    log_message "Report generated: $(date '+%Y-%m-%d %H:%M:%S')"
    log_message ""
    
    generate_system_info
    generate_service_status
    generate_resource_usage
    generate_log_analysis
    generate_performance_stats
    generate_intent_stats
    generate_recommendations
    
    log_message "=== END OF REPORT ==="
}

# Generate status report
main "$@"