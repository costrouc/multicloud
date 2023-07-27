import pydantic
import rich
from rich.table import Table

def print_table(data: dict[str, list[pydantic.BaseModel]], title: str, headers: list[str] = None):
    headers = headers or [_ for _ in data[next(iter(data))][0].__fields__]
    table = Table(title=title)

    table.add_column('cloud provider')
    for header in headers:
        table.add_column(header)

    for provider_name, provider_data in data.items():
        for row in provider_data:
            table.add_row(provider_name, *[str(getattr(row, header)) for header in headers])

    return table
