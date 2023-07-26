import typer

from multicloud.provider import google_cloud, amazon_web_services, azure

cli = typer.Typer()


@cli.command()
def identity():
    gc = google_cloud.GoogleCloud()
    print('Google identity', gc.identity())

    aws = amazon_web_services.AmazonWebServices()
    print('Amazon Web Services', aws.identity())

    az = azure.Azure()
    print('Azure', az.identity())


@cli.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")
