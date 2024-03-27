from fastapi import APIRouter, Depends
from typing import Annotated

from .application import application_read, application_write
from .utils import is_authenticated, is_admin_user
from ..models.vehicle import Vehicle, BaseVehicle

router = APIRouter(prefix="/vehicle")

@router.get("/", tags=["vehicle"])
async def get_vehicle(
        is_authenticated: Annotated[dict, Depends(is_authenticated)],
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
    ) -> dict:
    return application_read.createResponseBody(application_read.getVehicles(limit, offset, order_by, order_by_direction))

@router.get("/{fleet_no}", tags=["vehicle"])
async def get_vehicle_by_fleet_number(fleet_no: int | str, is_authenticated: Annotated[dict, Depends(is_authenticated)]) -> dict:
    return application_read.createResponseBody(application_read.getVehicle(fleet_no = fleet_no))

@router.post("/", tags=["account"])
async def new_account(
        vehicle: BaseVehicle,
        is_admin_user: Annotated[bool, Depends(is_admin_user)]
    ) -> dict:

    newVehicle = Vehicle(
            fleet_no = vehicle.fleet_no,
            opco_id = vehicle.opco_id,
        )

    return application_write.createResponseBody(application_write.newVehicle(newVehicle))
