import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your models' metadata
from models import Base

# set sqlalchemy.url from environment variable if prhttps://github.com/Abhibmc420/Saloon.gitesent
database_url = os.getenv('DATABASE_URL')
if not database_url:
    database_url = os.getenv('SQLITE_PATH')
    if database_url:
        config.set_main_option('sqlalchemy.url', f"sqlite:///{database_url}")
    else:
        # default sqlite
        config.set_main_option('sqlalchemy.url', 'sqlite:///salon.db')
else:
    config.set_main_option('sqlalchemy.url', database_url)


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
