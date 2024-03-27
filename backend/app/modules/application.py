from ..models.application import Application
from ..modules.database import database_read_only, database_read_write

application_read = Application(database_adapter = database_read_only)
application_write = Application(database_adapter = database_read_write, write_enabled = True)
