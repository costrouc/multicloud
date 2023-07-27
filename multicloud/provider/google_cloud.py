import typing
import subprocess
import json
import os
import shutil
import functools

from multicloud import schema
from multicloud.provider.base import Cloud


GCLOUD_PATH = shutil.which('gcloud')

def _run(*args, **kwargs) -> typing.Any:
    process = subprocess.run([GCLOUD_PATH, *args, '--format', 'json'], capture_output=True, **kwargs)
    if process.returncode != 0:
        raise ValueError(process.stdout)
    return json.loads(process.stdout)


class GoogleCloud(Cloud):
    @staticmethod
    @functools.cache
    def identity(self) -> schema.CloudContext:
        data = _run('info')
        return schema.CloudContext(
            identity=data['config']['account'],
            account=data['config']['project'],
            region='us-east-1',
        )

    @staticmethod
    @functools.cache
    def list_regions() -> list[schema.CloudRegion]:
        data = _run('compute', 'regions', 'list')
        return [schema.CloudRegion(
            display_name=_['description'],
            name=_['name'],
            available=_['status'] == 'UP',
        ) for _ in data]

    @staticmethod
    @functools.cache
    def list_zones() -> list[schema.CloudZone]:
        data = _run('compute', 'zones', 'list')
        return [schema.CloudZone(region_name=os.path.basename(_['region']), name=_['name']) for _ in data]

    @staticmethod
    @functools.cache
    def list_machines() -> list[schema.CloudMachine]:
        data = _run('compute', 'machine-types', 'list')
        return [schema.CloudMachine(
            name=_['name'],
            description=_['description'],
            memory=_['memoryMb'],
            cpus=_['guestCpus'],
            zone=_['zone'],
        ) for _ in data]
