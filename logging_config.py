"""
Logging configuration for the application
"""
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Configure application logging
    
    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to save logs to file (default: True)
        
    Returns:
        Logger: Configured root logger
    """
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"aggregator_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates when reloading
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    root_logger.addHandler(console_handler)
    
    # Add file handler if logging to file
    if log_to_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create specific logger for the application
    logger = logging.getLogger("aggregator")
    
    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    logger.info(f"Logging has been set up with log level {logging.getLevelName(log_level)}")
    if log_to_file:
        logger.info(f"Logs are being saved to {log_file}")
        
    return logger