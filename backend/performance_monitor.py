#!/usr/bin/env python3
"""
Performance monitoring and optimization for Binarybrained AI Agent
"""

import time
import logging
import psutil
import os
from functools import wraps
from collections import defaultdict

# Performance metrics storage
performance_metrics = {
    'request_times': defaultdict(list),
    'memory_usage': [],
    'cpu_usage': [],
    'db_query_times': [],
    'cache_hits': 0,
    'cache_misses': 0
}

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations
            if execution_time > 1.0:  # Log operations taking more than 1 second
                logging.warning(f"Slow operation detected: {func.__name__} took {execution_time:.2f}s")
            
            # Store metrics
            performance_metrics['request_times'][func.__name__].append(execution_time)
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Error in {func.__name__} after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper

def log_system_metrics():
    """Log current system metrics"""
    try:
        # CPU and Memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        performance_metrics['cpu_usage'].append(cpu_percent)
        performance_metrics['memory_usage'].append(memory.percent)
        
        # Keep only last 100 entries
        if len(performance_metrics['cpu_usage']) > 100:
            performance_metrics['cpu_usage'] = performance_metrics['cpu_usage'][-100:]
            performance_metrics['memory_usage'] = performance_metrics['memory_usage'][-100:]
        
        # Log if high usage
        if cpu_percent > 80:
            logging.warning(f"High CPU usage detected: {cpu_percent}%")
        if memory.percent > 80:
            logging.warning(f"High memory usage detected: {memory.percent}%")
            
    except Exception as e:
        logging.error(f"Error logging system metrics: {e}")

def get_performance_report():
    """Generate performance report"""
    report = {
        'system': {
            'avg_cpu': sum(performance_metrics['cpu_usage']) / len(performance_metrics['cpu_usage']) if performance_metrics['cpu_usage'] else 0,
            'avg_memory': sum(performance_metrics['memory_usage']) / len(performance_metrics['memory_usage']) if performance_metrics['memory_usage'] else 0,
        },
        'cache': {
            'hit_rate': performance_metrics['cache_hits'] / (performance_metrics['cache_hits'] + performance_metrics['cache_misses']) if (performance_metrics['cache_hits'] + performance_metrics['cache_misses']) > 0 else 0,
            'total_hits': performance_metrics['cache_hits'],
            'total_misses': performance_metrics['cache_misses']
        },
        'functions': {}
    }
    
    # Function performance
    for func_name, times in performance_metrics['request_times'].items():
        if times:
            report['functions'][func_name] = {
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'total_calls': len(times)
            }
    
    return report

def record_cache_hit():
    """Record a cache hit"""
    performance_metrics['cache_hits'] += 1

def record_cache_miss():
    """Record a cache miss"""
    performance_metrics['cache_misses'] += 1

def optimize_system():
    """Apply system optimizations"""
    try:
        # Set environment variables for better performance
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['PYTHON_GC_GENERATION'] = '700,10,10'  # Optimize garbage collection
        
        # Log optimization
        logging.info("System optimizations applied")
        
    except Exception as e:
        logging.error(f"Error applying optimizations: {e}")

# Initialize performance monitoring
if __name__ == "__main__":
    optimize_system()
    log_system_metrics()
    print("Performance monitoring initialized")