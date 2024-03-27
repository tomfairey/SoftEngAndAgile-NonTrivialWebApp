from pydantic import BaseModel

class BaseAccount(BaseModel):
    id: int = None
    uuid: str = None
    role: str | None = "STD"
    username: str | None = None
    name: str | None = None
    password: str | None = None
    disabled: bool | None = False
    last_modified: str | None = None

class BaseNewAccount(BaseModel):
    role: str | None = "STD"
    username: str | None = None
    name: str | None = None
    password: str | None = None
    disabled: bool | None = False

class Account:
    # On initialisation of class instance
    def __init__(
            self,
            role: str,
            username: str,
            name: str,
            password_hash: str,
            disabled: bool,
            password_last_modified: int | None = None,
            created_at: int | None = None,
            last_modified: int | None = None,
            id: int | None = None,
            uuid: str | None = None,
        ):
        self.id = id
        self.uuid = uuid
        self.role = role
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.password_last_modified = password_last_modified
        self.disabled = disabled
        self.created_at = created_at
        self.last_modified = last_modified

    # On destruction of class instance
    def __del__(self):
        pass

    def serialise(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "role": self.role,
            "username": self.username,
            "name": self.name,
            # "password_hash": "REDACTED",
            "password_last_modified": self.password_last_modified,
            "disabled": self.disabled,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }
    
    def hypermediaLinks(self, root: str = ""):
        links = []

        if self.id:
            links.append({
                "rel": "self",
                "href": f"{root}/api/v1/account/{self.id}"
            })

        return links
