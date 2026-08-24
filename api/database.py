from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import command
from api.models.feedback import Base

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_CONFIG_PATH = PROJECT_ROOT / "alembic.ini"


def _upgrade_database(connection: Connection, alembic_config: Config) -> None:
    alembic_config.attributes["connection"] = connection

    table_names = set(inspect(connection).get_table_names())
    schema_tables = set(Base.metadata.tables)
    if schema_tables.issubset(table_names) and "alembic_version" not in table_names:
        command.stamp(alembic_config, "head")
        return

    command.upgrade(alembic_config, "head")


def create_database_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


async def upgrade_database(database_engine: AsyncEngine) -> None:
    alembic_config = Config(str(ALEMBIC_CONFIG_PATH))

    async with database_engine.begin() as connection:
        await connection.run_sync(_upgrade_database, alembic_config)
