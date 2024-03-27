import psycopg
from typing import Annotated

class DatabaseAdapter:
    # On initialisation of class instance
    def __init__(self, database_host, database_name, database_username, database_password):
        self.database_host = database_host
        self.database_name = database_name
        self.database_username = database_username
        self.database_password = database_password

    # On destruction of class instance
    def __del__(self):
        # If the class instance has an open connection stored
        if hasattr(self, "_connection") and self._connection and self._connection.closed is not True:
            # Close the open connection
            self._connection.close()

    def _connect(self, database_name: Annotated[str, "Database name to use in lieu of instantiated default"] = None) -> psycopg.Connection:
        database_host = self.database_host
        database_name = (database_name or self.database_name)
        database_username = self.database_username
        database_password = self.database_password
                                                      
        print(f"Connecting to: '{database_username}@{database_host}/{database_name}'...")
        return psycopg.connect(f"""
                dbname='{database_name}'
                user='{database_username}'
                host='{database_host}'
                password='{database_password}'
            """)
    
    def _get_cursor(self, connection: Annotated[psycopg.Connection, "Connection to use in lieu of instantiated default"] = None) -> psycopg.Cursor:
        return (connection or self.getConnection()).cursor()

    def getConnection(self, forceNew = False, database_name: Annotated[str, "Database name to use in lieu of instantiated default"] = None) -> psycopg.Connection:
        if forceNew or database_name:
            return self._connect(database_name = database_name)
        
        if not hasattr(self, "_connection") or not self._connection or self._connection.closed is True:
            self._connection = self._connect()

        return self._connection
        
    def getCursor(self, forceNew = False, connection: Annotated[psycopg.Connection, "Connection to use in lieu of instantiated default"] = None) -> psycopg.Cursor:
        if forceNew or connection:
            return self._get_cursor(connection = connection)
        
        if not hasattr(self, "_cursor") or not self._cursor or self._cursor.closed is True:
            self._cursor = self._get_cursor()
        
        return self._cursor
    
    def close(self) -> None:
        return self.getCursor().close()
    
    def closed(self) -> None:
        if not hasattr(self, "_connection") or not self._connection or self._connection.closed is True:
            return True
        
        return self._connection.closed
    
    def commit(self, connection = None) -> None:
        return (connection or self.getConnection()).commit()
    
    def execute(self, *args, cursor: Annotated[psycopg.Cursor, "Cursor to use in lieu of instantiated default"] = None, **kwargs) -> psycopg.Cursor:
        return (cursor or self.getCursor()).execute(*args, **kwargs)
