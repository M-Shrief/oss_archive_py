from httpx import Timeout
###
from oss_archive.config import Forgejo
from oss_archive.utils import httpx
from oss_archive.utils.logger import logger
from oss_archive.components.forgejo.schema import ForgejoRepo, MigrateRepoReqBody
from oss_archive.components.forgejo.shared import base_headers


async def migrate_repo(repo_data: MigrateRepoReqBody):
    try:
        result = await httpx.async_post(
            base_url=Forgejo.get("base_url") or "",
            endpoint="/repos/migrate",
            body=repo_data.model_dump(mode="json"),
            headers=base_headers,
            timeout=Timeout(timeout=None, connect=10.0)
        )

        if result is None:
            logger.error("Unknown error calling Forgejo's POST /repos/migrate", repo_data=repo_data)
            return
        
        if result.status_code != 201:
            logger.error("Failed migrating the repo", result=result)
            return

        logger.info("Migrated the repo successfully", repo=repo_data)
        return 
    
    except Exception as e:
        logger.error("Unknown error mirgrating repo", repo_data=repo_data, error=e)
        return
