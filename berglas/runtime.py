import abc
import http.client
import os
from pathlib import Path
from typing import Dict

import google.auth
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from googleapiclient.http import set_user_agent

from berglas.constants import USER_AGENT
from berglas.exceptions import AutoException


class RuntimeEnv(abc.ABC):
    def _build(self, service_name: str, version: str):
        resource = discovery.build(service_name, version, cache_discovery=False)
        set_user_agent(resource._http, USER_AGENT)
        return resource

    def get_env(self) -> Dict[str, str]:
        raise NotImplementedError

    @staticmethod
    def _get_from_metadata(path: str) -> str:
        path = f"http://metadata.google.internal/computeMetadata/v1/{path}"

        http_client = discovery.build_http()
        set_user_agent(http_client, USER_AGENT)
        response, content = http_client.request(path, headers={"Metadata-Flavor": "Google", "User-Agent": USER_AGENT})
        if response.status != http.client.OK.value:
            raise AutoException(f"failed to get metadata for: {path}: {content}")

        return content.decode()


class CloudFunctionEnv(RuntimeEnv):
    def get_env(self) -> Dict[str, str]:
        name = (
            f"projects/{os.environ['X_GOOGLE_GCP_PROJECT']}/locations/{os.environ['X_GOOGLE_FUNCTION_REGION']}/"
            f"functions/{os.environ['X_GOOGLE_FUNCTION_NAME']}"
        )

        cloudfunctions_v1 = self._build("cloudfunctions", "v1")
        try:
            function = cloudfunctions_v1.projects().locations().functions().get(name=name).execute()
        except HttpError as e:
            if e.resp.status == http.client.NOT_FOUND.value:
                raise AutoException("function not found")
            elif e.resp.status == http.client.UNAUTHORIZED.value:
                raise AutoException("permission denied to fetch function info")

            raise AutoException(f"unable to fetch function: {e}")

        return function["environmentVariables"]


class CloudRunEnv(RuntimeEnv):
    def get_env(self) -> Dict[str, str]:
        revision = os.environ["K_REVISION"]

        project = self._get_from_metadata("project/project-id")
        zone = self._get_from_metadata("instance/zone")
        region = Path(zone).name[:-2]

        name = f"projects/{project}/locations/{region}/revisions/{revision}"

        cloudrun = self._build("run", "v1alpha1")
        try:
            service = cloudrun.projects().locations().revisions().get(name=name).execute()
        except HttpError as e:
            if e.resp.status == http.client.NOT_FOUND.value:
                raise AutoException("cloud run service not found")
            elif e.resp.status == http.client.UNAUTHORIZED.value:
                raise AutoException("permission denied to fetch cloud run info")

            raise AutoException(f"unable to fetch cloud run service: {e.content}")

        if "spec" not in service or "containers" not in service["spec"] or not service["spec"]["containers"]:
            raise AutoException(f"unable to get env from cloud run")

        env = service["spec"]["containers"][0]["env"]
        return {v["name"]: v["value"] for v in env}


class AppEngineEnv(RuntimeEnv):
    def get_env(self) -> Dict[str, str]:
        version = os.environ["GAE_VERSION"]
        service = os.environ["GAE_SERVICE"]

        project = self._get_from_metadata("project/project-id")

        gae = self._build("appengine", "v1")
        try:
            service_info = (
                gae.apps()
                .services()
                .versions()
                .get(appsId=project, servicesId=service, versionsId=version, view="FULL")
                .execute()
            )
        except HttpError as e:
            if e.resp.status == http.client.NOT_FOUND.value:
                raise AutoException("app engine service not found")
            elif e.resp.status == http.client.UNAUTHORIZED.value:
                raise AutoException("permission denied to fetch app engine info")

            raise AutoException(f"unable to fetch app engine service: {e.content}")

        return service_info["envVariables"]


def detect_runtime_environment() -> RuntimeEnv:
    """
    Finds the most likely runtime environment
    """
    if os.environ.get("X_GOOGLE_FUNCTION_NAME"):
        return CloudFunctionEnv()

    if os.environ.get("K_REVISION"):
        return CloudRunEnv()

    if os.environ.get("GAE_SERVICE"):
        return AppEngineEnv()

    raise AutoException("unknown runtime")
