import subprocess
import json
import shutil

from multicloud import schema


GCLOUD_PATH = shutil.which('gcloud')


def run_gcloud(*args, **kwargs):
    process = subprocess.run([GCLOUD_PATH, *args], **kwargs)
    return process.stdout


def get_identity() -> schema.CloudIdentity:
    breakpoint()
