from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import apps.prompts.models  # noqa: F401
from db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

DJANGO_TABLES = {
    "django_migrations",
    "django_content_type",
    "django_session",
    "django_admin_log",
    "auth_permission",
    "auth_group",
    "auth_group_permissions",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in DJANGO_TABLES:
        return False
    return True


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    import django
    from django.conf import settings

    django.setup()

    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
