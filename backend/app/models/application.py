from typing import Annotated, List
import bcrypt
from psycopg.errors import ForeignKeyViolation, InterfaceError, UniqueViolation
from fastapi.responses import JSONResponse

from ..models.account import Account
from ..models.authorisation import AuthorisationAdapter
from ..models.database import DatabaseAdapter
from ..models.errors import BadRequest, Conflict, Locked, NotFound
from ..models.operating_company import OperatingCompany
from ..models.vehicle import Vehicle

class Application:
    # On initialisation of class instance
    def __init__(
            self,
            database_adapter: Annotated[DatabaseAdapter | None, "An instantiated database adapter"],
            write_enabled: Annotated[bool, "Whether to accept write operations when using this application instance"] = False
        ):
        self.__set_database_adapter__(database_adapter = database_adapter)
        self.__set_write_enabled__(write_enabled)

    # On destruction of class instance
    def __del__(self):
        pass

    def __set_database_adapter__(self, database_adapter: Annotated[DatabaseAdapter, "An instantiated database adapter"]):
        self.database_adapter = database_adapter

    def __get_database_adapter__(self) -> DatabaseAdapter:
        if not self.database_adapter:
            raise Exception("No database connection has been stored!")
        
        return self.database_adapter
    
    def __set_write_enabled__(self, write_enabled: Annotated[bool, "Whether to accept write operations when using this application instance"] = False):
        self.__write_enabled__ = write_enabled

    def __get_write_enabled__(self) -> bool:
        return self.__write_enabled__
    
    def __get_account_with_params__(
            self,
            limit: int,
            offset: int,
            order_by: str,
            order_by_direction: str,
            database_adapter
        ) -> dict:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        # Offset cannot be negative so reset to 0
        if offset < 0:
            offset = 0

        # Ensure only allowed values make it into the non-prepared statement
        if not order_by_direction == "ASC" and not order_by_direction == "DESC":
            order_by_direction = "ASC"

        # Ensure filter is limited only to allowed fields
        order_by_int = 1

        match order_by:
            case 'uuid':
                order_by_int = 2
            case 'role':
                order_by_int = 3
            case 'username':
                order_by_int = 4
            case 'name':
                order_by_int = 5
            # Don't allow sort by password_hash
            case 'password_last_modified':
                order_by_int = 7
            case 'disabled':
                order_by_int = 8
            case 'created_at':
                order_by_int = 9
            case 'last_modified':
                order_by_int = 10
            case _: # id field as default (fallback)
                order_by_int = 1
        
        data = []
        final = []

        if limit > 1:
            try:
                data = cursor.execute("""
                        SELECT
                            id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified, count(*) OVER() AS full_count
                        FROM
                            account
                        ORDER BY
                            {0} {1}
                        LIMIT
                            %s
                        OFFSET
                            %s
                    ;""".format(order_by_int, order_by_direction), (int(limit),int(offset),)).fetchall()
                
            except Exception as e:
                connection.rollback()
                raise e
        
        elif limit < 1 or len(data) < 1:
            try:
                data = cursor.execute("""
                        SELECT
                            count(*) OVER() AS full_count
                        FROM
                            account
                        ORDER BY
                            %s {0}
                        LIMIT
                            1
                    ;""".format(order_by_direction), (str(order_by),)).fetchall()
                
                cursor.close()
                
            except Exception as e:
                connection.rollback()
                raise e
            
            return {
                    "result": final,
                    "meta": {
                        "max": data[0][0] if len(data) > 0 else 0,
                        "limit": limit,
                        "offset": offset,
                        "orderBy": order_by,
                        "orderByDirection": order_by_direction
                    }
                }
        
        cursor.close()
        
        for item in data:
            final.append(Account(id = item[0], uuid = item[1], role = item[2], username = item[3], name = item[4], password_hash = item[5], password_last_modified = item[6], disabled = item[7], created_at = item[8], last_modified = item[9]))

        return {
                "result": final,
                "meta": {
                    "max": data[0][10] if len(data) > 0 else 0,
                    "limit": limit,
                    "offset": offset,
                    "orderBy": order_by,
                    "orderByDirection": order_by_direction
                }
            }

    def __get_vehicle_by_fleet_no__(self, fleet_no: str, database_adapter) -> Vehicle:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    SELECT
                        fleet_no, opco_id
                    FROM
                        vehicle
                    WHERE
                        vehicle.fleet_no = %s
                    LIMIT
                        1
                ;""", (str(fleet_no),)).fetchone()
            
            cursor.close()
            
            if not data:
                raise NotFound("No vehicle matching specified fleet number...")
            
            # if less than 1, error (error 404 no vehicle by that fleet_no)
        except Exception as e:
            connection.rollback()
            raise e

        return Vehicle(fleet_no = data[0], opco_id = data[1])

    def __new_vehicle__(self, vehicle: Vehicle, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    INSERT INTO
                        vehicle
                        (fleet_no, opco_id)
                    VALUES
                        (%s, %s)
                    RETURNING
                        fleet_no, opco_id
                ;""", (int(vehicle.fleet_no),int(vehicle.opco_id),)).fetchone()
            
            if not data:
                raise NotFound("No operating company matching specified id...")
            
            cursor.close()
            connection.commit()
            
        except UniqueViolation:
            connection.rollback()
            raise Conflict("Duplicate value for a unique field, please ensure necessary field(s) are unique!")
        except Exception as e:
            connection.rollback()
            raise e

        return Vehicle(fleet_no = data[0], opco_id = data[1])

    def __get_vehicle_with_params__(
            self,
            limit: int,
            offset: int,
            order_by: str,
            order_by_direction: str,
            database_adapter
        ) -> dict:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        # Offset cannot be negative so reset to 0
        if offset < 0:
            offset = 0

        # Ensure only allowed values make it into the non-prepared statement
        if not order_by_direction == "ASC" and not order_by_direction == "DESC":
            order_by_direction = "ASC"

        # Ensure filter is limited only to allowed fields
        order_by_int = 1

        match order_by:
            case 'opco_id':
                order_by_int = 2
            case _: # fleet_no field as default (fallback)
                order_by_int = 1
        
        data = []
        final = []

        if limit > 1:
            try:
                data = cursor.execute("""
                        SELECT
                            fleet_no, opco_id, count(*) OVER() AS full_count
                        FROM
                            vehicle
                        ORDER BY
                            {0} {1}
                        LIMIT
                            %s
                        OFFSET
                            %s
                    ;""".format(order_by_int, order_by_direction), (int(limit),int(offset),)).fetchall()
                
            except Exception as e:
                connection.rollback()
                raise e
        
        elif limit < 1 or len(data) < 1:
            try:
                data = cursor.execute("""
                        SELECT
                            count(*) OVER() AS full_count
                        FROM
                            vehicle
                        ORDER BY
                            %s {0}
                        LIMIT
                            1
                    ;""".format(order_by_direction), (str(order_by),)).fetchall()
                
                cursor.close()
                
            except Exception as e:
                connection.rollback()
                raise e
            
            return {
                    "result": final,
                    "meta": {
                        "max": data[0][0] if len(data) > 0 else 0,
                        "limit": limit,
                        "offset": offset,
                        "orderBy": order_by,
                        "orderByDirection": order_by_direction
                    }
                }
        
        cursor.close()
        
        for item in data:
            final.append(Vehicle(fleet_no = item[0], opco_id = item[1]))

        return {
                "result": final,
                "meta": {
                    "max": data[0][2] if len(data) > 0 else 0,
                    "limit": limit,
                    "offset": offset,
                    "orderBy": order_by,
                    "orderByDirection": order_by_direction
                }
            }
    
    def __set_operating_company_by_id__(self, id: int, operating_company: OperatingCompany, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    UPDATE
                        operating_company
                    SET
                        noc = %s,
                        short_code = %s,
                        name = %s
                    WHERE
                        id = %s
                    RETURNING
                        id, noc, short_code, name
                ;""", (str(operating_company.noc),str(operating_company.short_code),str(operating_company.name),int(operating_company.id),)).fetchone()
            
            if not data:
                raise NotFound("No operating company matching specified id...")
            
            cursor.close()
            connection.commit()
        
        except UniqueViolation:
            connection.rollback()
            raise Conflict("Duplicate value for a unique field, please ensure necessary field(s) are unique!")
        except Exception as e:
            connection.rollback()
            raise e

        return OperatingCompany(id = data[0], noc = data[1], short_code = data[2], name = data[3])
    
    def __new_operating_company__(self, operating_company: OperatingCompany, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    INSERT INTO
                        operating_company
                        (noc, short_code, name)
                    VALUES
                        (%s, %s, %s)
                    RETURNING
                        id, noc, short_code, name
                ;""", (str(operating_company.noc),str(operating_company.short_code),str(operating_company.name),)).fetchone()
            
            if not data:
                raise NotFound("No operating company matching specified id...")
            
            cursor.close()
            connection.commit()
            
        except UniqueViolation:
            connection.rollback()
            raise Conflict("Duplicate value for a unique field, please ensure necessary field(s) are unique!")
        except Exception as e:
            connection.rollback()
            raise e

        return OperatingCompany(id = data[0], noc = data[1], short_code = data[2], name = data[3])
    
    def __delete_operating_company__(self, id: int | str, database_adapter, confirmed: bool = False) -> dict:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    DELETE FROM
                        operating_company
                    WHERE
                        id = %s
                    RETURNING
                        id, noc, short_code, name
                ;""", (int(id),)).fetchall()
            
            if len(data) < 1:
                raise NotFound("No operating company matching specified id...")
            
            cursor.close()

            if confirmed:
                connection.commit()
        
        except Exception as e:
            connection.rollback()
            raise e

        return data
    
    def __get_operating_company_with_params__(
            self,
            limit: int,
            offset: int,
            order_by: str,
            order_by_direction: str,
            database_adapter
        ) -> dict:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        # Offset cannot be negative so reset to 0
        if offset < 0:
            offset = 0

        # Ensure only allowed values make it into the non-prepared statement
        if not order_by_direction == "ASC" and not order_by_direction == "DESC":
            order_by_direction = "ASC"

        # Ensure filter is limited only to allowed fields
        order_by_int = 1

        match order_by:
            case 'noc':
                order_by_int = 2
            case 'short_code':
                order_by_int = 3
            case 'name':
                order_by_int = 4
            case _: # id field as default (fallback)
                order_by_int = 1

        data = []
        final = []

        if limit > 1:
            try:
                data = cursor.execute("""
                        SELECT
                            id, noc, short_code, name, count(*) OVER() AS full_count
                        FROM
                            operating_company
                        ORDER BY
                            {0} {1}
                        LIMIT
                            %s
                        OFFSET
                            %s
                    ;""".format(order_by_int, order_by_direction), (int(limit),int(offset),)).fetchall()
                
            except Exception as e:
                connection.rollback()
                raise e
            
        elif limit < 1 or len(data) < 1:
            try:
                data = cursor.execute("""
                        SELECT
                            count(*) OVER() AS full_count
                        FROM
                            operating_company
                        ORDER BY
                            %s {0}
                        LIMIT
                            1
                    ;""".format(order_by_direction), (str(order_by),)).fetchall()
                
                cursor.close()
                
            except Exception as e:
                connection.rollback()
                raise e
            
            return {
                    "result": final,
                    "meta": {
                        "max": data[0][0] if len(data) > 0 else 0,
                        "limit": limit,
                        "offset": offset,
                        "orderBy": order_by,
                        "orderByDirection": order_by_direction
                    }
                }
        
        cursor.close()
        
        for item in data:
            final.append(OperatingCompany(id = item[0], noc = item[1], short_code = item[2], name = item[3]))

        return {
                "result": final,
                "meta": {
                    "max": data[0][4] if len(data) > 0 else 0,
                    "limit": limit,
                    "offset": offset,
                    "orderBy": order_by,
                    "orderByDirection": order_by_direction
                }
            }
    
    def __get_operating_company_by_id__(self, id: int, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            data = cursor.execute("""
                    SELECT
                        id, noc, short_code, name
                    FROM
                        operating_company
                    WHERE
                        operating_company.id = %s
                    LIMIT
                        1
                ;""", (str(id),)).fetchone()
            
            cursor.close()
            
            if not data:
                raise NotFound("No operating company matching specified id...")
            
        except Exception as e:
            connection.rollback()
            raise e

        return OperatingCompany(id = data[0], noc = data[1], short_code = data[2], name = data[3])
    
    def __get_account_by_id__(self, id: int, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            account_data = cursor.execute("""
                    SELECT
                        id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified
                    FROM
                        account
                    WHERE
                        account.id = %s
                    LIMIT
                        1
                ;""", (str(id),)).fetchone()
            
            cursor.close()
            
            if not account_data:
                raise NotFound("No account matching specified id...")
            
        except Exception as e:
            connection.rollback()
            raise e

        return Account(
                id = account_data[0],
                uuid = account_data[1],
                role = account_data[2],
                username = account_data[3],
                name = account_data[4],
                password_hash = account_data[5],
                password_last_modified = account_data[6],
                disabled = account_data[7],
                created_at = account_data[8],
                last_modified = account_data[9],
            )
    
    def __get_account_by_uuid__(self, uuid: str, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            account_data = cursor.execute("""
                    SELECT
                        id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified
                    FROM
                        account
                    WHERE
                        account.uuid = %s
                    LIMIT
                        1
                ;""", (str(uuid),)).fetchone()
            
            cursor.close()
            
            if not account_data:
                raise NotFound("No account matching specified uuid...")
            
        except Exception as e:
            connection.rollback()
            raise e

        return Account(
                id = account_data[0],
                uuid = account_data[1],
                role = account_data[2],
                username = account_data[3],
                name = account_data[4],
                password_hash = account_data[5],
                password_last_modified = account_data[6],
                disabled = account_data[7],
                created_at = account_data[8],
                last_modified = account_data[9],
            )
    
    def __get_account_by_username__(self, username: str, database_adapter) -> OperatingCompany:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            account_data = cursor.execute("""
                    SELECT
                        id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified
                    FROM
                        account
                    WHERE
                        account.username = %s
                    LIMIT
                        1
                ;""", (str(username),)).fetchone()
            
            cursor.close()
            
            if not account_data:
                raise NotFound("No account matching specified username...")
            
        except Exception as e:
            connection.rollback()
            raise e

        return Account(
                id = account_data[0],
                uuid = account_data[1],
                role = account_data[2],
                username = account_data[3],
                name = account_data[4],
                password_hash = account_data[5],
                password_last_modified = account_data[6],
                disabled = account_data[7],
                created_at = account_data[8],
                last_modified = account_data[9],
            )
    
    def __new_account__(self, account: Account, database_adapter) -> Account:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            account_data = cursor.execute("""
                    INSERT INTO
                        account
                        (username, name, role, disabled, password_hash)
                    VALUES
                        (%s, %s, %s, %s, %s)
                    RETURNING
                        id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified
                ;""", (str(account.username),str(account.name),str(account.role),bool(account.disabled),str(account.password_hash),)).fetchone()
            
            if not account_data:
                raise NotFound("No account matching specified id...")
            
            cursor.close()
            connection.commit()
            
        except UniqueViolation:
            connection.rollback()
            raise Conflict("Duplicate value for a unique field, please ensure necessary field(s) are unique!")
        except Exception as e:
            connection.rollback()
            raise e

        return Account(
                id = account_data[0],
                uuid = account_data[1],
                role = account_data[2],
                username = account_data[3],
                name = account_data[4],
                password_hash = account_data[5],
                password_last_modified = account_data[6],
                disabled = account_data[7],
                created_at = account_data[8],
                last_modified = account_data[9],
            )
    
    def __set_account_by_id__(self, id: int, account: Account, database_adapter) -> Account:
        database_adapter = database_adapter or self.__get_database_adapter__()

        connection = self.database_adapter.getConnection(forceNew = True)
        cursor = self.database_adapter.getCursor(connection = connection)

        try:
            account_data = cursor.execute("""
                    UPDATE
                        account
                    SET
                        uuid = %s,
                        role = %s,
                        username = %s,
                        name = %s,
                        password_hash = %s,
                        password_last_modified = %s,
                        disabled = %s,
                        created_at = %s,
                        last_modified = %s
                    WHERE
                        id = %s
                    RETURNING
                        id, uuid, role, username, name, password_hash, password_last_modified, disabled, created_at, last_modified
                ;""", (str(account.uuid),str(account.role),str(account.username),str(account.name),str(account.password_hash),str(account.password_last_modified),bool(account.disabled),str(account.created_at),str(account.last_modified),int(account.id))).fetchone()
            
            if not account_data:
                raise NotFound("No account matching specified id...")
            
            cursor.close()
            connection.commit()
        
        except UniqueViolation:
            connection.rollback()
            raise Conflict("Duplicate value for a unique field, please ensure necessary field(s) are unique!")
        except Exception as e:
            connection.rollback()
            raise e

        return Account(
                id = account_data[0],
                uuid = account_data[1],
                role = account_data[2],
                username = account_data[3],
                name = account_data[4],
                password_hash = account_data[5],
                password_last_modified = account_data[6],
                disabled = account_data[7],
                created_at = account_data[8],
                last_modified = account_data[9],
            )

    def setDatabaseConnection(
            self,
            database_adapter: Annotated[DatabaseAdapter, "A database adpater to use as the default instatiation held adapter"],
            write_enabled: Annotated[bool, "Whether to accept write operations when using this application instance"] = False
        ):
        if not database_adapter:
            raise Exception("Database connection was not provided!")
        
        if database_adapter.closed is True:
            raise InterfaceError("Database connection is already closed!")
        
        self.__set_database_adapter__(database_adapter)
        self.__set_write_enabled__(write_enabled)

    def testDatabaseConnection(self, test_value: str | int | bool = 1) -> bool:
        try:
            received_value = self.__get_database_adapter__().execute("SELECT %s;", (test_value,)).fetchone()[0]
        except Exception as e:
            return False
        else:
            if received_value is not test_value:
                return False
            
            return True
        
    def getAccounts(
        self,
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> dict:
        return self.__get_account_with_params__(
                limit = limit,
                offset = offset,
                order_by = order_by,
                order_by_direction = order_by_direction,
                database_adapter = database_adapter
            )
    
    def newAccount(
        self,
        account: Account,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> OperatingCompany:
        if account.id:
            raise BadRequest("ID should not be specified for new account!")

        return self.__new_account__(account = account, database_adapter = database_adapter)
    
    def setAccount(
        self,
        account: Account,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> Account:
        if not account.id:
            raise BadRequest("Operating company ID not provided!")

        return self.__set_account_by_id__(id = id, account = account, database_adapter = database_adapter)
        
    def getVehicles(
        self,
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> dict:
        return self.__get_vehicle_with_params__(
                limit = limit,
                offset = offset,
                order_by = order_by,
                order_by_direction = order_by_direction,
                database_adapter = database_adapter
            )

    def getVehicle(
        self,
        fleet_no: Annotated[str, "The fleet number of the desired vehicle"],
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> Vehicle:
        if not fleet_no:
            raise BadRequest("Fleet number not provided!")

        return self.__get_vehicle_by_fleet_no__(fleet_no = fleet_no, database_adapter = database_adapter)
    
    def newVehicle(
        self,
        vehicle: Vehicle,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> Vehicle:
        return self.__new_vehicle__(vehicle = vehicle, database_adapter = database_adapter)
    
    def getOperatingCompanies(
        self,
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    # ) -> List[OperatingCompany]:
    ) -> dict:
        return self.__get_operating_company_with_params__(
                limit = limit,
                offset = offset,
                order_by = order_by,
                order_by_direction = order_by_direction,
                database_adapter = database_adapter
            )
    
    def getOperatingCompany(
        self,
        id: Annotated[str, "The ID of the desired operating company"],
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> OperatingCompany:
        if not id:
            raise BadRequest("Operating company ID not provided!")

        return self.__get_operating_company_by_id__(id = id, database_adapter = database_adapter)
    
    def setOperatingCompany(
        self,
        operating_company: OperatingCompany,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> OperatingCompany:
        if not operating_company.id:
            raise BadRequest("Operating company ID not provided!")

        return self.__set_operating_company_by_id__(id = id, operating_company = operating_company, database_adapter = database_adapter)
    
    def newOperatingCompany(
        self,
        operating_company: OperatingCompany,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> OperatingCompany:
        if operating_company.id:
            raise BadRequest("ID should not be specified for new operating company!")

        return self.__new_operating_company__(operating_company = operating_company, database_adapter = database_adapter)
    
    def deleteOperatingCompany(
        self,
        id: Annotated[str, "The ID of the desired operating company"],
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None,
        confirmed: bool = False
    ) -> JSONResponse:
        if not id:
            raise BadRequest("Operating company ID not provided!")

        try:
            records = self.__delete_operating_company__(id = id, database_adapter = database_adapter, confirmed = confirmed)

            return JSONResponse(content = {
                    "message": f"This operation has deleted {len(records)} record(s)!" if confirmed
                        else f"This operation will delete {len(records)} item(s), please confirm...",
                    "result": {
                        "rows": records,
                        "length": len(records),
                    }
                })
        except ForeignKeyViolation:
            return Conflict("Vehicles have been assigned to this operating company so it may not be deleted! You may still edit details...")
    
    def handleSerialisation(self, x: OperatingCompany | Vehicle, root: str = ""):
        return {
                **(
                    { **(x.serialise() or {}), **({"links": x.hypermediaLinks(root) or []} if hasattr(x, "hypermediaLinks") else {}) } if hasattr(x, "serialise")
                    else {}
                )
                # **({"result": x.serialise() or {}} if hasattr(x, "serialise") else {}),
                # **({"links": x.hypermediaLinks(root) or []} if hasattr(x, "hypermediaLinks") else {}),
            } 
    
    def createResponseBody(
            self,
            x: dict | OperatingCompany | Vehicle | List[OperatingCompany] | List[Vehicle],
            root: str = "",
            no_result_key: bool = False
        ):
        if isinstance(x, dict) and "result" in x:
            return { **x, "result": self.createResponseBody(x["result"], no_result_key = True) }

        if isinstance(x, List):
            if no_result_key:
                return map(self.handleSerialisation, x)
            return { "result": map(self.handleSerialisation, x) }

        if no_result_key:
            return self.handleSerialisation(x, root)
        
        return { "result": self.handleSerialisation(x, root) }
    
    def getAccount(
        self,
        id: Annotated[str, "The ID of the desired account"] = None,
        uuid: Annotated[str, "The UUID of the desired account"] = None,
        username: Annotated[str, "The username of the desired account"] = None,
        database_adapter: Annotated[DatabaseAdapter | None, "A database connection to use in lieu of the default instatiation held adapter"] = None
    ) -> Account:
        if id:
            return self.__get_account_by_id__(id = id, database_adapter = database_adapter)
        
        if uuid:
            return self.__get_account_by_uuid__(uuid = uuid, database_adapter = database_adapter)
        
        if username:
            return self.__get_account_by_username__(username = username, database_adapter = database_adapter)
        
        raise BadRequest("An account identifier was not provided!")
    
    def hashPassword(self, password: Annotated[str, "String value to be BCrypted"]):
        # Declaring our password
        password = password.encode("utf-8")
        
        # Generate a salt for the password
        salt = bcrypt.gensalt()
        
        # Return the hashed password
        return bcrypt.hashpw(password, salt).decode("utf-8")
    
    def matchAccountPassword(self, account: Account, password: bytes) -> bool:
        return bcrypt.checkpw(password = password.encode("utf-8"), hashed_password = account.password_hash.encode("utf-8"))
    
    def generateTokenPairForAccount(self, account: Account, authorisation: AuthorisationAdapter)-> str:
        return authorisation.generateTokenPair(account)
    
    def generateTokenForAccount(self, account: Account, authorisation: AuthorisationAdapter)-> str:
        return authorisation.generateAccessToken(account)
