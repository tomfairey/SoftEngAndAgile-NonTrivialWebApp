from pydantic import BaseModel

class BaseOperatingCompany(BaseModel):
    id: int = None
    noc: str = None
    short_code: str | None = None
    name: str | None = None

class BaseNewOperatingCompany(BaseModel):
    noc: str = None
    short_code: str | None = None
    name: str | None = None

class OperatingCompany:
    # On initialisation of class instance
    def __init__(self, id: int | None, noc: str, short_code: str | None = None, name: str | None = None):
        self.id = id
        self.noc = noc
        self.short_code = short_code
        self.name = name

    # On destruction of class instance
    def __del__(self):
        pass

    def serialise(self):
        return {
            "id": self.id,
            "noc": self.noc,
            "short_code": self.short_code,
            "name": self.name
        }
    
    def hypermediaLinks(self, root: str = ""):
        links = []

        if self.id:
            links.append({
                "rel": "self",
                "href": f"{root}/api/v1/operating-company/{self.id}"
            })

        return links
