from sqlalchemy.orm import Session
from sqlalchemy import select, exc 
from sqlalchemy.ext.asyncio import AsyncSession
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


async def get_all_categories(async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(CategoryModel).order_by(CategoryModel.priority)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            categories = res.all()
            return categories
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            categories = res.all()
            return categories
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all owners", error=e)
        return None


async def get_all_owners(async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OwnerModel).order_by(OwnerModel.priority)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            owners = res.all()
            return owners
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            owners = res.all()
            return owners
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all owners", error=e)
        return None

async def get_all_oss(async_db: AsyncSession | None = None, sync_db: Session | None = None):
    """Note: You have to pass async_db or sync_db, if you didn't it'll return None"""
    try:
        stmt = select(OSSModel).order_by(OSSModel.priority)
        if async_db is not None:
            res = await async_db.scalars(statement=stmt)
            oss_list = res.all()
            return oss_list
        elif sync_db is not None:
            res = sync_db.scalars(statement=stmt)
            oss_list = res.all()
            return oss_list
        else:
            return None
    except Exception as e:
        logger.error("Unknown error getting all OSS", error=e)
        return None