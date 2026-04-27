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

@router.post(
    "/ops/seed/json",
    status_code=status.HTTP_201_CREATED,
    response_model=api_schemas.BaseRes,
    response_model_exclude_none=True,   
)
async def seed_json(db: Annotated[Session, Depends(get_sync_db)]):
    try:
        _ = await seed_all_json(db)
        return api_schemas.BaseRes(message="Operation is completed.")
    except Exception as e:
        logger.error("Couldn't seed all JSON files", error=e)
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail="Error: Couldn't seed all JSON files, try again later!")


@router.post(
    "/ops/seed/category_owners/{category_key}",
    status_code=status.HTTP_201_CREATED,
    response_model=api_schemas.BaseRes,
    response_model_exclude_none=True,   
)
async def seed_category_owners(category_key: str, queries: Annotated[DBQueryLimits, Query()] ,db: Annotated[Session, Depends(get_sync_db)]):
    try:
        owners = await get_all_owners(category_key=category_key, query_limits=queries, sync_db=db)
        if owners is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Couldn't get owners by {category_key} category, try again later.")
        elif len(owners) == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Couldn't get any owners by the selected category")

        for owner in owners:
            logger.info(f"Owner: {owner.username}")
        # _ = seed_owners_oss(owners, db)

        return api_schemas.BaseRes(message=f"Seeded all owners in {category_key} category")

    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise e
        logger.error(f"Couldn't seed owners by {category_key} category", error=e)
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=f"Error: Couldn't seed owners by {category_key} category, try again later!")



@router.post(
    "/ops/seed/owner_oss/{owner_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=list[oss_schemas.MinimalSchema],
    response_model_exclude_none=True,   
)
async def seed_owner_oss(owner_id: UUID, db: Annotated[Session, Depends(get_sync_db)]):
    try:
        stmt = select(OwnerModel).where(OwnerModel.id == owner_id)

        res = db.scalars(stmt)
        owner = res.unique().one()

        owner_oss = await seed_owner_oss_from_source(owner, db)
        if owner_oss is  None:
            logger.error(f"Couldn't seed Owner: {owner.name} OSS from source: {owner.source}")
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Couldn't seed Owner's OSS")

        return owner_oss
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner is not found!")
    except Exception:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Couldn't seed Owner's OSS")
