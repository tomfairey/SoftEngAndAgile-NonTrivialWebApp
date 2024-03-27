from fastapi import APIRouter, Depends
from typing import Annotated

from .application import application_read, application_write
from ..models.errors import BadRequest
from ..models.operating_company import BaseOperatingCompany, BaseNewOperatingCompany, OperatingCompany
from .utils import is_authenticated, is_admin_user

router = APIRouter(prefix="/operating-company")

@router.get("/", tags=["operating-company"])
async def get_operating_company(
        current_user: Annotated[dict, Depends(is_authenticated)],
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
    ) -> dict:
    return application_read.createResponseBody(application_read.getOperatingCompanies(limit, offset, order_by, order_by_direction))

@router.post("/", tags=["operating-company"])
async def new_operating_company(operating_company: BaseNewOperatingCompany, is_admin_user: Annotated[dict, Depends(is_admin_user)]) -> dict:
    newOperatingCompany = OperatingCompany(
            id = None,
            noc = operating_company.noc,
            short_code = operating_company.short_code,
            name = operating_company.name
        )

    return application_write.createResponseBody(application_write.newOperatingCompany(newOperatingCompany))

@router.get("/{id}", tags=["operating-company"])
async def get_operating_company_by_id(id: int | str, current_user: Annotated[dict, Depends(is_authenticated)]) -> dict:
    return application_read.createResponseBody(application_read.getOperatingCompany(id = id))

@router.put("/{id}", tags=["operating-company"])
async def edit_operating_company_by_id(
        id: int | str,
        operating_company: BaseOperatingCompany | BaseNewOperatingCompany,
        is_admin_user: Annotated[dict, Depends(is_admin_user)]
    ) -> dict:
    if operating_company.id and not id == operating_company.id:
        raise BadRequest("Mismatch between ID and ID in body provided")

    existingOperatingCompany = application_read.getOperatingCompany(id = id)

    newOperatingCompany = OperatingCompany(
            id = existingOperatingCompany.id,
            noc = operating_company.noc or existingOperatingCompany.noc,
            short_code = operating_company.short_code or existingOperatingCompany.short_code,
            name = operating_company.name or existingOperatingCompany.name
        )

    return application_write.createResponseBody(application_write.setOperatingCompany(newOperatingCompany))

@router.delete("/{id}", tags=["operating-company"])
async def delete_operating_company_by_id(
        id: int | str,
        is_admin_user: Annotated[dict, Depends(is_admin_user)],
        confirmed: bool = False
    ) -> dict:
    return application_write.deleteOperatingCompany(id = id, confirmed = confirmed)
