import typer
import rich
from rich.progress import track

from multicloud.provider import google_cloud, amazon_web_services, azure
from multicloud import schema, output

cli = typer.Typer()


providers = {
    'Google Cloud': google_cloud.GoogleCloud(),
    'Amazon Web Services': amazon_web_services.AmazonWebServices(),
    'Azure': azure.Azure(),
}


@cli.command()
def identity():
    for provider_name, provider in providers.items():
        print(provider_name, 'identity', provider.identity())


@cli.command(name="list")
def _list(resource: schema.ResourceEnum):
    resource_map = {
        schema.ResourceEnum.REGIONS: 'list_regions',
        schema.ResourceEnum.ZONES: 'list_zones',
        schema.ResourceEnum.MACHINES: 'list_machines',
        schema.ResourceEnum.ACCOUNTS: 'list_accounts',
        schema.ResourceEnum.INSTANCES: 'list_instances',
        schema.ResourceEnum.KUBERNETES_CLUSTERS: 'list_kubernetes_clusters',
        schema.ResourceEnum.BUCKETS: 'list_buckets',
    }

    if resource not in resource_map:
        print('resource', resource, 'not recognized')
        typer.Abort(1)

    results = {}
    for provider_name, provider in track(providers.items(), description=f"Collecting {resource.value}"):
        results[provider_name] = getattr(provider, resource_map[resource])()

    table = output.print_table(results, title=resource.value)
    rich.print(table)
