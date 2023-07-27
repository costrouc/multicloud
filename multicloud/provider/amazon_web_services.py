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
    def login(self):
        command = [AWS_PATH, 'configure']
        return command

    @staticmethod
    @functools.cache
    def identity() -> schema.CloudContext:
        data = _run('sts', 'get-caller-identity')
        return schema.CloudContext(
            identity=data['Arn'],
            account=data['Account'],
        )

    @staticmethod
    @functools.cache
    def list_accounts() -> list[schema.CloudAccount]:
        data = _run('organizations', 'list-accounts')
        return [schema.CloudAccount(
            account=_['Id'],
            name=_['Name'],
        ) for _ in data['Accounts']]

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
            memory=_['MemoryInfo']['SizeInMiB'],
            cpus=_['VCpuInfo']['DefaultVCpus'],
        ) for _ in data['InstanceTypes']]

    @staticmethod
    @functools.cache
    def list_buckets() -> list[schema.CloudBucket]:
        context = AmazonWebServices.identity()

        buckets = []
        for account in AmazonWebServices.list_accounts():
            env = {
                'AWS_PROFILE': 'multicloud',
            }
            subprocess.run([AWS_PATH, 'configure', 'set', 'role_arn', f'arn:aws:iam::{account.account}:role/OrganizationAccountAccessRole'], env=env)
            subprocess.run([AWS_PATH, 'configure', 'set', 'source_profile', 'default'], env=env)
            data = _run('s3api', 'list-buckets', env=env if account.account != context.account else {})
            buckets.extend([schema.CloudBucket(
                account=account.account,
                name=_['Name'],
            ) for _ in data['Buckets']])
        return buckets

    @staticmethod
    @functools.cache
    def list_instances() -> list[schema.CloudVM]:
        context = AmazonWebServices.identity()

        instances = []
        for account in AmazonWebServices.list_accounts():
            env = {
                'AWS_PROFILE': 'multicloud',
            }
            subprocess.run([AWS_PATH, 'configure', 'set', 'role_arn', f'arn:aws:iam::{account.account}:role/OrganizationAccountAccessRole'], env=env)
            subprocess.run([AWS_PATH, 'configure', 'set', 'source_profile', 'default'], env=env)
            for region in AmazonWebServices.list_regions():
                if region.available:
                    data = _run('ec2', 'describe-instances', '--region', region.name, env=env if account.account != context.account else {})
                    for reservation in data['Reservations']:
                        for instance in reservation['Instances']:
                            instances.append(schema.CloudVM(
                                account=account.account,
                                name=instance['InstanceId'],
                                zone=instance['Placement']['AvailabilityZone'],
                                machine_name=instance['InstanceType'],
                            ))
        return instances

    @staticmethod
    @functools.cache
    def list_kubernetes_clusters() -> list[schema.CloudKubernetesCluster]:
        context = AmazonWebServices.identity()

        kubernetes_clusters = []
        for account in AmazonWebServices.list_accounts():
            env = {
                'AWS_PROFILE': 'multicloud',
            }
            subprocess.run([AWS_PATH, 'configure', 'set', 'role_arn', f'arn:aws:iam::{account.account}:role/OrganizationAccountAccessRole'], env=env)
            subprocess.run([AWS_PATH, 'configure', 'set', 'source_profile', 'default'], env=env)
            for region in AmazonWebServices.list_regions():
                if region.available:
                    data = _run('eks', 'list-clusters', '--region', region.name, env=env if account.account != context.account else {})
                    for cluster_name in data['clusters']:
                        node_groups = []
                        node_group_names_data = _run('eks', 'list-nodegroups', '--cluster-name', cluster_name, '--region', region.name, env=env if account.account != context.account else {})
                        for node_group_name in node_group_names_data['nodegroups']:
                            node_group_data = _run('eks', 'describe-nodegroup', '--cluster-name', cluster_name, '--nodegroup-name', node_group_name, '--region', region.name, env=env if account.account != context.account else {})
                            node_groups.append(schema.NodeGroup(
                                name=node_group_data['nodegroup']['nodegroupName'],
                                machine_name=node_group_data['nodegroup']['instanceTypes'][0],
                                min_nodes=node_group_data['nodegroup']['scalingConfig']['minSize'],
                                max_nodes=node_group_data['nodegroup']['scalingConfig']['maxSize'],
                            ))

                        cluster = _run('eks', 'describe-cluster', '--name', cluster_name, '--region', region.name, env=env if account.account != context.account else {})
                        kubernetes_clusters.append(schema.CloudKubernetesCluster(
                            account=account.account,
                            name=cluster['cluster']['name'],
                            zone=region.name,
                            endpoint=cluster['cluster']['endpoint'],
                            node_groups=node_groups,
                        ))
        return kubernetes_clusters
