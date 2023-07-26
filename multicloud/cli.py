import typer

from multicloud.provider import google_cloud

cli = typer.Typer()


@cli.command()
def hello(name: str):
    google_cloud.get_identity()
    print(f"Hello {name}")


@cli.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")
