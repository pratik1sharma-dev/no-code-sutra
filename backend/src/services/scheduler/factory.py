"""
Scheduler factory for creating appropriate scheduler instances
Provides configuration-based switching between scheduler backends
"""

import os
from typing import Optional

from services.scheduler.base import SchedulerInterface, SchedulerBackend
from services.scheduler.apscheduler_backend import APSchedulerBackend
from services.scheduler.celery_backend import CeleryBackend


class SchedulerConfig:
    """Configuration for scheduler factory"""
    
    def __init__(self):
        # Scheduler backend selection
        self.backend = SchedulerBackend(
            os.getenv('SCHEDULER_BACKEND', 'apscheduler')
        )
        
        # Database configuration
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
        
        # Celery configuration (for future use)
        self.celery_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        self.celery_result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
        
        # APScheduler configuration
        self.apscheduler_job_defaults = {
            'coalesce': bool(os.getenv('APSCHEDULER_COALESCE', 'True').lower() == 'true'),
            'max_instances': int(os.getenv('APSCHEDULER_MAX_INSTANCES', '1')),
            'misfire_grace_time': int(os.getenv('APSCHEDULER_MISFIRE_GRACE_TIME', '300'))
        }


class SchedulerFactory:
    """Factory for creating scheduler instances"""
    
    _instance: Optional[SchedulerInterface] = None
    _config: Optional[SchedulerConfig] = None
    
    @classmethod
    def create_scheduler(cls, config: Optional[SchedulerConfig] = None) -> SchedulerInterface:
        """Create a scheduler instance based on configuration"""
        if config is None:
            config = SchedulerConfig()
        
        cls._config = config
        
        if config.backend == SchedulerBackend.APSCHEDULER:
            return APSchedulerBackend(config.database_url)
        elif config.backend == SchedulerBackend.CELERY:
            return CeleryBackend(config.celery_broker_url, config.celery_result_backend)
        else:
            raise ValueError(f"Unsupported scheduler backend: {config.backend}")
    
    @classmethod
    def get_scheduler(cls) -> SchedulerInterface:
        """Get singleton scheduler instance"""
        if cls._instance is None:
            cls._instance = cls.create_scheduler()
        return cls._instance
    
    @classmethod
    async def initialize_scheduler(cls, config: Optional[SchedulerConfig] = None) -> SchedulerInterface:
        """Initialize and start the scheduler"""
        if cls._instance is None:
            cls._instance = cls.create_scheduler(config)
        
        await cls._instance.start()
        return cls._instance
    
    @classmethod
    async def shutdown_scheduler(cls) -> None:
        """Shutdown the scheduler"""
        if cls._instance is not None:
            await cls._instance.shutdown()
            cls._instance = None
    
    @classmethod
    def get_backend_info(cls) -> dict:
        """Get information about the current scheduler backend"""
        if cls._instance is None:
            return {"backend": "none", "status": "not_initialized"}
        
        return {
            "backend": cls._instance.backend_type.value,
            "is_distributed": cls._instance.is_distributed,
            "status": "running"
        }


# Convenience function for getting scheduler
def get_scheduler() -> SchedulerInterface:
    """Get the current scheduler instance"""
    return SchedulerFactory.get_scheduler()

