import typing
import subprocess
import json
import shutil
import functools

from multicloud import schema
from multicloud.provider.base import Cloud


AZURE_PATH = shutil.which('az')

def _run(*args, **kwargs) -> typing.Any:
    process = subprocess.run([AZURE_PATH, *args, '--output', 'json'], capture_output=True, **kwargs)
    if process.returncode != 0:
        raise ValueError(process.stdout)
    return json.loads(process.stdout)


class Azure(Cloud):
    def login(self):
        command = [AZURE_PATH, 'login']
        return command

    @staticmethod
    @functools.cache
    def identity() -> schema.CloudContext:
        data = _run('ad', 'signed-in-user', 'show')
        return schema.CloudContext(
            identity=data['mail']
        )

    @staticmethod
    @functools.cache
    def list_accounts() -> list[schema.CloudAccount]:
        data = _run('account', 'subscription', 'list')
        return [schema.CloudAccount(
            account=_['subscriptionId'],
            name=_['displayName'],
        ) for _ in data]

    @staticmethod
    @functools.cache
    def list_regions() -> list[schema.CloudRegion]:
        data = _run('account', 'list-locations')
        return [schema.CloudRegion(
            display_name=_['displayName'],
            name=_['name'],
            available=True,
        ) for _ in data]

    @staticmethod
    @functools.cache
    def list_zones() -> list[schema.CloudZone]:
        # TODO: not implemented
        return []

    @staticmethod
    @functools.cache
    def list_buckets() -> list[schema.CloudBucket]:
        # TODO: not implemented
        return []

    @staticmethod
    @functools.cache
    def list_machines() -> list[schema.CloudMachine]:
        for location in Azure.list_regions():
            data = _run('vm', 'list-sizes', '--location', location.name)
            return [schema.CloudMachine(
                name=_['name'],
                memory=_['memoryInMb'],
                cpus=_['numberOfCores'],
            ) for _ in data]

    @staticmethod
    @functools.cache
    def list_instances() -> list[schema.CloudVM]:
        for account in Azure.list_accounts():
            data = _run('vm', 'list', '--subscription', account.account)
            if len(data) != 0:
                breakpoint()
            return [schema.CloudVM(
                name=_['name'],
                memory=_['memoryInMb'],
                cpus=_['numberOfCores'],
            ) for _ in data]

    @staticmethod
    @functools.cache
    def list_kubernetes_clusters() -> list[schema.CloudKubernetesCluster]:
        kubernetes_clusters = []
        for account in Azure.list_accounts():
            data = _run('aks', 'list', '--subscription', account.account)
            if len(data) != 0:
                raise NotImplementedError()
        return kubernetes_clusters
