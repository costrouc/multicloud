import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.provider.base import Cloud


class GoogleCloud(Cloud):
    GCLOUD_PATH = shutil.which('gcloud')

    def _run(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.GCLOUD_PATH, *args, '--format', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def identity(self) -> schema.CloudContext:
        data = self._run('info')
        return schema.CloudContext(
            identity=data['config']['account'],
            account=data['config']['project'],
            region='us-east-1',
        )

    def list_regions():
        data = self._run('gcloud', 'compute', 'regions', 'list')
        breakpoint()
