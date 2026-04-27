from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, exc 
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from pydantic import BaseModel, Field
### 
from oss_archive.utils.logger import logger
from oss_archive.database.models import  Category as CategoryModel, Owner as OwnerModel, OSS as OSSModel

async def does_category_exists(category_key: str, async_db: AsyncSession | None = None, sync_db: Session | None = None) -> bool | None:
    """check if category exists, if result is None then there was unknown error.
    Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(CategoryModel).where(CategoryModel.key == category_key)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        else:
            return None
    except exc.NoResultFound:
        return False
    except Exception as e:
        logger.error("Error checking category existence", category_key=category_key, error=e)
        return None

async def does_owner_exists(owner_username: str, async_db: AsyncSession | None = None, sync_db: Session | None = None) -> bool | None:
    """check if owner exists, if result is None then there was unknown error.
    Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OwnerModel).where(OwnerModel.username == owner_username)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        else:
            return None
    except exc.NoResultFound:
        return False
    except Exception as e:
        logger.error("Error checking owner existence", owner_username=owner_username, error=e)
        return None

async def does_oss_exists(oss_fullname: str, async_db: AsyncSession | None = None, sync_db: Session | None = None) -> bool | None:
    """check if OSS exists, if result is None then there was unknown error.
    Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OSSModel).where(OSSModel.fullname == oss_fullname)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            _ = res.one() # if it exists in won't raise an error
            return True
        else:
            return None
    except exc.NoResultFound:
        return False
    except Exception as e:
        logger.error("Error checking OSS existence", oss_fullname=oss_fullname, error=e)
        return None

class DBQueryLimits(BaseModel):
    limit: Annotated[int, Field(default=10, gt=0, le=100)]
    offset: Annotated[int, Field(default=0, ge=0)]

async def get_all_categories(with_owners: bool = False, with_oss: bool = False, query_limits: DBQueryLimits | None = None, async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(CategoryModel).order_by(CategoryModel.priority)
        if with_owners:
            stmt = stmt.options(joinedload(CategoryModel.owners).load_only(OwnerModel.id, OwnerModel.username, OwnerModel.priority, OwnerModel.reviewed))
        if with_oss:
            stmt = stmt.options(joinedload(CategoryModel.main_oss).load_only(OSSModel.id, OSSModel.fullname, OSSModel.priority, OSSModel.is_mirrored))

        if query_limits is not None:
            stmt = stmt.offset(query_limits.offset).limit(query_limits.limit)
        
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            categories = res.unique().all()
            return categories
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            categories = res.unique().all()
            return categories
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all owners", error=e)
        return None


async def get_all_owners(category_key: str | None = None, with_oss: bool = False, query_limits: DBQueryLimits | None = None, async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OwnerModel).order_by(OwnerModel.priority)
        if category_key is not None:
            stmt = stmt.where(OwnerModel.main_category_key == category_key)
        if with_oss:
            stmt = stmt.options(joinedload(OwnerModel.owned_oss).load_only(OSSModel.id, OSSModel.fullname, OSSModel.priority, OSSModel.is_mirrored))
        
        if query_limits is not None:
            stmt = stmt.offset(query_limits.offset).limit(query_limits.limit)
        
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            owners = res.unique().all()
            return owners
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            owners = res.unique().all()
            return owners
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all owners", error=e)
        return None

async def get_all_oss(category_key: str | None = None, owner_username: str | None = None, query_limits: DBQueryLimits | None = None, async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OSSModel).order_by(OSSModel.priority)
        if owner_username is not None: # if owner is specified, then we don't need to care about main_category_key
            stmt = stmt.where(OSSModel.owner_username == owner_username)
        if category_key is not None:
            stmt = stmt.where(OSSModel.main_category_key == category_key)
        
        if query_limits is not None:
            stmt = stmt.offset(query_limits.offset).limit(query_limits.limit)
        

        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            oss_list = res.unique().all()
            return oss_list
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            oss_list = res.unique().all()
            return oss_list
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all OSS", error=e)
        return None