from typing import TypedDict
from sqlalchemy.orm import Session
###
from oss_archive.database.models import Category as CategoryModel, Owner as OwnerModel, OSS as OSSModel
from oss_archive.database import helpers as db_helpers
from oss_archive.utils import json as json_utils
from oss_archive.utils.logger import logger

class SeedAll_Res(TypedDict):
    seeded_categories_json: bool
    seeded_owners_json: bool
    seeded_oss_json: bool
\
async def seed_all(db: Session)->SeedAll_Res:
    return SeedAll_Res(
        seeded_categories_json=await seed_categories_json_files(db),
        seeded_owners_json=await seed_owners_json_files(db),
        seeded_oss_json=await seed_oss_json_files(db)
        )

async def seed_categories_json_files(db: Session)->bool:
    try:
        for file in json_utils.get_json_files(json_utils.CategoriesJSONFileConfig):
            file_data = json_utils.get_json_file_data(json_utils.CategoriesJSONFileConfig, file)
            if file_data is None:
                continue
            for item in file_data.items:
                new_category = CategoryModel(**item)

                does_exist = await db_helpers.does_category_exists(new_category.key, sync_db=db)
                if does_exist is False:
                    _ = db.add(new_category)
                
                db.commit()

        return True
    except Exception:
        logger.error("Couldn't seed Owners' JSON files")
        return False

async def seed_owners_json_files(db: Session)->bool:
    try:
        for file in json_utils.get_json_files(json_utils.OwnersJSONFileConfig):
            file_data = json_utils.get_json_file_data(json_utils.OwnersJSONFileConfig, file)
            if file_data is None:
                continue
            for item in file_data.items:
                new_owner = OwnerModel(**item)

                does_exist = await db_helpers.does_owner_exists(new_owner.username, sync_db=db)
                if does_exist is False:
                    _ = db.add(new_owner)
                
                db.commit()

        return True
    except Exception:
        logger.error("Couldn't seed Owners' JSON files")
        return False

async def seed_oss_json_files(db: Session)->bool:
    try:
        for file in json_utils.get_json_files(json_utils.OSSJSONFileConfig):
            file_data = json_utils.get_json_file_data(json_utils.OSSJSONFileConfig, file)
            if file_data is None:
                continue
            for item in file_data.items:
                new_oss = OSSModel(**item)

                does_exist = await db_helpers.does_oss_exists(new_oss.fullname, sync_db=db)
                if does_exist is False:
                    db.add(new_oss)
                    
                db.commit()

        return True
    except Exception:
        logger.error("Couldn't seed OSS JSON files")
        return False
