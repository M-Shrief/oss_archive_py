from operator import concat
from re import split
from typing import Any
from sqlalchemy.orm import Session
from time import sleep
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

# API's Guide: https://huggingface.co/spaces/huggingface/openapi
# Steps:
# First, get collections by an owner: GET /api/collections 
#   example: https://huggingface.co/api/collections?owner=deepseek-ai&expand=true&limit=10
# Second, Then get data about certain collection:
# GET	https://huggingface.co/api/collections/{namespace}/{slug} ==> namespace = owner.username , slug is provided in get_collections for every collection
#   Example:	https://huggingface.co/api/collections/deepseek-ai/deepseek-v4-69ea2d6001aafa84d4d6f6f9
# you get the git's clone_url as the same url for the model, like: https://huggingface.co/deepseek-ai/deepseek-math-7b-rl

BASE_URL = "https://huggingface.co"
API_BASE_URL = BASE_URL + "/api"
DEFAULT_PRIORITY = 7

async def seed_owner_oss(owner: OwnerModel, db: Session):
    collections = await get_collections(owner)
    if collections is None:
        return None


    repos_arr: list[dict[str, Any]] = []
    for cItem in collections:
        sleep(0.5)
        cItem_slug = cItem.get("slug")
        if cItem_slug is None:
            continue

        collection = await get_collection(owner, cItem_slug)
        if collection is None:
            continue

        collection_items= collection.get("items")
        if collection_items is None:
            continue

        repos_arr = repos_arr + collection_items
        

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


async def get_collections(owner: OwnerModel):
    res = await httpx.async_get(base_url=API_BASE_URL, endpoint=f"/collections?owner={owner.username}&expand=true")
    if res is None or res.status_code != 200:
        logger.info("Couldn't get collections from source", res=res)
        return None

    collections: list[dict[str, Any]] = res.json()
    return collections 
    

async def get_collection(owner: OwnerModel, slug: str) :
    res = await httpx.async_get(base_url=API_BASE_URL, endpoint=f"/collections/{owner.username}/{slug}")
    if res is None or res.status_code != 200:
        logger.info("Couldn't get collections from source", res=res)
        return None

    collection: dict[str, Any] = res.json()
    return collection 
    
async def seed_oss(owner: OwnerModel, repo_dict: dict[str, Any], db: Session): 
    try:
        repo_name = __get_repo_name(repo_dict)
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


def create_new_oss(owner: OwnerModel, repo_dict: dict[str, Any]): # pyright:ignore[reportExplicitAny]
    """Get the needed data from Github API response - an item from repos array - to create a OSS model."""
    try:
        oss = OSSModel()

        oss.repo_name = __get_repo_name(repo_dict)

        oss.fullname = format_oss_fullname(owner.username, oss.repo_name)
        oss.priority = DEFAULT_PRIORITY
        oss.description = None
        oss.topics = repo_dict.get("pipeline_tag") or None # pyright:ignore[reportAttributeAccessIssue]
        oss.reviewed = True
        oss.is_mirrored = False
        oss.development_started_at = None
        oss.development_status = general_schemas.DevelopmentStatusEnum.Ongoing
        
        url = f"https://huggingface.co/{id}"
        oss.html_url = url
        oss.clone_url = url
        # repo_license = repo_dict.get("license")
        # if repo_license is not None and repo_license["key"] != "other":
        #     oss.license_key = repo_license["key"]

        # Relations
        oss.main_category_key = owner.main_category_key or "ai" # as huggingface is all about AI
        # oss.related_categories.extend(owner.related_categories)
        oss.owner_username = owner.username

        return oss

    except KeyError as e:
        logger.error("OSS's repo data keys have changed, so there was an error converting it to an OSS model", error=e)
        return None

    except Exception as e:
        logger.error(f"Unknown error parsing github API for {owner.username}'s Repo: f{repo_dict.get("name")}", error=e)
        return None


def __get_repo_name(repo_dict: dict[str, Any]):
        # huggingface doesn't save repo's name alone,
        # but repo's id looks like: deepseek-ai/DeepSeek-V4-Flash-Base
        # so we got what after /
        repo_id = repo_dict.get("id")
        name = ""
        if repo_id is not None:
            name = split(repo_id, "/")[1] # pyright:ignore[reportAny]
        return name