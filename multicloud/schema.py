import enum

import pydantic


class ResourceEnum(enum.Enum):
    ACCOUNTS = "accounts"
    REGIONS = "regions"
    ZONES = "zones"
    BUCKETS = "buckets"
    MACHINES = "machines"
    INSTANCES = "instances"
    KUBERNETES_CLUSTERS = "kubernetes-clusters"


class CloudContext(pydantic.BaseModel):
    identity: str
    account: str
    region: str = None


class CloudAccount(pydantic.BaseModel):
    account: str
    name: str


class CloudRegion(pydantic.BaseModel):
    display_name: str
    name: str
    available: bool


class CloudZone(pydantic.BaseModel):
    region_name: str
    name: str


class CloudBucket(pydantic.BaseModel):
    account: str
    name: str


class CloudMachine(pydantic.BaseModel):
    name: str
    description: str = None
    memory: int
    cpus: int
    zone: str = None


class CloudVM(pydantic.BaseModel):
    account: str
    name: str
    zone: str
    machine_name: str


class NodeGroup(pydantic.BaseModel):
    name: str
    machine_name: str
    min_nodes: int
    max_nodes: int


class CloudKubernetesCluster(pydantic.BaseModel):
    account: str
    name: str
    zone: str
    endpoint: str
    node_groups: list[NodeGroup]
