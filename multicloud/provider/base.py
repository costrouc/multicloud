import enum

from multicloud import schema


class ResourceEnum(enum.Enum):
    REGION = "region"


class Cloud:
    def identity(self) -> schema.CloudContext:
        pass

    def login(self) -> list[str]:
        pass

    def list_regions(self) -> list[str]:
        pass
