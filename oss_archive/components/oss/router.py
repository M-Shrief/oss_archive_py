from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc, delete, func
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Annotated, Literal
###
from oss_archive.database.index import get_async_db
from oss_archive.database.models import OSS as OSSModel
from oss_archive.database.helpers import does_oss_exists
from oss_archive.utils.logger import logger
from oss_archive.components.oss import schema as component_schemas
from oss_archive.schemas import oss as oss_schemas, api as api_schemas
# from oss_archive.utils import git, tarfile, paths
from oss_archive.utils import formatter, json as json_utils

router = APIRouter(tags=["OSS"])

@router.get(
    "/oss",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.GetAll_Res[oss_schemas.DescriptiveSchema],
    response_model_exclude_none=True,
)
async def get_all_oss(queries: Annotated[api_schemas.SharedQueriesForGetAllRequests, Query()], db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OSSModel, func.count().over().label('total')).offset(queries.offset).limit(queries.limit)
        resp  = await db.execute(statement=stmt)
        result = resp.all()

        total_count: int = result[1].total if result else 0 
        all_oss: list[oss_schemas.DescriptiveSchema] =  [oss_schemas.DescriptiveSchema.model_validate(item[0], from_attributes=True) for item in list(result)]

        return api_schemas.GetAll_Res[oss_schemas.DescriptiveSchema](data=all_oss, offset=queries.offset, limit=queries.limit, total_count=total_count)
    except Exception as e:
        logger.error("Error when getting all OSS", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

@router.get(
    "/oss/search",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.GetAll_Res[oss_schemas.DescriptiveSchema],
    response_model_exclude_none=True
)
async def search_oss(queries: Annotated[component_schemas.SearchOSSQueries, Query()], db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OSSModel, func.count().over().label('total'))
        if queries.id is not None:
            stmt = stmt.where(OSSModel.id == queries.id)
        if queries.repo_name is not None:
            stmt = stmt.where(OSSModel.repo_name == queries.repo_name)
        if queries.fullname is not None:
            stmt = stmt.where(OSSModel.fullname == queries.fullname)
        if queries.owner_username is not None:
            stmt = stmt.where(OSSModel.owner_username == queries.owner_username)
        if queries.category_key is not None:
            stmt = stmt.where(OSSModel.main_category_key == queries.category_key)
        if queries.priority is not None:
            stmt = stmt.where(OSSModel.priority == queries.priority)
        if queries.is_mirrored is not None:
            stmt = stmt.where(OSSModel.is_mirrored == queries.is_mirrored)
        if queries.development_status is not None:
            stmt = stmt.where(OSSModel.development_status == queries.development_status)


        stmt = stmt.offset(queries.offset).limit(queries.limit)  
        
        resp  = await db.execute(statement=stmt)
        result = resp.unique().all()

        total_count: int = result[1].total if result else 0 
        all_oss: list[oss_schemas.DescriptiveSchema] =  [oss_schemas.DescriptiveSchema.model_validate(item[0], from_attributes=True) for item in list(result)]

        return api_schemas.GetAll_Res[oss_schemas.DescriptiveSchema](data=all_oss, total_count=total_count, offset=queries.offset, limit=queries.limit)

    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
    except Exception as e:
        logger.error("Error when getting OSS by id", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


@router.get(
    "/oss/{id}",
    status_code=status.HTTP_200_OK,
    response_model=component_schemas.GetOSS_Res,
    response_model_exclude_none=True
)
async def get_oss_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OSSModel).where(OSSModel.id == id)
        res = await db.scalars(statement=stmt)
        oss = res.unique().one()
        return oss
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
    except Exception as e:
        logger.error("Error when getting OSS by id", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

@router.post(
    path="/oss/",
    status_code=status.HTTP_201_CREATED,
    response_model=component_schemas.CreateOSS_Res,
    response_model_exclude_none=True
)
async def create_oss(oss: component_schemas.CreateOSS_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        new_oss = OSSModel(**oss.model_dump())
        new_oss.fullname = formatter.format_oss_fullname(oss.owner_username, oss.repo_name)
        db.add(new_oss)
        await db.commit()
        await db.refresh(new_oss)

        return new_oss

    except Exception as e: ## need effective error handling here
        logger.error("Error when creating OSS", error=e)
        await db.rollback()
        if "psycopg.errors.UniqueViolation" in str(e):
            detail_msg = "OSS's name already exists"
            raise HTTPException(status.HTTP_409_CONFLICT, detail=detail_msg)
        else:
            detail_msg = "An error occurred while signing up, try again later."
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=detail_msg)

@router.post(
    path="/oss/many",
    status_code=status.HTTP_201_CREATED,
    response_model=component_schemas.CreateManyOSS_Res,
    response_model_exclude_none=True
)
async def create_many_oss(req_body: component_schemas.CreateManyOSS_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        new_oss_list: list[oss_schemas.FullSchema] = []
        already_exists: list[str] = []

        for oss in req_body.oss_list:
            oss_fullname = formatter.format_oss_fullname(oss.owner_username, oss.repo_name)
            does_exist = await does_oss_exists(oss_fullname, db)
            if does_exist:
                already_exists.append(oss_fullname)
                continue
            else:
                new_oss = OSSModel(**oss.model_dump())    
                new_oss.fullname = oss_fullname    
                _ = db.add(new_oss)
                await db.commit()
                await db.refresh(new_oss)
                new_oss_list.append(oss_schemas.FullSchema.model_validate(new_oss, from_attributes=True))

        return component_schemas.CreateManyOSS_Res(
            new_oss_list=new_oss_list,
            already_exists=already_exists,
        )

    except Exception as e:
        logger.error("Error occurred while creating many OSS", error=e)
        detail_msg = "An error occurred while creating many OSS, try again later."
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail=detail_msg)


@router.put(
    "/oss/json",
    status_code=status.HTTP_200_OK,
    response_model=api_schemas.Update_Res,
    response_model_exclude_none=True
)
async def sync_json(db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        json_utils.del_files(json_utils.OSSJSONFileConfig)

        stmt = select(OSSModel).order_by(OSSModel.fullname)
        res = await db.scalars(statement=stmt)
        result = res.all()

        oss_list: list[oss_schemas.JSONSchema] = [oss_schemas.JSONSchema.model_validate(item, from_attributes=True) for item in list(result)]

        json_utils.write_json_files(json_utils.OSSJSONFileConfig, oss_list)

        return api_schemas.Update_Res()
    except Exception as e:
        logger.error("ERROR", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


@router.put(
    "/oss/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=api_schemas.Update_Res,
    response_model_exclude_none=True
)
async def update_one(id: UUID, req_body: component_schemas.UpdateOSS_Req, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = select(OSSModel).where(OSSModel.id == id)
        res = await db.scalars(statement=stmt)    
        existing_oss = res.unique().one()

        new_oss_data = req_body.model_dump(exclude_none=True)  # Exclude None fields from the request body

        for key, value in new_oss_data.items():
            setattr(existing_oss, key, value)

        await db.commit()
        return api_schemas.Update_Res()
        
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
    except Exception as e:
        logger.error("Error when updating category", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


@router.delete(
    "/oss/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=api_schemas.Delete_Res,
    response_model_exclude_none=True
)
async def delete_one(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        stmt = delete(OSSModel).where(OSSModel.id == id)
        _ = await db.execute(statement=stmt)
        await db.commit()

        return api_schemas.Delete_Res()
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
    except Exception as e:
        logger.error("Error when deleting OSS", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")



### For testing utilites, most likely we won't expose them in production.
# @router.get(
#     "/oss/{id}/git",
#     status_code=status.HTTP_200_OK,
#     # response_model=OSSoftwareSchema,
#     response_model_exclude_none=True,
#     description="Gets OSS's git configurations"
# )
# async def oss_git_info_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
#     try:
#         stmt = select(OSSoftwareModel).options(joinedload(OSSoftwareModel.meta_list).load_only(MetaList.key, MetaList.name)).options(joinedload(OSSoftwareModel.meta_item).load_only(MetaItem.id, MetaItem.owner_username, MetaItem.owner_name, MetaItem.owner_type)).where(OSSoftwareModel.id == id)
#         res = await db.scalars(statement=stmt)
#         oss: OSSoftwareModel = res.one()
#         # return oss
#         if oss.clone_url is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS's clone url is not found!")
#         res, isSuccess = await git.get_info(oss.fullname)
        
#         if isSuccess:
#             return res
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation have failed, try again later")
#     except exc.NoResultFound:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
#     except Exception as e:
#         logger.error("error", error=e)
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")

# @router.get(
#     "/oss/{id}/clone",
#     status_code=status.HTTP_200_OK,
#     # response_model=OSSoftwareSchema,
#     response_model_exclude_none=True,
#     description="Clone OSS"
# )
# async def clone_oss_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
#     try:
#         stmt = select(OSSoftwareModel).options(joinedload(OSSoftwareModel.meta_list).load_only(MetaList.key, MetaList.name)).options(joinedload(OSSoftwareModel.meta_item).load_only(MetaItem.id, MetaItem.owner_username, MetaItem.owner_name, MetaItem.owner_type)).where(OSSoftwareModel.id == id)
#         res = await db.scalars(statement=stmt)
#         oss: OSSoftwareModel = res.one()
#         # return oss
#         if oss.clone_url is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS's clone url is not found!")
#         res, iscloned = await git.clone(oss.fullname, oss.clone_url)
        
#         if iscloned:
#             return res
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation have failed, try again later")
#     except exc.NoResultFound:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
#     except Exception:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")


# @router.get(
#     "/oss/{id}/compress",
#     status_code=status.HTTP_200_OK,
#     # response_model=OSSoftwareSchema,
#     response_model_exclude_none=True,
#     description="Compress OSS"
# )
# async def compress_oss_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
#     try:
#         stmt = select(OSSoftwareModel).where(OSSoftwareModel.id == id)
#         res = await db.scalars(statement=stmt)
#         oss: OSSoftwareModel = res.one()
        
#         iscompressed = await tarfile.compress(oss.fullname)
#         if iscompressed:
#             return {"message": "Operation Succeded, OSS have been compressed"}
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation have failed, try again later")
#     except exc.NoResultFound:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown error: {e}")

# @router.get(
#     "/oss/{id}/decompress",
#     status_code=status.HTTP_200_OK,
#     # response_model=OSSoftwareSchema,
#     response_model_exclude_none=True,
#     description="Decompress OSS"
# )
# async def decompress_oss_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
#     try:
#         stmt = select(OSSoftwareModel).options(joinedload(OSSoftwareModel.meta_list).load_only(MetaList.key, MetaList.name)).options(joinedload(OSSoftwareModel.meta_item).load_only(MetaItem.id, MetaItem.owner_username, MetaItem.owner_name, MetaItem.owner_type)).where(OSSoftwareModel.id == id)
#         res = await db.scalars(statement=stmt)
#         oss: OSSoftwareModel = res.one()

#         isdecompressed = await tarfile.decompress(oss.fullname)
#         if isdecompressed:
#             return {"message": "Operation Succeded, OSS have been decompressed"}
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation have failed, try again later")

#     except exc.NoResultFound:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown error: {e}")

# @router.get(
#     "/oss/{id}/archive",
#     status_code=status.HTTP_200_OK,
#     # response_model=OSSoftwareSchema,
#     response_model_exclude_none=True,
#     description="Get OSS's archive info, does it exist or not, it's size...etc"
# )
# async def oss_info_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
#     try:
#         stmt = select(OSSoftwareModel).where(OSSoftwareModel.id == id)
#         res = await db.scalars(statement=stmt)
#         oss: OSSoftwareModel = res.one()

#         oss_archive_path = paths.get_oss_archive_path(oss.fullname)
#         does_archive_exists = paths.does_path_exists(oss_archive_path)
#         oss_archive_info = paths.get_path_info(oss_archive_path)

#         oss_compressed_archive_path = paths.get_oss_compressed_archive_path(oss.fullname)
#         does_compressed_archive_exists = paths.does_path_exists(oss_compressed_archive_path)
#         oss_compressed_archive_info = paths.get_path_info(oss_compressed_archive_path)


#         return {
#             "oss_archive": {
#                 "exists": does_archive_exists,
#                 "info": oss_archive_info
#             },
#             "oss_compressed_archive": {
#                 "exists": does_compressed_archive_exists,
#                 "info": oss_compressed_archive_info
#             }
#         }

#     except exc.NoResultFound:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown error: {e}")


# # @router.get(
# #     "/oss/{id}/source",
# #     status_code=status.HTTP_200_OK,
# #     # response_model=OSSoftwareSchema,
# #     response_model_exclude_none=True,
# #     description="Gets OSS's data from its external source"
# # )
# # async def get_oss_api_data_by_id(id: UUID, db: Annotated[AsyncSession, Depends(get_async_db)]):
# #     try:
# #         stmt = select(OSSoftwareModel).options(joinedload(OSSoftwareModel.meta_list).load_only(MetaList.key, MetaList.name)).options(joinedload(OSSoftwareModel.meta_item).load_only(MetaItem.id, MetaItem.owner_username, MetaItem.owner_name, MetaItem.owner_type)).where(OSSoftwareModel.id == id)
# #         res = await db.scalars(statement=stmt)
# #         oss: OSSoftwareModel = res.one()
# #         url = url=f"https://api.github.com/repos/{oss.meta_item.owner_username}/{oss.name}"
# #         res = httpx.client.get(url=url)
# #         return res.json()
# #     except exc.NoResultFound:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSS is not found!")
# #     except Exception:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown error, try again later")
