import os

from ..models.database import DatabaseAdapter

database_host = os.environ.get("POSTGRES_HOST", "localhost")
database_name = os.environ.get("POSTGRES_DB", "postgres")
database_user = os.environ.get("POSTGRES_USER", "postgres")
database_pass = os.environ.get("POSTGRES_PASSWORD", None)

database_read_user = os.environ.get("POSTGRES_READ_USER", database_user)
database_read_pass = os.environ.get("POSTGRES_READ_PASSWORD", database_pass)

database_read_only = DatabaseAdapter(database_host, database_name, database_read_user, database_read_pass)
database_read_write = DatabaseAdapter(database_host, database_name, database_user, database_pass)
