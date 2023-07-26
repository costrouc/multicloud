import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.base import Cloud


class AmazonWebServices(Cloud):
    AWS_PATH = shutil.which('aws')

    def _run_aws(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.AWS_PATH, *args, '--format', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def identity(self) -> schema.CloudIdentity:
        breakpoint()
        data = self._run_aws('info')
        return schema.CloudIdentity(
            email=data['config']['account']
        )
