from multicloud import schema

class Cloud:
    def identity(self) -> schema.CloudIdentity:
        pass

    def login(self) -> list[str]:
        pass
