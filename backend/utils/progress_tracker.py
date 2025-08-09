#!/usr/bin/env python3
"""
📊 Progress Tracker Module

Provides consistent progress tracking, timing, and ETA calculations
for data processing operations throughout the app.

Features:
- Real-time progress indicators
- ETA calculations
- Consistent logging format
- Memory usage tracking
- Performance benchmarking
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger
import sys


@dataclass
class ProcessingStep:
    """Represents a single processing step with timing and metadata."""
    name: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    records_processed: int = 0
    total_records: int = 0
    memory_usage_mb: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    
    def start(self, total_records: int = 0):
        """Start timing this step."""
        self.start_time = time.time()
        self.total_records = total_records
        self.status = "running"
        self.memory_usage_mb = self._get_memory_usage()
        
    def end(self, records_processed: int = 0):
        """End timing this step."""
        if self.start_time:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time
            self.records_processed = records_processed
            self.status = "completed"
            self.memory_usage_mb = self._get_memory_usage()
    
    def fail(self, error_message: str):
        """Mark step as failed."""
        if self.start_time:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time
        self.status = "failed"
        self.error_message = error_message
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.total_records == 0:
            return 0.0
        return (self.records_processed / self.total_records) * 100
    
    @property
    def records_per_second(self) -> float:
        """Get processing speed in records per second."""
        if not self.duration or self.duration == 0:
            return 0.0
        return self.records_processed / self.duration


class ProgressTracker:
    """
    Main progress tracking class for data processing operations.
    
    Provides consistent timing, progress indicators, and logging
    for multi-step data processing workflows.
    """
    
    def __init__(self, operation_name: str = "Data Processing"):
        self.operation_name = operation_name
        self.steps: List[ProcessingStep] = []
        self.current_step: Optional[ProcessingStep] = None
        self.start_time = None
        self.end_time = None
        self.total_duration = None
        self.callback: Optional[Callable] = None
        self._lock = threading.Lock()
        
    def add_step(self, step_name: str) -> ProcessingStep:
        """Add a new processing step."""
        step = ProcessingStep(name=step_name)
        self.steps.append(step)
        return step
    
    def start_operation(self, total_records: int = 0):
        """Start the overall operation."""
        self.start_time = time.time()
        logger.info(f"🚀 Starting {self.operation_name}")
        logger.info(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        if total_records > 0:
            logger.info(f"📊 Total records to process: {total_records:,}")
        
        # Estimate total time based on historical data
        estimated_time = self._estimate_total_time(total_records)
        if estimated_time > 0:
            logger.info(f"⏱️  Estimated total time: {estimated_time:.1f}s")
    
    def start_step(self, step_name: str, total_records: int = 0):
        """Start a processing step."""
        with self._lock:
            # End previous step if running
            if self.current_step and self.current_step.status == "running":
                self.current_step.end()
            
            # Find or create step
            step = next((s for s in self.steps if s.name == step_name), None)
            if not step:
                step = self.add_step(step_name)
            
            self.current_step = step
            step.start(total_records)
            
            logger.info(f"🔄 {step_name}")
            logger.info(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
            
            if total_records > 0:
                logger.info(f"📊 Processing {total_records:,} records")
    
    def update_progress(self, records_processed: int, step_name: Optional[str] = None):
        """Update progress for current or specified step."""
        with self._lock:
            step = self.current_step
            if step_name:
                step = next((s for s in self.steps if s.name == step_name), None)
            
            if step and step.status == "running":
                step.records_processed = records_processed
                
                # Calculate progress
                if step.total_records > 0:
                    progress = (records_processed / step.total_records) * 100
                    eta = self._calculate_eta(step)
                    
                    # Log progress every 10% or every 1000 records
                    if (progress % 10 < 1 and progress > 0) or records_processed % 1000 == 0:
                        logger.info(f"📈 {step.name}: {progress:.1f}% ({records_processed:,}/{step.total_records:,})")
                        if eta:
                            logger.info(f"⏱️  ETA: {eta}")
                
                # Call callback if provided
                if self.callback:
                    self.callback(step)
    
    def end_step(self, records_processed: int = 0):
        """End the current processing step."""
        with self._lock:
            if self.current_step and self.current_step.status == "running":
                self.current_step.end(records_processed)
                
                duration = self.current_step.duration
                speed = self.current_step.records_per_second
                memory = self.current_step.memory_usage_mb
                
                logger.info(f"✅ {self.current_step.name} completed")
                logger.info(f"⏱️  Duration: {duration:.2f}s")
                if speed > 0:
                    logger.info(f"🚀 Speed: {speed:.0f} records/sec")
                logger.info(f"💾 Memory: {memory:.1f} MB")
                
                # Update total progress
                total_processed = sum(s.records_processed for s in self.steps if s.status == "completed")
                total_duration = time.time() - self.start_time if self.start_time else 0
                if total_duration > 0:
                    overall_speed = total_processed / total_duration
                    logger.info(f"📊 Overall: {total_processed:,} records in {total_duration:.2f}s ({overall_speed:.0f} records/sec)")
    
    def fail_step(self, error_message: str):
        """Mark current step as failed."""
        with self._lock:
            if self.current_step:
                self.current_step.fail(error_message)
                logger.error(f"❌ {self.current_step.name} failed: {error_message}")
    
    def end_operation(self):
        """End the overall operation."""
        with self._lock:
            # End current step if running
            if self.current_step and self.current_step.status == "running":
                self.current_step.end()
            
            self.end_time = time.time()
            if self.start_time:
                self.total_duration = self.end_time - self.start_time
            
            # Generate final report
            self._generate_final_report()
    
    def set_callback(self, callback: Callable[[ProcessingStep], None]):
        """Set a callback function for progress updates."""
        self.callback = callback
    
    def _calculate_eta(self, step: ProcessingStep) -> Optional[str]:
        """Calculate estimated time to completion for a step."""
        if step.total_records == 0 or step.records_processed == 0:
            return None
        
        if step.records_per_second <= 0:
            return None
        
        remaining_records = step.total_records - step.records_processed
        eta_seconds = remaining_records / step.records_per_second
        
        if eta_seconds < 60:
            return f"{eta_seconds:.0f}s"
        elif eta_seconds < 3600:
            minutes = eta_seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = eta_seconds / 3600
            return f"{hours:.1f}h"
    
    def _estimate_total_time(self, total_records: int) -> float:
        """Estimate total processing time based on historical data."""
        # This could be enhanced with actual historical data
        # For now, use conservative estimates
        if total_records == 0:
            return 0.0
        
        # Rough estimates based on typical processing speeds
        records_per_second = 1000  # Conservative estimate
        return total_records / records_per_second
    
    def _generate_final_report(self):
        """Generate final processing report."""
        logger.info(f"🎉 {self.operation_name} completed!")
        logger.info(f"⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
        
        if self.total_duration:
            logger.info(f"⏱️  Total duration: {self.total_duration:.2f}s")
        
        # Step summary
        completed_steps = [s for s in self.steps if s.status == "completed"]
        failed_steps = [s for s in self.steps if s.status == "failed"]
        
        if completed_steps:
            logger.info(f"✅ Completed steps: {len(completed_steps)}")
            for step in completed_steps:
                logger.info(f"   • {step.name}: {step.duration:.2f}s")
        
        if failed_steps:
            logger.error(f"❌ Failed steps: {len(failed_steps)}")
            for step in failed_steps:
                logger.error(f"   • {step.name}: {step.error_message}")
        
        # Performance summary
        total_records = sum(s.records_processed for s in completed_steps)
        if total_records > 0 and self.total_duration:
            overall_speed = total_records / self.total_duration
            logger.info(f"📊 Performance: {total_records:,} records in {self.total_duration:.2f}s ({overall_speed:.0f} records/sec)")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary as dictionary."""
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "duration": step.duration,
                    "records_processed": step.records_processed,
                    "total_records": step.total_records,
                    "memory_usage_mb": step.memory_usage_mb,
                    "error_message": step.error_message
                }
                for step in self.steps
            ]
        }


