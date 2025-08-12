#!/usr/bin/env python3
"""
CPU Monitor Utility

Monitors CPU usage and identifies high CPU operations.
"""

import psutil
import time
import threading
from typing import Dict, List, Optional, Callable
from loguru import logger
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CPUProfile:
    """CPU profile for an operation."""
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    cpu_percent_start: float = 0.0
    cpu_percent_end: float = 0.0
    memory_start: float = 0.0
    memory_end: float = 0.0
    duration: Optional[float] = None
    
    def finish(self, cpu_percent: float, memory_mb: float):
        """Finish profiling."""
        self.end_time = datetime.now()
        self.cpu_percent_end = cpu_percent
        self.memory_end = memory_mb
        self.duration = (self.end_time - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, any]:
        """Get profiling summary."""
        return {
            'operation': self.operation_name,
            'duration_seconds': self.duration,
            'cpu_percent_start': self.cpu_percent_start,
            'cpu_percent_end': self.cpu_percent_end,
            'cpu_percent_avg': (self.cpu_percent_start + self.cpu_percent_end) / 2,
            'memory_start_mb': self.memory_start,
            'memory_end_mb': self.memory_end,
            'memory_delta_mb': self.memory_end - self.memory_start
        }


class CPUMonitor:
    """Monitor CPU usage and profile operations."""
    
    def __init__(self, log_interval: float = 5.0):
        self.log_interval = log_interval
        self.monitoring = False
        self.monitor_thread = None
        self.profiles: List[CPUProfile] = []
        self.current_profile: Optional[CPUProfile] = None
        
    def start_monitoring(self):
        """Start continuous CPU monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 CPU monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous CPU monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("🔍 CPU monitoring stopped")
    
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=1.0)
                memory_mb = psutil.virtual_memory().used / (1024 * 1024)
                
                if cpu_percent > 50:  # Log high CPU usage
                    logger.warning(f"🔥 High CPU usage detected: {cpu_percent:.1f}% | Memory: {memory_mb:.1f}MB")
                elif cpu_percent > 20:  # Log moderate CPU usage
                    logger.info(f"⚡ Moderate CPU usage: {cpu_percent:.1f}% | Memory: {memory_mb:.1f}MB")
                
                time.sleep(self.log_interval)
                
            except Exception as e:
                logger.error(f"CPU monitoring error: {e}")
                time.sleep(self.log_interval)
    
    def profile_operation(self, operation_name: str):
        """Profile decorator for operations."""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                self.start_profile(operation_name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.end_profile()
            return wrapper
        return decorator
    
    def start_profile(self, operation_name: str):
        """Start profiling an operation."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.virtual_memory().used / (1024 * 1024)
        
        self.current_profile = CPUProfile(
            operation_name=operation_name,
            start_time=datetime.now(),
            cpu_percent_start=cpu_percent,
            memory_start=memory_mb
        )
        
        logger.info(f"🔍 Starting profile: {operation_name} | CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.1f}MB")
    
    def end_profile(self):
        """End profiling current operation."""
        if not self.current_profile:
            return
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.virtual_memory().used / (1024 * 1024)
        
        self.current_profile.finish(cpu_percent, memory_mb)
        self.profiles.append(self.current_profile)
        
        summary = self.current_profile.get_summary()
        logger.info(f"🔍 Profile complete: {summary['operation']} | "
                   f"Duration: {summary['duration_seconds']:.2f}s | "
                   f"CPU: {summary['cpu_percent_avg']:.1f}% | "
                   f"Memory: {summary['memory_delta_mb']:+.1f}MB")
        
        self.current_profile = None
    
    def get_profiles_summary(self) -> Dict[str, any]:
        """Get summary of all profiles."""
        if not self.profiles:
            return {}
        
        total_duration = sum(p.duration or 0 for p in self.profiles)
        avg_cpu = sum(p.get_summary()['cpu_percent_avg'] for p in self.profiles) / len(self.profiles)
        total_memory_delta = sum(p.get_summary()['memory_delta_mb'] for p in self.profiles)
        
        return {
            'total_operations': len(self.profiles),
            'total_duration_seconds': total_duration,
            'average_cpu_percent': avg_cpu,
            'total_memory_delta_mb': total_memory_delta,
            'operations': [p.get_summary() for p in self.profiles]
        }
    
    def log_profiles_summary(self):
        """Log summary of all profiles."""
        summary = self.get_profiles_summary()
        if not summary:
            logger.info("🔍 No profiles recorded")
            return
        
        logger.info("🔍 CPU Profiles Summary:")
        logger.info(f"   Total operations: {summary['total_operations']}")
        logger.info(f"   Total duration: {summary['total_duration_seconds']:.2f}s")
        logger.info(f"   Average CPU: {summary['average_cpu_percent']:.1f}%")
        logger.info(f"   Total memory delta: {summary['total_memory_delta_mb']:+.1f}MB")
        
        # Log individual operations
        for op in summary['operations']:
            logger.info(f"   • {op['operation']}: {op['duration_seconds']:.2f}s | "
                       f"CPU: {op['cpu_percent_avg']:.1f}% | "
                       f"Memory: {op['memory_delta_mb']:+.1f}MB")


# Global CPU monitor instance
cpu_monitor = CPUMonitor()


def monitor_cpu_usage(func: Callable):
    """Decorator to monitor CPU usage for a function."""
    def wrapper(*args, **kwargs):
        cpu_monitor.start_profile(func.__name__)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            cpu_monitor.end_profile()
    
    # Preserve the original function signature
    import functools
    functools.update_wrapper(wrapper, func)
    return wrapper


def start_cpu_monitoring():
    """Start continuous CPU monitoring."""
    cpu_monitor.start_monitoring()


def stop_cpu_monitoring():
    """Stop continuous CPU monitoring."""
    cpu_monitor.stop_monitoring()


def log_cpu_summary():
    """Log CPU usage summary."""
    cpu_monitor.log_profiles_summary() 