import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.provider.base import Cloud


class GoogleCloud(Cloud):
    GCLOUD_PATH = shutil.which('gcloud')

    def _run_gcloud(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.GCLOUD_PATH, *args, '--format', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def identity(self) -> schema.CloudIdentity:
        data = self._run_gcloud('info')
        return schema.CloudIdentity(
            identity=data['config']['account']
        )