class DataProcessingProgress:
    """
    Specialized progress tracker for data processing operations.
    
    Provides common patterns for data loading, cleaning, transformation,
    and export operations.
    """
    
    def __init__(self, operation_name: str = "Data Processing"):
        self.tracker = ProgressTracker(operation_name)
        self.total_records = 0
    
    def start_data_processing(self, total_records: int):
        """Start data processing operation."""
        self.total_records = total_records
        self.tracker.start_operation(total_records)
    
    def start_loading(self, filepath: str):
        """Start data loading step."""
        self.tracker.start_step("Loading Data", self.total_records)
        logger.info(f"📁 Loading: {filepath}")
    
    def start_cleaning(self):
        """Start data cleaning step."""
        self.tracker.start_step("Cleaning Data", self.total_records)
    
    def start_transformation(self):
        """Start data transformation step."""
        self.tracker.start_step("Transforming Data", self.total_records)
    
    def start_prioritization(self):
        """Start phone prioritization step."""
        self.tracker.start_step("Prioritizing Phones", self.total_records)
    
    def start_export(self):
        """Start data export step."""
        self.tracker.start_step("Exporting Data", self.total_records)
    
    def update_progress(self, records_processed: int):
        """Update progress for current step."""
        self.tracker.update_progress(records_processed)
    
    def end_current_step(self, records_processed: int = 0):
        """End current step."""
        self.tracker.end_step(records_processed)
    
    def fail_current_step(self, error_message: str):
        """Fail current step."""
        self.tracker.fail_step(error_message)
    
    def complete_processing(self):
        """Complete the data processing operation."""
        self.tracker.end_operation()
    
    def set_callback(self, callback: Callable):
        """Set progress callback."""
        self.tracker.set_callback(callback)


# Convenience functions for common operations
def track_data_loading(filepath: str, total_records: int = 0) -> DataProcessingProgress:
    """Create a progress tracker for data loading operations."""
    progress = DataProcessingProgress("Data Loading")
    progress.start_data_processing(total_records)
    progress.start_loading(filepath)
    return progress


def track_data_processing(operation_name: str, total_records: int = 0) -> DataProcessingProgress:
    """Create a progress tracker for general data processing."""
    progress = DataProcessingProgress(operation_name)
    progress.start_data_processing(total_records)
    return progress


def track_phone_prioritization(total_records: int = 0) -> DataProcessingProgress:
    """Create a progress tracker for phone prioritization."""
    progress = DataProcessingProgress("Phone Prioritization")
    progress.start_data_processing(total_records)
    progress.start_prioritization()
    return progress


def track_smart_seller_creation(total_records: int = 0) -> DataProcessingProgress:
    """Create a progress tracker for smart seller creation."""
    progress = DataProcessingProgress("Smart Seller Creation")
    progress.start_data_processing(total_records)
    progress.start_transformation()
    return progress


# Example usage:
if __name__ == "__main__":
    # Example of how to use the progress tracker
    progress = track_data_processing("Example Processing", 10000)
    
    # Simulate processing steps
    progress.start_loading("example.csv")
    time.sleep(1)  # Simulate work
    progress.update_progress(5000)
    time.sleep(1)
    progress.end_current_step(10000)
    
    progress.start_cleaning()
    time.sleep(0.5)
    progress.end_current_step(10000)
    
    progress.complete_processing() 