""" This module is used to seed Forgejo's instance, meaning:
it's used to use the OSS data in our database, to add new mirrored repos to the Forgejo's instance.
"""
from httpx import Timeout
###
from oss_archive.config import Forgejo as forgejo_config, API as api_config
from oss_archive.utils import httpx
from oss_archive.utils.logger import logger
from oss_archive.database.models import OSS as OSSModel
from oss_archive.components.forgejo.shared import base_headers
from oss_archive.components.forgejo.schema import MigrateRepoReqBody, ServiceEnum

DEFAULT_MIRROR_INTERVAL = "168h0m0s"

async def create_org_for_mirrors() -> bool:
    try:
        admin_username = forgejo_config.get("admin_username")
        org_for_mirrors = forgejo_config.get("org_for_mirrors")

        get_org_result = await httpx.async_get(
            base_url=forgejo_config.get("base_url") or "",
            endpoint=F"/orgs/{org_for_mirrors}",
            headers=base_headers
            )

        if get_org_result is None or get_org_result.status_code != 200:
            request_body = {"username": org_for_mirrors}
            create_org_result = await httpx.async_post(
                base_url=forgejo_config.get("base_url") or "",
                endpoint=f"/admin/users/{admin_username}/orgs",
                body=request_body,
                headers=base_headers
            ) 

            if create_org_result is None or create_org_result.status_code != 201:
                return False

            return True
        else: # it already exists
            return True

    except Exception as e:
        logger.error("Unknown error creating Organization to mirrored OSS", error=e)
        return False

async def is_oss_mirrored(oss_fullname: str):
    try:
        get_repo_res = await httpx.async_get(
            base_url=forgejo_config.get("base_url") or "",
            endpoint=f"/repos/{forgejo_config.get("org_for_mirrors")}/{oss_fullname}",
            headers=base_headers
        )

        if get_repo_res is None or get_repo_res.status_code != 200:
            return False
        else: # it's mirrored
            return True

    except Exception as e:
        logger.error("Unknown error checking if OSS is mirrored", oss_fullname=oss_fullname, error=e)
        return False

async def mirror_oss(oss_data: MigrateRepoReqBody):
    try:
        # Calling our API's which starts the task queue from FastAPI, 
        # and doesn't wait for Forgejo's response.
        mirror_response = await httpx.async_post(
            base_url=api_config.get("base_url") or "",
            endpoint="/forgejo/repos/migrate",
            body=oss_data.model_dump(mode="json"),
            headers=base_headers,
            timeout=Timeout(timeout=None, connect=10.0)
            )

        # Calling Forgejo's instance directly, and wait for the response
        
        # mirror_response = await httpx.async_post(
        #     base_url=forgejo_config.get("base_url") or "",
        #     endpoint="/repos/migrate",
        #     body=oss_data.model_dump(mode="json"),
        #     headers=base_headers,
        #     timeout=Timeout(timeout=None, connect=10.0)
        #     )

        if mirror_response is None or mirror_response.status_code != 201:
            return False
        else:
            return True
        
    except Exception as e:
        logger.error("Unknown error mirroring OSS", oss_data=oss_data, error=e)
        return False

def create_migrate_repo_req_body(oss: OSSModel, org_for_mirrors: str) -> MigrateRepoReqBody | None:
    """ return a MigrateRepoBody using git as it's service.
    
    if no git's clone_url is provided, it returns None."""
    if oss.clone_url is None:
        logger.info("Failed to mirror OSS, as it's clone_url doesn't exists", oss_fullname=oss.fullname)
        return None

    return MigrateRepoReqBody(   
        clone_addr=oss.clone_url,
        repo_name=oss.fullname,
        repo_owner=org_for_mirrors,
        service=ServiceEnum.git,
        mirror=True,
        mirror_interval=DEFAULT_MIRROR_INTERVAL
    )
