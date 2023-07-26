import enum

import pydantic


class ResourceEnum(enum.Enum):
    REGIONS = "regions"
    ZONES = "zones"
    VMS = "vms"


class CloudContext(pydantic.BaseModel):
    identity: str
    account: str
    region: str


class CloudRegion(pydantic.BaseModel):
    display_name: str
    name: str
    available: bool


class CloudZone(pydantic.BaseModel):
    region_name: str
    name: str


class CloudVM(pydantic.BaseModel):
    name: str
    description: str
    memory: int
    cpus: int
    zone: str
