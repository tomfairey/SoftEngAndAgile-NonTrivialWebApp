from pydantic import BaseModel

class BaseVehicle(BaseModel):
    fleet_no: int | str
    opco_id: int

class Vehicle:
    # On initialisation of class instance
    def __init__(self, fleet_no, opco_id):
        self.fleet_no = fleet_no
        self.opco_id = opco_id

    # On destruction of class instance
    def __del__(self):
        pass

    def serialise(self):
        return {
            "fleet_no": self.fleet_no,
            "opco_id": self.opco_id
        }
    
    def hypermediaLinks(self, root: str = ""):
        links = []

        if self.fleet_no:
            links.append({
                "rel": "self",
                "href": f"{root}/api/v1/vehicle/{self.fleet_no}"
            })

        if self.opco_id:
            links.append({
                "rel": "operatingCompany",
                "href": f"{root}/api/v1/operating-company/{self.opco_id}"
            })

        return links
