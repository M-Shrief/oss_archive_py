from typing import Any
from sqlalchemy.orm import Session
# from sqlalchemy import select, delete, update
# from sqlalchemy import exc 
from psycopg import errors
###
from oss_archive.utils.logger import logger
from oss_archive.utils import httpx
from oss_archive.utils.formatter import format_oss_fullname
from oss_archive.database.models import Owner as OwnerModel, OSS as OSSModel
from oss_archive.schemas import general as general_schemas
from oss_archive.seeders import helpers as seed_helpers
from oss_archive.database import helpers as db_helpers

API_BASE_URL = "https://codeberg.org/api/v1"
DEFAULT_PRIORITY = 7

async def seed_owner_oss(owner: OwnerModel, db: Session):
    repos_arr = await get_repos_from_source(owner)
    if repos_arr is None:
        return None

    logger.info("Got owners' repos", count=len(repos_arr))
    new_oss: list[OSSModel] = []
    for repo in repos_arr:
        should_apply_on = seed_helpers.should_apply_action_on_oss(owner, repo.get("name"))
        if not should_apply_on:
            continue

        seeded_oss = await seed_oss(owner, repo, db)
        if seeded_oss is None:
            continue
    
        logger.info(f"Seeded OSS: {seeded_oss.fullname}")

        new_oss.append(seeded_oss)

    logger.info("Seeded all OSS", count=len(new_oss))

    return new_oss

async def seed_oss(owner: OwnerModel, repo_dict: dict[str, Any], db: Session):
    try:
        repo_name = repo_dict.get("name")
        if repo_name is None:
            return None
        oss_fullname = format_oss_fullname(owner.username, repo_name)

        oss_does_exists = await db_helpers.does_oss_exists(oss_fullname, sync_db=db)
        if oss_does_exists:
            return None

        new_oss = create_new_oss(owner, repo_dict)
        if new_oss is None:
            return None
        
        db.add(new_oss)
        db.commit()

        db.refresh(new_oss)
        
        return new_oss
    except errors.UniqueViolation as e:
        db.rollback()
        logger.error("Error Inserting OSS for Unique key Violation OSS from Owner's repo", owner=owner, error=e)
        return None
    except errors.CheckViolation as e:
        db.rollback()
        logger.error("Error Inserting OSS for check Violation OSS from Owner's repo", owner=owner, error=e)
        return None
    except Exception as e:
        db.rollback()
        logger.error("Unknown Error when Inserting OSS from Owner's repom", owner=owner, error=e)
        return None

async def get_repos_from_source(owner: OwnerModel):
    match owner.type:
        case general_schemas.OwnerTypeEnum.Organization:
            res = await httpx.async_get(base_url=API_BASE_URL, endpoint=f"/orgs/{owner.username}/repos")
        case general_schemas.OwnerTypeEnum.Individual:
            logger.error("Can't get Individual data without authentication token")
            return None
        # case _:
        #     logger.error(f"Uknown OwnerType: {meta_item.type}")
        #     return None

    if res is None or res.status_code != 200:
        logger.info("Couldn't get repos from source", res=res)
        return None

    res_arr: list[dict[str, Any]] = res.json()
    return res_arr


def create_new_oss(owner: OwnerModel, repo_dict: dict[str, Any]): # pyright:ignore[reportExplicitAny]
    """Get the needed data from Github API response - an item from repos array - to create a OSS model."""
    try:
        oss = OSSModel()
        oss.repo_name = repo_dict.get("name") # pyright:ignore[reportAttributeAccessIssue]
        oss.fullname = format_oss_fullname(owner.username, oss.repo_name)
        oss.priority = DEFAULT_PRIORITY
        oss.description = repo_dict.get("description")
        oss.topics = repo_dict.get("topics") # pyright:ignore[reportAttributeAccessIssue]
        oss.reviewed = True
        oss.is_mirrored = False
        oss.development_started_at = repo_dict.get("created_at") 
        oss.development_status = general_schemas.DevelopmentStatusEnum.Stopped if repo_dict.get("archived") else general_schemas.DevelopmentStatusEnum.Ongoing
        oss.html_url = repo_dict.get("html_url")
        oss.clone_url = repo_dict.get("clone_url")
        # repo_license = repo_dict.get("license")
        # if repo_license is not None and repo_license["key"] != "other":
        #     oss.license_key = repo_license["key"]

        # Relations
        oss.main_category_key = owner.main_category_key
        # oss.related_categories.extend(owner.related_categories)
        oss.owner_username = owner.username

        return oss

    except KeyError as e:
        logger.error("OSS's repo data keys have changed, so there was an error converting it to an OSS model", error=e)
        return None

    except Exception as e:
        logger.error(f"Unknown error parsing github API for {owner.username}'s Repo: f{repo_dict.get("name")}", error=e)
        return None

