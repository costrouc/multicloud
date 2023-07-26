import pydantic


class CloudContext(pydantic.BaseModel):
    identity: str
    account: str
    region: str
