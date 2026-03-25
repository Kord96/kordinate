"""
PostgreSQL database connection and schema validation.

Provides:
- Database URL parsing and connection
- Session factory (get_db context manager)
- Schema validation (compare models to actual DB)

Usage:
    from infra_client import get_db, validate_schema

    with get_db() as db:
        users = db.query(User).all()

    # Fail fast if schema doesn't match models
    validate_schema([
        (User, "public", "users"),
    ])
"""

import os
import re
from contextlib import contextmanager
from typing import Any, Dict, List

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

# =============================================================================
# Exceptions
# =============================================================================


class SchemaValidationError(Exception):
    """Raised when database schema doesn't match models."""

    pass


# =============================================================================
# Configuration
# =============================================================================

_database_url: str | None = None


def configure_database(url: str) -> None:
    """
    Configure the database URL programmatically.

    Call this before any database operations. Preferred over setting
    DATABASE_URL environment variable.

    Args:
        url: PostgreSQL connection URL (e.g., postgresql://user@host:5432/dbname)
    """
    global _database_url, _engine, _SessionLocal
    _database_url = url
    # Reset engine/session so next get_db() uses the new URL
    _engine = None
    _SessionLocal = None


def _require_database_url() -> str:
    """Get database URL from configuration or environment."""
    if _database_url:
        return _database_url
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "Database not configured. Call configure_database(url) or "
            "set DATABASE_URL environment variable."
        )
    return url


# =============================================================================
# URL Parsing
# =============================================================================


def parse_database_url(url: str) -> Dict[str, str]:
    """Parse DATABASE_URL into components."""
    # Support both user:password@host and user@host (no password)
    pattern = r"postgresql://([^:@]+)(?::([^@]*))?@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid DATABASE_URL format: {url}")
    return {
        "user": match.group(1),
        "password": match.group(2) or "",
        "host": match.group(3),
        "port": match.group(4),
        "database": match.group(5),
    }


# =============================================================================
# Database Creation
# =============================================================================


def ensure_database(url: str = None) -> bool:
    """
    Ensure the target database exists, creating it if necessary.

    Returns:
        True if database was created, False if it already existed

    Note: When connecting through PgBouncer (port 6432), this check is
    skipped since PgBouncer typically proxies specific databases and
    the postgres admin database may not be accessible.
    """
    url = url or DATABASE_URL
    parts = parse_database_url(url)
    db_name = parts["database"]

    # Skip database creation check when using PgBouncer (port 6432)
    # PgBouncer proxies specific databases; assume database exists
    if parts["port"] == "6432":
        return False

    # Connect to postgres database to check/create target db
    postgres_url = url.rsplit("/", 1)[0] + "/postgres"

    engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db"), {"db": db_name}
        )
        exists = result.fetchone() is not None

        if not exists:
            # Create database
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            engine.dispose()
            return True

    engine.dispose()
    return False


# =============================================================================
# Schema Validation
# =============================================================================


def _get_model_columns(model_class) -> Dict[str, Dict[str, Any]]:
    """Get column definitions from a SQLAlchemy model."""
    columns = {}
    mapper = inspect(model_class)

    for column in mapper.columns:
        columns[column.name] = {
            "type": str(column.type),
            "nullable": column.nullable,
            "primary_key": column.primary_key,
            "default": str(column.default) if column.default else None,
        }

    return columns


def _get_db_columns(
    engine: Engine, schema: str, table: str
) -> Dict[str, Dict[str, Any]]:
    """Get column definitions from actual database table."""
    inspector = inspect(engine)
    columns = {}

    try:
        for col in inspector.get_columns(table, schema=schema):
            columns[col["name"]] = {
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "primary_key": col.get("primary_key", False),
                "default": str(col.get("default")) if col.get("default") else None,
            }
    except Exception:
        # Table doesn't exist
        pass

    return columns


