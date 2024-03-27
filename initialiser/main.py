import os
import bcrypt
import psycopg
from typing import Annotated
# import psycopg2 as psycopg
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
import socket

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
    
    def commit(self, connection = None) -> None:
        return (connection or self.getConnection()).commit()
    
    def execute(self, *args, cursor: Annotated[psycopg.Cursor, "Cursor to use in lieu of instantiated default"] = None, **kwargs) -> psycopg.Cursor:
        return (cursor or self.getCursor()).execute(*args, **kwargs)   

class ApplicationDatabaseAdapter(DatabaseAdapter):
    # Pass initialisation of class instance to parent class
    def __init__(self, database_host, database_name, database_username, database_password):
        super().__init__(database_host, database_name, database_username, database_password)

    # Pass destruction of class instance to parent class
    def __del__(self):
        super().__del__()

    def canConnect(self):
        try:
            self.getConnection()
        except Exception as e:
            print("Exception while connecting to database!")
            print("Except:", e)
            return False
        
        test_value = 1

        try:
            received_value = self.execute("SELECT %s;", (test_value,)).fetchone()[0]
        except Exception as e:
            print("Exception while confirming connection to database!")
            print("Except:", e)
            return False
        else:
            if received_value is not test_value:
                print("Test query failed, basic value did not match!")
                return False
            
            return True

    # Function to check whether the script has been run previously
    def hasRunPreviously(self):
        try:
            return self.execute("SELECT b FROM initialisation_script LIMIT 1;").fetchone()[0] == 1
        except:
            return False
        
    # Mark database that the script has been run previously
    def setRunPreviously(self):
        try:
            self.execute("CREATE TABLE IF NOT EXISTS initialisation_script (b INT);")
            self.execute("INSERT INTO initialisation_script (b) VALUES (1);")
            return self.getConnection().commit()
        except:
            pass
        
    # Remove the mark that signifies the script has been run previously
    def clearRunPreviously(self):
        try:
            self.execute("DELETE FROM initialisation_script;")
            return self.getConnection().commit()
        except:
            pass

    # Function to wipe the database
    def wipeAll(self):
        # Commit any in-flight changes as the DB will be wiped shortly anyway
        self.getConnection().commit()

        # Attempt to close all connected clients
        try:
            self.getConnection().execute(f"""SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{self.database_name}' AND pid <> pg_backend_pid();""")
        except:
            pass

        self.getConnection().close()

        # Open new connection to default database, otherwise an Exception will occur trying to delete currently opened DB
        connection = self.getConnection(database_name = "postgres")

        # Enable auto commit for the current session to allow deletion of databases
        connection.autocommit = True

        try:
            # Delete the database, if it exists, and re-create under the same name
            connection.execute(f"""DROP DATABASE IF EXISTS "{self.database_name}";""")
            connection.execute(f"""CREATE DATABASE "{self.database_name}";""")
        except psycopg.errors.ObjectInUse:
            print("FATAL:", "Database already in use and could not be wiped, please close any other connections!")
            exit(1)

        # Close the current auto commiting connection to re-enable transactions
        connection.close()

        return
    
    def createTables(self):
        connection = self.getConnection(forceNew = True)

        # self.getConnection().autocommit = True

        # connection.execute("""
        #         CREATE EXTENSION IF NOT EXISTS postgis;
        #     """)
        
        # connection.execute("""
        #         CREATE EXTENSION IF NOT EXISTS postgis;
        #         CREATE EXTENSION IF NOT EXISTS pg_trgm;
        #     """)
        
        # connection.close()

        # connection = self.getConnection(forceNew = True)

        with self.getCursor(connection = connection, forceNew = True) as cursor:
            # Enable the postgis and pgcrypto extensions
            # cursor.execute("""
            #     CREATE EXTENSION IF NOT EXISTS postgis;
            #     CREATE EXTENSION IF NOT EXISTS pgcrypto;
            # """)
            cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS pgcrypto;
            """)

            # Create the users table
            cursor.execute("""CREATE TABLE IF NOT EXISTS account (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) NOT NULL UNIQUE DEFAULT gen_random_uuid(),
                    role VARCHAR(3) NOT NULL DEFAULT 'STD',
                    username VARCHAR(36) NOT NULL UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(60) NOT NULL,
                    password_last_modified TIMESTAMP NOT NULL DEFAULT now(),
                    disabled BOOLEAN NOT NULL DEFAULT True,
                    created_at TIMESTAMP NOT NULL DEFAULT now(),
                    last_modified TIMESTAMP NOT NULL DEFAULT now()
                );""")

            ## Fifth (and unnecessary table - remove!)
            # Create the event log table
            cursor.execute("""CREATE TABLE IF NOT EXISTS event_log (
                    id SERIAL PRIMARY KEY,
                    event VARCHAR(36) NOT NULL,
                    message VARCHAR(255),
                    account_id INT,
                    timestamp TIMESTAMP NOT NULL,
                    CONSTRAINT fk_event_log_account_id
                        FOREIGN KEY (account_id)
                        REFERENCES account(id)
                );""")
            ## Fifth (and unnecessary table - remove!)

            # Create the operating companies table
            cursor.execute("""CREATE TABLE IF NOT EXISTS operating_company (
                    id SERIAL PRIMARY KEY,
                    noc VARCHAR(4) NOT NULL UNIQUE,
                    short_code VARCHAR(3) NOT NULL UNIQUE,
                    name VARCHAR(255)
                );""")

            # Create the vehicles table
            cursor.execute("""CREATE TABLE IF NOT EXISTS vehicle (
                    fleet_no VARCHAR(5) PRIMARY KEY,
                    opco_id INT,
                    CONSTRAINT fk_vehicle_opco_id
                        FOREIGN KEY (opco_id)
                        REFERENCES operating_company(id)
                );""")
            
            # Create the vehicle locations table
            # cursor.execute("""CREATE TABLE IF NOT EXISTS vehicle_location (
            #         id SERIAL PRIMARY KEY,
            #         fleet_no VARCHAR(5),
            #         updated_timestamp TIMESTAMP WITH TIME ZONE,
            #         recorded_timestamp TIMESTAMP WITH TIME ZONE,
            #         latitude DOUBLE PRECISION,
            #         longitude DOUBLE PRECISION,
            #         geolocation GEOMETRY(POINT, 4326),
            #         CONSTRAINT fk_vehicle_location_fleet_no
            #             FOREIGN KEY (fleet_no)
            #             REFERENCES vehicle(fleet_no)
            #     );""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS vehicle_location (
                    id SERIAL PRIMARY KEY,
                    fleet_no VARCHAR(5),
                    updated_timestamp TIMESTAMP WITH TIME ZONE,
                    recorded_timestamp TIMESTAMP WITH TIME ZONE,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    CONSTRAINT fk_vehicle_location_fleet_no
                        FOREIGN KEY (fleet_no)
                        REFERENCES vehicle(fleet_no)
                );""")
            
            # Create the indexes for all table to speed up future queries
            # cursor.execute("""
            #         CREATE INDEX IF NOT EXISTS vehicle_fleet_no_index ON vehicle (fleet_no);

            #         CREATE INDEX IF NOT EXISTS vehicle_location_id_index ON vehicle_location (id);
            #         CREATE INDEX IF NOT EXISTS vehicle_location_fleet_no_index ON vehicle_location (fleet_no);
            #         CREATE INDEX IF NOT EXISTS vehicle_location_spindex ON vehicle_location USING gist (geolocation);
            #     """)
            cursor.execute("""
                    CREATE INDEX IF NOT EXISTS vehicle_fleet_no_index ON vehicle (fleet_no);

                    CREATE INDEX IF NOT EXISTS vehicle_location_id_index ON vehicle_location (id);
                    CREATE INDEX IF NOT EXISTS vehicle_location_fleet_no_index ON vehicle_location (fleet_no);
                """)
            
        # Commit the changes to the database
        connection.commit()

        connection.close()

    def hashPassword(self, password: Annotated[str, "String value to be BCrypted"]):
        # Declaring our password
        password = password.encode("utf-8")
        
        # Generate a salt for the password
        salt = bcrypt.gensalt()
        
        # Return the hashed password
        return bcrypt.hashpw(password, salt).decode("utf-8")
    
    def addUser(
        self,
        username: Annotated[str, "The username for the new user"],
        name: Annotated[str, "The name of the new user"],
        password: Annotated[str, "The password for the new user"],
        role:  Annotated[str, "The role for the new user ('STD', 'ADM')"]
    ):
        connection = self.getConnection()

        with self.getCursor(connection = connection) as cursor:
            # Create the users table            
            cursor.execute("""INSERT INTO account (
                        username,
                        name,
                        password_hash,
                        role,
                        disabled
                    )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        );
                """, (
                        username,
                        name,
                        self.hashPassword(password),
                        role,
                        False
                    ))
            
        # Commit the changes to the database
        connection.commit()
        connection.close()

    def createAdmin(self, default_admin_password: str):
        self.addUser("admin", "Administrator", default_admin_password, "ADM")

