from fastapi import APIRouter

from .account import router as router_account
from .application import application_read, application_write
from .authorisation import router as router_authorisation
from .errors import ServiceUnavailable
from .operating_company import router as router_operating_company
from .vehicle import router as router_vehicle
    
router = APIRouter(prefix="/api/v1")

@router.head("/status", tags=["status"])
async def head_status() -> dict:
    return {}

@router.get("/status", tags=["status"])
async def status() -> dict:
    # Ensure databases are reachable, status check will otherwise throw an internal error
    if not application_read.testDatabaseConnection() or not application_write.testDatabaseConnection():
        return ServiceUnavailable("Database connection is not ready!")

    # Database is available, service is available!
    return {"status": 200, "message": "Up"}

# Include account routes
router.include_router(router_account)

# Include authorisation routes
router.include_router(router_authorisation)

# Include operating company routes
router.include_router(router_operating_company)

# Include application routes
router.include_router(router_vehicle)
