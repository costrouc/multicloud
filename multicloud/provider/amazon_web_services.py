import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.provider.base import Cloud


class AmazonWebServices(Cloud):
    AWS_PATH = shutil.which('aws')

    def __init__(self):
        data = self._run_aws('sts', 'get-caller-identity')
        self.account_id: str = data['Account']
        self.user_arn: str = data['Arn']

    def _run_aws(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.AWS_PATH, *args, '--output', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def identity(self) -> schema.CloudIdentity:
        return schema.CloudIdentity(
            email=self.user_arn
        )