if __name__ == "__main__":
    force_run = os.environ.get("FORCE_RUN", "0")

    database_host = os.environ.get("POSTGRES_HOST", "localhost")
    database_name = os.environ.get("POSTGRES_DB", "postgres")
    database_user = os.environ.get("POSTGRES_USER", "postgres")
    database_pass = os.environ.get("POSTGRES_PASSWORD", None)
    default_admin_password = os.environ.get("ADMIN_PASSWORD", "Admin1!")

    if not database_pass:
        print("Database password must be specified! Please specify a $POSTGRES_PASSWORD value...")
        exit(1)

    database = ApplicationDatabaseAdapter(database_host, database_name, database_user, database_pass)

    print("Checking connection to database...")
    canConnect = database.canConnect()
    
    if not canConnect:
        print("Could not connect to database using specified credentials! Exiting...")

        # ip_list = list({addr[-1][0] for addr in socket.getaddrinfo(database_host, 0, 0, 0, 0)})

        # print(f"IPs for host '{database_host}':")
        # print(ip_list)

        exit(1)
    else:
        print("Connection to database was successful!")

    # TODO: Check the logic here
    if (not force_run or force_run == "0") and database.hasRunPreviously():
        print("Exiting: Process has detected previous successful run!")
        print("Set $FORCE_RUN to 1 to execute regardless...")
        exit(0)

    # Clear previously ran mark, if script fails before completion, next launch will transparently resume
    database.clearRunPreviously()

    # Delete entire database and re-create under same name
    print("Wiping database...")
    database.wipeAll()
    print("Wiped!")

    # Create all tables and indexes within database
    print("Creating tables...")
    database.createTables()
    print("Created!")

    # Create default accounts for system
    print("Creating default login accounts...")
    database.createAdmin(default_admin_password = default_admin_password)
    print("Created!")

    # Set previously ran mark so script does not automatically delete all data on next automatic launch
    database.setRunPreviously()

    exit(0)
