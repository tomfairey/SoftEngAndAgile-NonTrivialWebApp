import math
import time
import uuid
from jose import jwt
from typing import Annotated

from ..models.account import Account

class AuthorisationAdapter:
    # On initialisation of class instance
    def __init__(self, algorithm: Annotated[str, "Algorithm to use for the JWTs"], secret: Annotated[str, "Secret to use for the JWTs"]):
        self.__algorithm__ = algorithm
        self.__secret__ = secret

    # On destruction of class instance
    def __del__(self):
        pass

    def encode(self, claims: dict, validTime: Annotated[int, "Seconds the token will be valid for"] = 1200) -> str:
        time_now = math.floor(time.time())

        claims = {
            **claims,
            "iat": time_now,
            "nbf": time_now,
            "exp": time_now + validTime
        }

        return jwt.encode(claims = claims, key = self.__secret__, algorithm = self.__algorithm__)
    
    # Generate an access token for an account (2 minute life)
    def generateAccessToken(self, account: Account, id: str) -> str:
        return self.encode({
                "sub": str(account.id),
                "name": account.name,
                "role": account.role,
                "disabled": account.disabled,
                "jti": id,
                "type": "access",
            }, 120)
    
    # Generate a refresh token for an account (4 day life)
    def generateRefreshToken(self, account: Account, id: str) -> str:
        return self.encode({
                # "sub": f"{account.id}|{account.uuid}",
                "sub": str(account.id),
                "jti": id,
                "type": "refresh",
            }, 345600)
    
    def generateCurrentJTI(self, account: Account) -> tuple:
        accountUUID = uuid.UUID(account.uuid)
        id = str(uuid.uuid5(accountUUID, str(account.id)))

        return id
    
    def generateTokenPair(self, account: Account) -> tuple:
        id = self.generateCurrentJTI(account)

        return (
            self.generateAccessToken(account, id),
            self.generateRefreshToken(account, id),
        )
    
    def decode(self, token: str) -> dict:
        return jwt.decode(token = token, key = self.__secret__, algorithms = self.__algorithm__)
    
    def decode_ignore_expiry(self, token: str) -> dict:
        return jwt.decode(token = token, key = self.__secret__, algorithms = self.__algorithm__, options={ 'verify_exp': False })
