import os
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

from ..modules.application import application_read
from ..models.authorisation import AuthorisationAdapter
from ..models.errors import Unauthorised
    
jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
jwt_secret = os.environ.get("JWT_SECRET", None)

if not jwt_secret:
    raise Exception("$JWT_SECRET is required and must be specified!")

authorisation = AuthorisationAdapter(jwt_algorithm, jwt_secret)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/authorisation/token")

router = APIRouter(prefix="/authorisation")

async def get_current_account_ignore_expiry(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    claims = authorisation.decode_ignore_expiry(token)

    if not claims or claims["type"] != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims

@router.post("/token", tags=["authorisation"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        account = application_read.getAccount(username = form_data.username)

        if not account:
            raise Unauthorised("Incorrect username")
        
        passwordMatches = application_read.matchAccountPassword(account = account, password = form_data.password)

        if not passwordMatches:
            raise Unauthorised("Incorrect password")
    except:
        # Don't confirm existence of an account to the user, for security reasons this is reset to a generic message
        raise Unauthorised("Incorrect username or password")
    
    accessToken, refreshToken = application_read.generateTokenPairForAccount(account, authorisation)

    return {"access_token": accessToken, "refresh_token": refreshToken, "token_type": "bearer"}

@router.post("/refresh", tags=["authorisation"])
async def refresh(current_account: Annotated[dict, Depends(get_current_account_ignore_expiry)], refresh_token: Annotated[str, Form(), "Refresh token"]):
    refresh_claims = authorisation.decode(refresh_token)

    if refresh_claims["type"] != "refresh":
        raise Unauthorised("Ensure provided token is a refresh token...")

    # Ensure token are of same pair, token ID is generated from account ID and current account UUID
    # This ties tokens to a particular account and current account UUID, see ../models/authorisation:generateTokenPair() for generation logic
    if current_account["jti"] != refresh_claims["jti"]:
        raise Unauthorised("Access/refresh pair mismatch!")
    
    # Query account data by account ID
    account = application_read.getAccount(id = refresh_claims["sub"])

    # Ensure the account UUID has not changed, otherwise refresh token is no longer valid
    if authorisation.generateCurrentJTI(account) != refresh_claims["jti"]:
        raise Unauthorised("Token no longer valid!")
    
    accessToken, refreshToken = application_read.generateTokenPairForAccount(account, authorisation)

    return {"access_token": accessToken, "refresh_token": refreshToken, "token_type": "bearer"}

@router.get("/claims", tags=["authorisation"])
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return authorisation.decode(token)
