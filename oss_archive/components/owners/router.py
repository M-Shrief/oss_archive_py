from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc, delete, func
from sqlalchemy.orm import joinedload, Session
from uuid import UUID
from typing import Annotated
###
from oss_archive.utils.logger import logger
from oss_archive.utils import json as json_utils
from oss_archive.database.index import get_async_db, get_sync_db
from oss_archive.database.models import Owner as OwnerModel, Category as CategoryModel
from oss_archive.database.helpers import does_owner_exists
from oss_archive.schemas import owner as owner_schemas, api as api_schemas, oss as oss_schemas
from oss_archive.components.owners import schema as component_schemas

router = APIRouter(tags=["Owners"])

@router.get(
    "/owners",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.GetAll_Res[owner_schemas.DescriptiveSchema],
    response_model_exclude_none=True
)
async def get_owners(queries: Annotated[api_schemas.SharedQueriesForGetAllRequests, Query()],db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OwnerModel).offset(queries.offset).limit(queries.limit)
        resp  = await db.scalars(statement=stmt)
        result = resp.all()
        owners: list[owner_schemas.DescriptiveSchema] =  [owner_schemas.DescriptiveSchema.model_validate(item, from_attributes=True) for item in list(result)]
        
        count = 0
        if len(owners) != 0:
            count_resp = await db.execute(select(func.count()).select_from(OwnerModel))
            count = count_resp.scalar() or 0

        return api_schemas.GetAll_Res[owner_schemas.DescriptiveSchema](data=owners, offset=queries.offset, limit=queries.limit, total_count=count)

    except Exception as e:
        logger.error("Error when getting owners", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

@router.get(
    "/owners/search",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.GetAll_Res[owner_schemas.DescriptiveSchema],
    response_model_exclude_none=True
)
async def search_owners(queries: Annotated[component_schemas.SearchOwnersQueries, Query()], db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        data_stmt = select(OwnerModel)
        count_stmt = select(func.count()).select_from(OwnerModel)

        if queries.id is not None:
            data_stmt = data_stmt.where(OwnerModel.id == queries.id)
            count_stmt = count_stmt.where(OwnerModel.id == queries.id)
        if queries.username is not None:
            data_stmt = data_stmt.where(OwnerModel.username == queries.username)
            count_stmt = count_stmt.where(OwnerModel.username == queries.username)
        if queries.priority is not None:
            data_stmt = data_stmt.where(OwnerModel.priority == queries.priority)
            count_stmt = count_stmt.where(OwnerModel.priority == queries.priority)
        if queries.type is not None:
            data_stmt = data_stmt.where(OwnerModel.type == queries.type)
            count_stmt = count_stmt.where(OwnerModel.type == queries.type)
        if queries.source is not None:
            data_stmt = data_stmt.where(OwnerModel.source == queries.source)
            count_stmt = count_stmt.where(OwnerModel.source == queries.source)

        data_stmt = data_stmt.offset(queries.offset).limit(queries.limit)  

        resp = await db.scalars(data_stmt)
        res = resp.unique().all()
        owners: list[owner_schemas.DescriptiveSchema] =  [owner_schemas.DescriptiveSchema.model_validate(item, from_attributes=True) for item in list(res)]

        count = 0
        if len(owners) != 0:
            count_resp = await db.execute(count_stmt)
            count = count_resp.scalar() or 0

        return api_schemas.GetAll_Res[owner_schemas.DescriptiveSchema](data=owners, total_count=count, offset=queries.offset, limit=queries.limit)
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner is not found!")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


@router.get(
    "/owners/{id}",
    status_code=status.HTTP_200_OK,
    response_model=component_schemas.GetOwner_Res,
    response_model_exclude_none=True
)
async def get_owner_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OwnerModel).where(OwnerModel.id == id)

        res = await db.scalars(stmt)
        owner = res.unique().one()
        return owner
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner is not found!")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


@router.post(
    path="/owners",
    status_code=status.HTTP_201_CREATED,
    response_model=component_schemas.CreatingOwner_Res,
    response_model_exclude_none=True
)
async def create_owner(owner: component_schemas.CreatingOwner_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        new_owner = OwnerModel(**owner.model_dump())
        db.add(new_owner)
        await db.commit()
        await db.refresh(new_owner)

        return new_owner

    except Exception as e:
        logger.error("Error occurred while creating owner", error=e)
        await db.rollback()
        if "psycopg.errors.UniqueViolation" in str(e):
            detail_msg = "Owner does already exists"
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail_msg)
        else:
            detail_msg = "An error occurred while creating owner, try again later."
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=detail_msg)

@router.post(
    path="/owners/many",
    status_code=status.HTTP_201_CREATED,
    response_model=component_schemas.CreateOwners_Res,
    response_model_exclude_none=True
)
async def create_owners(req_body: component_schemas.CreateOwners_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        new_owners: list[owner_schemas.FullSchema] = []
        already_exists: list[str] = []

        for owner in req_body.owners:
            does_exist = await does_owner_exists(owner.username, async_db=db)
            if does_exist:
                already_exists.append(owner.username)
                continue
            else:
                new_owner = OwnerModel(**owner.model_dump())        
                _ = db.add(new_owner)
                await db.commit()
                await db.refresh(new_owner)
                new_owners.append(owner_schemas.FullSchema.model_validate(new_owner, from_attributes=True))

        return component_schemas.CreateOwners_Res(
            new_owners=new_owners,
            already_exists=already_exists,
        )

    except Exception as e:
        logger.error("Error occurred while creating a owners", error=e)
        detail_msg = "An error occurred while creating a owners, try again later."
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=detail_msg)

@router.put(
    "/owners/json",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.Update_Res,
    response_model_exclude_none=True
)
async def sync_json(db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        json_utils.del_files(json_utils.OwnersJSONFileConfig)

        stmt = select(OwnerModel).order_by(OwnerModel.username)
        res = await db.scalars(statement=stmt)
        result = res.all()

        owners: list[owner_schemas.JSONSchema] = [owner_schemas.JSONSchema.model_validate(item, from_attributes=True) for item in list(result)]

        json_utils.write_json_files(json_utils.OwnersJSONFileConfig, owners)

        return api_schemas.Update_Res()
    except Exception as e:
        logger.error("ERROR", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

@router.put(
    "/owners/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=api_schemas.Update_Res,
    response_model_exclude_none=True
)
async def update_one(id: UUID, req_body: component_schemas.UpdatingOwner_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OwnerModel).where(OwnerModel.id == id)
        res = await db.scalars(statement=stmt)    
        existing_owner = res.unique().one()

        new_owner_data = req_body.model_dump(exclude_none=True)  # Exclude None fields from the request body

        for key, value in new_owner_data.items():
            setattr(existing_owner, key, value)

        await db.commit()
        return api_schemas.Update_Res()
        
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner is not found!")
    except Exception as e:
        logger.error("Error when updating owner", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

@router.delete(
    "/owners/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=api_schemas.Delete_Res,
    response_model_exclude_none=True
)
async def delete_one(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = delete(OwnerModel).where(OwnerModel.id == id)
        _ = await db.execute(statement=stmt)
        await db.commit()

        return api_schemas.Delete_Res()
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner is not found!")
    except Exception as e:
        logger.error("Error when deleting Owner", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")
