from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine

from alembic import context

# Import your app models and settings
from app import models  # ensure models are imported so metadata is available
from app.models import Base
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Prefer a single DATABASE_URL env var (easier for Render/CI)
def _normalize_database_url(url: str) -> str:
    # Normalize common prefixes to explicit SQLAlchemy + driver style
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        # make explicit driver if missing
        if "psycopg2" not in url and "+psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # Ensure sslmode is present for Supabase
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = url + f"{sep}sslmode=require"

    return url

# Set the sqlalchemy.url config value: prefer DATABASE_URL, else build from settings
database_url_env = os.getenv("DATABASE_URL")
if database_url_env:
    database_url_env = _normalize_database_url(database_url_env)
    config.set_main_option("sqlalchemy.url", database_url_env)
else:
    # fallback to existing settings-based URL (keep your pattern, but include sslmode)
    fallback = (
        f"postgresql+psycopg2://"
        f"{settings.database_username}:"
        f"{settings.database_password}@"
        f"{settings.database_hostname}:"
        f"{settings.database_port}/"
        f"{settings.database_name}"
        f"?sslmode=require"
    )
    config.set_main_option("sqlalchemy.url", fallback)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()






# from logging.config import fileConfig
# import os

# from sqlalchemy import engine_from_config
# from sqlalchemy import pool

# from app import models
# from alembic import context
# from app.models import Base
# from app.config import settings

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# def get_url():
#     return os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

# # prefer a full DATABASE_URL env var (easiest for runtime & CI)
# database_url = os.getenv("DATABASE_URL")
# if database_url:
#     # ensure using psycopg2 dialect if user supplied a plain postgres:// URL
#     # SQLAlchemy accepts both but explicitly using postgresql+psycopg2 avoids ambiguity
#     if database_url.startswith("postgres://"):
#         database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
#     config.set_main_option("sqlalchemy.url", database_url)
# else:
#     # fallback to settings-derived URL (keeps your current behavior)
#     config.set_main_option(
#         "sqlalchemy.url",
#         f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}?sslmode=require'
#     )