import pydantic


class CloudIdentity(pydantic.BaseModel):
    email: str
