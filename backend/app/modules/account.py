from fastapi import APIRouter, Depends
from typing import Annotated

from ..models.account import Account, BaseAccount, BaseNewAccount
from ..models.errors import BadRequest
from .application import application_read, application_write
from .utils import get_current_account, is_admin_user

router = APIRouter(prefix="/account")

@router.get("/", tags=["account"])
async def get_account(
        is_admin_user: Annotated[bool, Depends(is_admin_user)],
        limit: Annotated[int, "The cap for results (useful for pagination)"] = 10,
        offset: Annotated[int, "The offset for results (useful for pagination)"] = 0,
        order_by: Annotated[str, "The field for results to be ordered by"] = "id",
        order_by_direction: Annotated[str, "The sort order for the results"] = "ASC",
    ) -> dict:
    return application_read.createResponseBody(application_read.getAccounts(limit, offset, order_by, order_by_direction))

@router.post("/", tags=["account"])
async def new_account(
        account: BaseNewAccount,
        is_admin_user: Annotated[bool, Depends(is_admin_user)]
    ) -> dict:

    newAccount = Account(
            username = account.username,
            name = account.name,
            role = account.role,
            password_hash = application_read.hashPassword(account.password),
            disabled = account.disabled
        )

    return application_write.createResponseBody(application_write.newAccount(newAccount))

@router.get("/{id}", tags=["account"])
async def get_account_by_id(id: int | str, is_admin_user: Annotated[bool, Depends(is_admin_user)]) -> dict:
    return application_read.createResponseBody(application_read.getAccount(id = id))

@router.put("/{id}", tags=["account"])
async def edit_account_by_id(
        id: int,
        account: BaseAccount,
        is_admin_user: Annotated[bool, Depends(is_admin_user)]
    ) -> dict:

    if account.id and not id == account.id:
        raise BadRequest("Mismatch between ID and ID in body provided")

    existingAccount = application_read.getAccount(id = id)

    newAccount = Account(
            id = existingAccount.id,
            uuid = account.uuid or existingAccount.uuid,
            username = account.username or existingAccount.username,
            name = account.name or existingAccount.name,
            role = account.role or existingAccount.role,
            password_hash= existingAccount.password_hash,
            password_last_modified = existingAccount.password_last_modified,
            disabled = account.disabled if account.disabled == True or account.disabled == False else existingAccount.disabled,
            created_at = existingAccount.created_at,
            last_modified = existingAccount.last_modified,
        )

    return application_write.createResponseBody(application_write.setAccount(newAccount))
