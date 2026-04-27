from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc, delete, func
from sqlalchemy.orm import joinedload, Session
from typing import Annotated
from uuid import UUID
###
from oss_archive.config import ENV, Forgejo as forgejo_config
from oss_archive.utils.logger import logger
from oss_archive.database.index import get_sync_db, get_async_db
from oss_archive.database.models import Owner as OwnerModel, OSS as OSSModel
from oss_archive.database.helpers import DBQueryLimits, get_all_categories, get_all_owners, get_all_oss
from oss_archive.schemas import api as api_schemas, oss as oss_schemas
from oss_archive.seeders.index import initialize_all_seed_ops, seed_owners_oss, seed_owner_oss_from_source, mirror_oss_list
from oss_archive.seeders.json import seed_all as seed_all_json
from oss_archive.seeders.forgejo import create_org_for_mirrors, create_migrate_repo_req_body, is_oss_mirrored, mirror_oss
from oss_archive.components.ops import schema as component_schema

router = APIRouter(tags=["Operations"])

@router.post(
    "/ops/seed/init",
    status_code=status.HTTP_201_CREATED,
    response_model=api_schemas.BaseRes,
    response_model_exclude_none=True,   
)
async def seed_init(db: Annotated[Session, Depends(get_sync_db)]):
    try:
        # Maybe we can add query params to skip what we want
        _ = await initialize_all_seed_ops(db)
        return api_schemas.BaseRes(message="Seeding initialization operation is Successful")
    except Exception as e:
        logger.error("Seeding initialization operation has failed", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seeding initialization operation has failed")
