import logging
import os
from sqlalchemy import Column, String, DateTime, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .db import engine, SessionLocal

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Run database migrations for workflow persistence enhancements
    """
    logger.info("Starting database migrations for workflow persistence")
    
    try:
        db = SessionLocal()
        connection = db.connection()
        
        # Check if user_id column exists in workflows table
        user_id_exists = connection.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='workflows' AND column_name='user_id'"
        )).fetchone()
        
        if not user_id_exists:
            logger.info("Adding user_id column to workflows table")
            connection.execute(text(
                "ALTER TABLE workflows ADD COLUMN user_id VARCHAR"
            ))
            connection.execute(text(
                "CREATE INDEX idx_workflow_user_id ON workflows (user_id)"
            ))
        
        # Check if is_public column exists in workflows table
        is_public_exists = connection.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='workflows' AND column_name='is_public'"
        )).fetchone()
        
        if not is_public_exists:
            logger.info("Adding is_public column to workflows table")
            connection.execute(text(
                "ALTER TABLE workflows ADD COLUMN is_public BOOLEAN DEFAULT FALSE"
            ))
            connection.execute(text(
                "CREATE INDEX idx_workflow_public ON workflows (is_public)"
            ))
        
        # Check if version column exists in workflows table
        version_exists = connection.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='workflows' AND column_name='version'"
        )).fetchone()
        
        if not version_exists:
            logger.info("Adding version column to workflows table")
            connection.execute(text(
                "ALTER TABLE workflows ADD COLUMN version INTEGER DEFAULT 1"
            ))
        
        # Check if parent_id column exists in workflows table
        parent_id_exists = connection.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='workflows' AND column_name='parent_id'"
        )).fetchone()
        
        if not parent_id_exists:
            logger.info("Adding parent_id column to workflows table")
            connection.execute(text(
                "ALTER TABLE workflows ADD COLUMN parent_id VARCHAR"
            ))
        
        # Create index on name for better search performance
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_workflow_name ON workflows (name)"
        ))
        
        # Ensure executions table has required columns and indexes
        exec_user_id_exists = connection.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='executions' AND column_name='user_id'"
        )).fetchone()
        
        if not exec_user_id_exists:
            logger.info("Adding user_id column to executions table and creating indexes")
            # Add missing user_id column
            connection.execute(text(
                "ALTER TABLE executions ADD COLUMN user_id VARCHAR"
            ))
            
            # Create helpful indexes (no-ops if they already exist)
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions (user_id)"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON executions (workflow_id)"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_executions_status ON executions (status)"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_executions_started_at ON executions (started_at)"
            ))
            # Composite indexes used by queries
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_execution_workflow_user ON executions (workflow_id, user_id)"
            ))
            connection.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_execution_status_time ON executions (status, started_at)"
            ))
        
        db.commit()
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running migrations: {e}", exc_info=True)
        raise
    finally:
        db.close()
