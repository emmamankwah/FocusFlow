import sys, os

# Make the project root importable so Alembic can discover the app package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.core.config import settings
from app.database.session import Base
from app.models import users
from app.models import Categories
from app.models import task
from app.models import pending_users
from app.models import email_outbox

# This is the Alembic Config object, which exposes the active migration configuration.
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configure Python logging from the Alembic config file if available.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the app's metadata object here so Alembic can detect model changes during autogenerate.
target_metadata = Base.metadata

# Other values from the config, defined by the needs of env.py, can be acquired here.
# For example: my_important_option = config.get_main_option("my_important_option")


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
        compare_server_default= True 
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
            connection=connection, 
            target_metadata=target_metadata,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
