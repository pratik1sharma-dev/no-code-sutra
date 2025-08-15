import os
from typing import Optional

from psycopg_pool import AsyncConnectionPool
from psycopg.types.json import Json

# Connection string: set via env. Example for local:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nocodesutra
DATABASE_URL: str = os.getenv(
	"DATABASE_URL",
	"postgresql://postgres:postgres@localhost:5432/nocodesutra",
)

# Create a global async pool. Do not open yet (no running loop at import time).
pool: Optional[AsyncConnectionPool] = AsyncConnectionPool(
	DATABASE_URL,
	min_size=1,
	max_size=10,
	timeout=30,
	open=False,
)


async def init_db() -> None:
	"""Open pool and create required tables if they don't exist."""
	await pool.open()  # type: ignore[union-attr]
	create_workflows_sql = """
	CREATE TABLE IF NOT EXISTS workflows (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		description TEXT NOT NULL DEFAULT '',
		data JSONB NOT NULL,
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
	);
	"""

	create_executions_sql = """
	CREATE TABLE IF NOT EXISTS executions (
		id TEXT PRIMARY KEY,
		workflow_id TEXT NOT NULL,
		status TEXT NOT NULL DEFAULT 'running',
		result JSONB,
		nodes_executed INTEGER NOT NULL DEFAULT 0,
		started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		finished_at TIMESTAMPTZ
	);
	"""

	async with pool.connection() as conn:  # type: ignore[union-attr]
		async with conn.cursor() as cur:
			await cur.execute(create_workflows_sql)
			await cur.execute(create_executions_sql)
			await conn.commit()


async def close_db() -> None:
	"""Close the connection pool on shutdown."""
	if pool is not None:
		await pool.close()


async def save_workflow_row(
	*,
	workflow_id: str,
	name: str,
	description: str,
	data: dict,
) -> None:
	"""Upsert a workflow row."""
	upsert_sql = """
	INSERT INTO workflows (id, name, description, data)
	VALUES (%s, %s, %s, %s)
	ON CONFLICT (id) DO UPDATE SET
		name = EXCLUDED.name,
		description = EXCLUDED.description,
		data = EXCLUDED.data,
		updated_at = NOW();
	"""
	async with pool.connection() as conn:  # type: ignore[union-attr]
		async with conn.cursor() as cur:
			await cur.execute(
				upsert_sql,
				(workflow_id, name, description or "", Json(data)),
			)
			await conn.commit()


async def save_execution_row(
	*,
	execution_id: str,
	workflow_id: str,
	status: str,
	result: dict,
	nodes_executed: int,
	finished_at: Optional[str] = None,
) -> None:
	"""Upsert an execution row."""
	upsert_sql = """
	INSERT INTO executions (id, workflow_id, status, result, nodes_executed, finished_at)
	VALUES (%s, %s, %s, %s, %s, %s)
	ON CONFLICT (id) DO UPDATE SET
		workflow_id = EXCLUDED.workflow_id,
		status = EXCLUDED.status,
		result = EXCLUDED.result,
		nodes_executed = EXCLUDED.nodes_executed,
		finished_at = EXCLUDED.finished_at;
	"""
	async with pool.connection() as conn:  # type: ignore[union-attr]
		async with conn.cursor() as cur:
			await cur.execute(
				upsert_sql,
				(
					execution_id,
					workflow_id,
					status,
					Json(result) if result is not None else None,
					nodes_executed,
					finished_at,
				),
			)
			await conn.commit()