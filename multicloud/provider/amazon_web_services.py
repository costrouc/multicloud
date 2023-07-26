import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.provider.base import Cloud


class AmazonWebServices(Cloud):
    AWS_PATH = shutil.which('aws')

    def __init__(self):
        data = self._run('sts', 'get-caller-identity')
        self.account_id: str = data['Account']
        self.user_arn: str = data['Arn']

    def _run(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.AWS_PATH, *args, '--output', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def login(self):
        command = [self.AWS_PATH, 'configure']
        return command

    def identity(self) -> schema.CloudContext:
        return schema.CloudContext(
            identity=self.user_arn
        )