def _normalize_type(type_str: str) -> str:
    """Normalize SQL type strings for comparison."""
    type_str = type_str.upper()

    # Remove precision/length specifiers for comparison
    if "(" in type_str:
        type_str = type_str.split("(")[0]

    # Normalize common equivalences
    equivalences = {
        "DOUBLE PRECISION": "FLOAT",
        "DOUBLE_PRECISION": "FLOAT",
        "REAL": "FLOAT",
        "INT": "INTEGER",
        "INT4": "INTEGER",
        "INT8": "BIGINT",
        "SERIAL": "INTEGER",
        "BIGSERIAL": "BIGINT",
        "BOOL": "BOOLEAN",
        "TIMESTAMPTZ": "TIMESTAMP",
        "TIMESTAMP WITHOUT TIME ZONE": "TIMESTAMP",
        "TIMESTAMP WITH TIME ZONE": "TIMESTAMP",
        "CHARACTER VARYING": "VARCHAR",
        "TEXT": "VARCHAR",
    }

    return equivalences.get(type_str, type_str)


def _compare_table_columns(
    model_columns: Dict[str, Dict],
    db_columns: Dict[str, Dict],
    table_name: str,
) -> List[str]:
    """Compare model columns with database columns."""
    diffs = []

    model_names = set(model_columns.keys())
    db_names = set(db_columns.keys())

    # Columns in model but not in DB
    for col in sorted(model_names - db_names):
        diffs.append(f"MISSING: {table_name}.{col} (in model, not in DB)")

    # Columns in DB but not in model
    for col in sorted(db_names - model_names):
        diffs.append(f"EXTRA: {table_name}.{col} (in DB, not in model)")

    # Type mismatches
    for col in sorted(model_names & db_names):
        model_type = _normalize_type(model_columns[col]["type"])
        db_type = _normalize_type(db_columns[col]["type"])

        if model_type != db_type:
            diffs.append(
                f"TYPE MISMATCH: {table_name}.{col} "
                f"(model: {model_columns[col]['type']}, db: {db_columns[col]['type']})"
            )

    return diffs


def validate_schema(models: List[tuple], engine: Engine = None) -> None:
    """
    Validate database schema matches SQLAlchemy models. Raises on mismatch.

    Call at application startup to fail fast if schema doesn't match models.

    Args:
        models: List of (model_class, schema_name, table_name) tuples
        engine: SQLAlchemy engine (defaults to default engine)

    Raises:
        SchemaValidationError: If schema doesn't match models

    Example:
        from myapp.models import User, Order
        validate_schema([
            (User, "public", "users"),
            (Order, "public", "orders"),
        ])
    """
    if engine is None:
        engine = _get_engine()

    diffs = []

    for model_class, schema, table in models:
        model_cols = _get_model_columns(model_class)
        db_cols = _get_db_columns(engine, schema, table)

        if not db_cols:
            diffs.append(f"MISSING TABLE: {schema}.{table}")
            continue

        table_diffs = _compare_table_columns(model_cols, db_cols, f"{schema}.{table}")
        diffs.extend(table_diffs)

    if diffs:
        diff_list = "\n  - ".join(diffs)
        raise SchemaValidationError(
            f"Database schema doesn't match models:\n  - {diff_list}\n\n"
            "Apply migrations to sync schema with models."
        )


# =============================================================================
# Database Engine and Session (lazy initialization)
# =============================================================================

_engine = None
_SessionLocal = None


def _get_engine():
    """Get or create the database engine (lazy initialization).

    Uses NullPool when connecting through PgBouncer (port 6432) since
    PgBouncer handles connection pooling. Otherwise uses a minimal pool.
    """
    global _engine
    if _engine is None:
        url = _require_database_url()
        ensure_database(url)

        # Use NullPool for PgBouncer connections (pooling handled externally)
        parts = parse_database_url(url)
        use_pgbouncer = parts["port"] == "6432"

        if use_pgbouncer:
            _engine = create_engine(url, poolclass=NullPool)
        else:
            _engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_size=1,
                max_overflow=2,
            )
    return _engine


def _get_session_factory():
    """Get or create the session factory (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=_get_engine()
        )
    return _SessionLocal


@contextmanager
def get_db() -> Session:
    """
    Get database session context manager.

    Usage:
        from infra_client import get_db

        with get_db() as db:
            users = db.query(User).all()
    """
    SessionLocal = _get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


__all__ = [
    "SchemaValidationError",
    "parse_database_url",
    "ensure_database",
    "validate_schema",
    "get_db",
    "text",
]
