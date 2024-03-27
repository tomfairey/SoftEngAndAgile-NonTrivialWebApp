from fastapi import Depends, HTTPException
from typing import Annotated
from jose.exceptions import ExpiredSignatureError

from ..modules.authorisation import authorisation, oauth2_scheme
from .errors import Forbidden, Unauthorised

async def get_current_account(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        claims = authorisation.decode(token)

        if not claims:
            raise Unauthorised("No claims present")
        
        if claims.get("type") != "access":
            raise Unauthorised("Token is not an access token")
        
        return claims
    except ExpiredSignatureError:
        raise Unauthorised("Access token has expired")
    except:
        raise Unauthorised("Invalid authentication credentials")

async def is_authenticated(claims: Annotated[dict, Depends(get_current_account)]) -> dict:
    if not claims.get("sub"):
        raise Unauthorised("Account is not authorised")
    
    if claims.get("disabled"):
        raise Forbidden("Account has been disabled")
    
    return claims

async def is_admin_user(claims: Annotated[None, Depends(is_authenticated)]) -> None:
    if not claims.get("role") == "ADM":
        raise Forbidden("Access forbidden for current account")
