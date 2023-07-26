import typer

from multicloud.provider import google_cloud, amazon_web_services, azure, base

cli = typer.Typer()


providers = {
    'Google Cloud': google_cloud.GoogleCloud(),
    'Amazon Web Services': amazon_web_services.AmazonWebServices(),
    'Azure': azure.Azure(),
}


@cli.command()
def identity():
    for provider_name, provider in providers:
        print(provider_name, 'identity', provider.identity())


@cli.command()
def list(resource: str):
    if resource == base.ResourceEnum.REGION:
        for provider_name, provider in providers:
            print(provider_name, 'region', provider.list_region())


@cli.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")
