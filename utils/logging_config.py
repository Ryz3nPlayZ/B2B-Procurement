"""
Logging Configuration

Structured logging setup for the ASI system.
"""

import logging
import logging.handlers
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import json


class ASIFormatter(logging.Formatter):
    """Custom formatter for ASI system logs."""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        
        # Create format string
        format_parts = []
        if include_timestamp:
            format_parts.append('%(asctime)s')
        if include_level:
            format_parts.append('%(levelname)s')
        format_parts.extend(['%(name)s', '%(message)s'])
        
        super().__init__(fmt=' | '.join(format_parts), datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        # Add custom fields
        record.asi_timestamp = datetime.utcnow().isoformat()
        record.asi_level = record.levelname
        record.asi_logger = record.name
        
        # Format the message
        formatted = super().format(record)
        
        # Add structured data if available
        if hasattr(record, 'asi_data') and record.asi_data:
            data_str = json.dumps(record.asi_data, default=str)
            formatted += f" | DATA: {data_str}"
        
        return formatted


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add custom fields
        if hasattr(record, 'asi_data') and record.asi_data:
            log_entry['data'] = record.asi_data
        
        if hasattr(record, 'asi_context') and record.asi_context:
            log_entry['context'] = record.asi_context
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str)


class ASILogger:
    """ASI system logger with structured logging capabilities."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        
        # Configure logger
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        # Set log level
        level = self.config.get('level', 'INFO')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add console handler
        if self.config.get('console', True):
            self._add_console_handler()
        
        # Add file handler
        if self.config.get('file', True):
            self._add_file_handler()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _add_console_handler(self):
        """Add console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use JSON formatter for console if configured
        if self.config.get('json_console', False):
            formatter = JSONFormatter()
        else:
            formatter = ASIFormatter()
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add file handler with rotation."""
        log_file = self.config.get('log_file', 'logs/asi.log')
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create rotating file handler
        max_bytes = self.config.get('max_log_size', 10 * 1024 * 1024)  # 10MB
        backup_count = self.config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        file_handler.setLevel(logging.DEBUG)
        
        # Use JSON formatter for file logs
        formatter = JSONFormatter()
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_with_context(self, level: str, message: str, context: Dict[str, Any] = None, 
                        data: Dict[str, Any] = None):
        """Log message with additional context and data."""
        log_method = getattr(self.logger, level.lower())
        
        # Create log record with extra fields
        extra = {}
        if context:
            extra['asi_context'] = context
        if data:
            extra['asi_data'] = data
        
        log_method(message, extra=extra)
    
    def info(self, message: str, context: Dict[str, Any] = None, data: Dict[str, Any] = None):
        """Log info message with context."""
        self.log_with_context('info', message, context, data)
    
    def warning(self, message: str, context: Dict[str, Any] = None, data: Dict[str, Any] = None):
        """Log warning message with context."""
        self.log_with_context('warning', message, context, data)
    
    def error(self, message: str, context: Dict[str, Any] = None, data: Dict[str, Any] = None):
        """Log error message with context."""
        self.log_with_context('error', message, context, data)
    
    def debug(self, message: str, context: Dict[str, Any] = None, data: Dict[str, Any] = None):
        """Log debug message with context."""
        self.log_with_context('debug', message, context, data)
    
    def critical(self, message: str, context: Dict[str, Any] = None, data: Dict[str, Any] = None):
        """Log critical message with context."""
        self.log_with_context('critical', message, context, data)


class LoggingConfig:
    """Logging configuration manager for ASI system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.loggers = {}
        
        # Setup root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger configuration."""
        # Set root logger level
        level = self.config.get('level', 'INFO')
        logging.getLogger().setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Add console handler for root
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        formatter = ASIFormatter()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str, config: Dict[str, Any] = None) -> ASILogger:
        """Get or create logger with configuration."""
        if name not in self.loggers:
            logger_config = self.config.copy()
            if config:
                logger_config.update(config)
            
            self.loggers[name] = ASILogger(name, logger_config)
        
        return self.loggers[name]
    
    def setup_agent_logger(self, agent_id: str, agent_type: str) -> ASILogger:
        """Setup logger for agent with specific configuration."""
        config = {
            'level': self.config.get('level', 'INFO'),
            'console': True,
            'file': True,
            'log_file': f'logs/agents/{agent_type}_{agent_id}.log',
            'json_console': self.config.get('json_console', False),
            'json_file': True
        }
        
        return self.get_logger(f'agent.{agent_id}', config)
    
    def setup_system_logger(self, component: str) -> ASILogger:
        """Setup logger for system component."""
        config = {
            'level': self.config.get('level', 'INFO'),
            'console': True,
            'file': True,
            'log_file': f'logs/system/{component}.log',
            'json_console': self.config.get('json_console', False),
            'json_file': True
        }
        
        return self.get_logger(f'system.{component}', config)
    
    def setup_negotiation_logger(self, deal_id: str) -> ASILogger:
        """Setup logger for negotiation process."""
        config = {
            'level': 'DEBUG',
            'console': False,
            'file': True,
            'log_file': f'logs/negotiations/{deal_id}.log',
            'json_console': False,
            'json_file': True
        }
        
        return self.get_logger(f'negotiation.{deal_id}', config)
    
    def get_all_loggers(self) -> Dict[str, ASILogger]:
        """Get all configured loggers."""
        return self.loggers.copy()
    
    def set_log_level(self, level: str):
        """Set log level for all loggers."""
        for logger in self.loggers.values():
            logger.logger.setLevel(getattr(logging, level.upper()))
    
    def enable_debug(self):
        """Enable debug logging for all loggers."""
        self.set_log_level('DEBUG')
    
    def disable_debug(self):
        """Disable debug logging for all loggers."""
        self.set_log_level('INFO')


def setup_logging(config: Dict[str, Any] = None) -> LoggingConfig:
    """Setup logging configuration for ASI system."""
    default_config = {
        'level': 'INFO',
        'console': True,
        'file': True,
        'log_file': 'logs/asi.log',
        'max_log_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'json_console': False,
        'json_file': True
    }
    
    if config:
        default_config.update(config)
    
    return LoggingConfig(default_config)


def get_logger(name: str, config: Dict[str, Any] = None) -> ASILogger:
    """Get logger instance."""
    logging_config = setup_logging(config)
    return logging_config.get_logger(name)

