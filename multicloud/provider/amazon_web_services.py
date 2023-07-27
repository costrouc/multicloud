import typing
import subprocess
import json
import shutil
import functools

from multicloud import schema
from multicloud.provider.base import Cloud


AWS_PATH = shutil.which('aws')


def _run(*args, **kwargs) -> typing.Any:
    process = subprocess.run([AWS_PATH, *args, '--output', 'json'], capture_output=True, **kwargs)
    if process.returncode != 0:
        raise ValueError(process.stdout)
    return json.loads(process.stdout)


class AmazonWebServices(Cloud):
    def __init__(self):
        data = _run('sts', 'get-caller-identity')
        self.account_id: str = data['Account']
        self.user_arn: str = data['Arn']

    def login(self):
        command = [AWS_PATH, 'configure']
        return command

    def identity(self) -> schema.CloudContext:
        return schema.CloudContext(
            identity=self.user_arn
        )

    @staticmethod
    @functools.cache
    def list_regions() -> list[schema.CloudRegion]:
        data = _run('account', 'list-regions')
        return [schema.CloudRegion(
            display_name=_['RegionName'],
            name=_['RegionName'],
            available=_["RegionOptStatus"] != "DISABLED",
        ) for _ in data['Regions']]

    @staticmethod
    @functools.cache
    def list_zones() -> list[schema.CloudZone]:
        zones = []
        for region in AmazonWebServices.list_regions():
            if region.available:
                data = _run('ec2', 'describe-availability-zones', '--region', region.name)
                zones.extend([schema.CloudZone(region_name=region.name, name=_['ZoneName']) for _ in data['AvailabilityZones']])
        return zones

    @staticmethod
    @functools.cache
    def list_machines() -> list[schema.CloudMachine]:
        data = _run('ec2', 'describe-instance-types')
        return [schema.CloudMachine(
            name=_['InstanceType'],
            memory=_['MemoryInfo']['sizeInMiB'],
            cpus=_['VCpuInfo']['DefaultVCpus'],
        ) for _ in data['InstanceTypes']]
