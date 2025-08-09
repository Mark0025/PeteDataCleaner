#!/usr/bin/env python3
"""
Process Monitor - Track CPU usage and process status
"""

import psutil
import time
import os
import sys
from datetime import datetime
import subprocess
import threading
from pathlib import Path

class ProcessMonitor:
    def __init__(self, process_name="python", log_file="process_monitor.log"):
        self.process_name = process_name
        self.log_file = log_file
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start monitoring in a separate thread."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"🔍 Started monitoring processes containing '{self.process_name}'")
        
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("🛑 Stopped monitoring")
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._log_process_status()
                time.sleep(2)  # Check every 2 seconds
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                
    def _log_process_status(self):
        """Log current process status."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Find processes containing the process name
        target_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if self.process_name.lower() in proc.info['name'].lower():
                    target_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if target_processes:
            log_entry = f"[{timestamp}] Found {len(target_processes)} processes:\n"
            total_cpu = 0
            total_memory = 0
            
            for proc in target_processes:
                cpu = proc.get('cpu_percent', 0)
                memory = proc.get('memory_percent', 0)
                cmdline = ' '.join(proc.get('cmdline', [])[:3])  # First 3 args
                
                log_entry += f"  PID {proc['pid']}: {proc['name']} - CPU: {cpu:.1f}% | Memory: {memory:.1f}% | CMD: {cmdline}\n"
                total_cpu += cpu
                total_memory += memory
                
            log_entry += f"  Total CPU: {total_cpu:.1f}% | Total Memory: {total_memory:.1f}%\n"
            log_entry += "-" * 80 + "\n"
            
            # Write to log file
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
                
            # Also print to console
            print(log_entry.strip())
        else:
            print(f"[{timestamp}] No processes found containing '{self.process_name}'")
            
    def get_current_status(self):
        """Get current status without logging."""
        target_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if self.process_name.lower() in proc.info['name'].lower():
                    target_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return target_processes


def monitor_test_process():
    """Monitor the test process specifically."""
    print("🔍 Starting process monitor...")
    print("Press Ctrl+C to stop monitoring")
    print("-" * 80)
    
    monitor = ProcessMonitor(process_name="test_end_to_end_pipeline", log_file="test_monitor.log")
    
    try:
        monitor.start_monitoring()
        
        # Keep monitoring until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor stopped")


def quick_status_check():
    """Quick status check of current processes."""
    print("🔍 Quick Status Check")
    print("=" * 50)
    
    monitor = ProcessMonitor(process_name="python")
    processes = monitor.get_current_status()
    
    if processes:
        print(f"Found {len(processes)} Python processes:")
        for proc in processes:
            cpu = proc.get('cpu_percent', 0)
            memory = proc.get('memory_percent', 0)
            cmdline = ' '.join(proc.get('cmdline', [])[:3])
            print(f"  PID {proc['pid']}: CPU {cpu:.1f}% | Memory {memory:.1f}% | {cmdline}")
    else:
        print("No Python processes found")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            monitor_test_process()
        elif sys.argv[1] == "status":
            quick_status_check()
        else:
            print("Usage: python monitor_process.py [monitor|status]")
    else:
        quick_status_check() 