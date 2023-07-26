import typing
import subprocess
import json
import shutil

from multicloud import schema
from multicloud.provider.base import Cloud


class Azure(Cloud):
    AZURE_PATH = shutil.which('az')

    def _run(self, *args, **kwargs) -> typing.Any:
        process = subprocess.run([self.AZURE_PATH, *args, '--output', 'json'], capture_output=True, **kwargs)
        if process.returncode != 0:
            raise ValueError(process.stdout)
        return json.loads(process.stdout)

    def login(self):
        command = [self.AZURE_PATH, 'login']
        return command

    def identity(self) -> schema.CloudContext:
        data = self._run('ad', 'signed-in-user', 'show')
        return schema.CloudContext(
            identity=data['mail']
        )
