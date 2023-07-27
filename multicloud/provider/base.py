from multicloud import schema


class Cloud:
    def identity(self) -> schema.CloudContext:
        pass

    def login(self) -> list[str]:
        pass

    def list_accounts(self) -> list[schema.CloudAccount]:
        pass

    def list_regions(self) -> list[schema.CloudRegion]:
        pass

    def list_zones(self) -> list[schema.CloudZone]:
        pass

    def list_buckets() -> list[schema.CloudBucket]:
        pass

    def list_machines(self) -> list[schema.CloudMachine]:
        pass

    def list_instances() -> list[schema.CloudVM]:
        pass

    def list_kubernetes_clusters(self) -> list[schema.CloudKubernetesCluster]:
        pass
