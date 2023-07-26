import typer

from multicloud.provider import google_cloud, amazon_web_services, azure
from multicloud import schema

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
        schema.ResourceEnum.VMS: 'list_vms',
    }

    if resource not in resource_map:
        print('resource', resource, 'not recognized')
        typer.Abort(1)

    for provider_name, provider in providers.items():
        print(provider_name, resource.value, getattr(provider, resource_map[resource])())


@cli.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")
