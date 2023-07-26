import pydantic


class CloudIdentity(pydantic.BaseModel):
    identity: str
