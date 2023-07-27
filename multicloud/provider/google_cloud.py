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
    def list_accounts() -> list[schema.CloudAccount]:
        data = _run('projects', 'list')
        return [schema.CloudAccount(
            account=_['projectId'],
            name=_['name'],
        ) for _ in data]

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
    def list_buckets() -> list[schema.CloudBucket]:
        buckets = []
        for account in GoogleCloud.list_accounts():
            if account.account.startswith('sys'):
                # google cloud generated project should be ignored
                continue

            data = _run('--project', account.account, 'storage', 'buckets', 'list')
            buckets.extend([schema.CloudBucket(
                name=_['id'],
                account=account.account
            ) for _ in data])
        return buckets

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

    @staticmethod
    @functools.cache
    def list_instances() -> list[schema.CloudVM]:
        instances = []
        for account in GoogleCloud.list_accounts():
            if account.account.startswith('sys'):
                # google cloud generated project should be ignored
                continue

            data = _run('--project', account.account, 'compute', 'instances', 'list')
            instances.extend([schema.CloudVM(
                account=account.account,
                name=_['name'],
                zone=os.path.basename(_['zone']),
                machine_name=os.path.basename(_['machineType']),
            ) for _ in data])
        return instances

    @staticmethod
    @functools.cache
    def list_kubernetes_clusters() -> list[schema.CloudKubernetesCluster]:
        kubernetes_clusters = []
        for account in GoogleCloud.list_accounts():
            data = _run('--project', account.account, 'container', 'clusters', 'list')
            for cluster in data:
                node_groups = []
                for node_group in cluster['nodePools']:
                    node_groups.append(schema.NodeGroup(
                        name=node_group['name'],
                        machine_name=node_group['config']['machineType'],
                        min_nodes=node_group.get('autoscaling', {}).get('minNodeCount', 1),
                        max_nodes=node_group.get('autoscaling', {}).get('maxNodeCount', 1),
                    ))

                kubernetes_clusters.append(schema.CloudKubernetesCluster(
                    account=account.account,
                    name=cluster['name'],
                    zone=cluster['zone'],
                    endpoint=cluster['endpoint'],
                    node_groups=node_groups,
                ))
        return kubernetes_clusters
