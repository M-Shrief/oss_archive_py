from sqlalchemy.orm import Session
from time import sleep
###
from oss_archive.config import ENV, Forgejo as forgejo_config
from oss_archive.utils.logger import logger
from oss_archive.database.models import Category as CategoryModel, Owner as OwnerModel, OSS as OSSModel
from oss_archive.database import helpers as db_helpers
from oss_archive.seeders.json import seed_json
from oss_archive.seeders.sources import github as github_source, codeberg as codeberg_source
from oss_archive.seeders.forgejo import create_org_for_mirrors, is_oss_mirrored, mirror_oss, DEFAULT_MIRROR_INTERVAL
from oss_archive.components.forgejo.schema import MigrateRepoReqBody, ServiceEnum

async def seed(db: Session):
    ### Make requests to outer APIs async, but the seeding operation can by sync
    # Steps:
    # 1 - We seed data in json-archive first to the database
    # _ = await seed_json(db)   
    # 2 -  Pull owners and start using each item to seed OSS into oss_table    
    # _ = await seed_owners_oss(db)

    # 3 - After that we should create "mirrors" user in forgejo if it doesn't exist
    # is_org_for_mirrors_created = await create_org_for_mirrors()
    # if is_org_for_mirrors_created is False:
    #     return
    # 4 - Then we begin mirrors OSS while prioritizing the most important one to be done first,
    # and use a method that enable us to resume the work if it was stopped for any reason, and we can use WAL for that. 
    _ = await mirror_all_oss(db)    
    return


async def seed_owners_oss(db: Session):
    owners = await db_helpers.get_all_owners(sync_db=db)
    if owners is None or len(owners) == 0:
        return

    for owner in owners:

        # So that we limit owners seeded while testing.
        if ENV == "dev" and owner.main_category_key not in ["ai", "prog_awe"]:
            continue
        
        logger.info(f"Owner is in {owner.main_category}")
        _ = await seed_owner_oss_from_source(owner, db)
        # Sleep 0.5 seconds to prevent source's rate-limit
        sleep(0.5)
    return

async def seed_owner_oss_from_source(owner: OwnerModel, db: Session): #-> Owner:
    match owner.source:
        case "github":
            return await github_source.seed_owner_oss(owner, db)
        case "codeberg":
            return await codeberg_source.seed_owner_oss(owner, db)
        # Defualt None value for unknown sources.
        case _:
            logger.error("Unkown OSS source", owner=owner)
            return None

async def mirror_all_oss(db: Session):
    oss_list = await db_helpers.get_all_oss(sync_db=db)
    if oss_list is None:
        return

    if ENV == "dev": # if we're in development limit them to 10 OSS only.
        oss_list = oss_list[:10]

    org_for_mirrors = forgejo_config.get("org_for_mirrors")
    if org_for_mirrors is None:
        return

    for oss in oss_list:
        if oss.clone_url is None:
            logger.info("Failed to mirror OSS, as it's clone_url doesn't exists", oss_fullname=oss.fullname)
            continue


        is_mirrored = await is_oss_mirrored(oss.fullname)
        if is_mirrored is True:
            logger.info("OSS is already mirrored.", oss_fullname=oss.fullname)
            continue


        oss_data = MigrateRepoReqBody(
            clone_addr=oss.clone_url,
            repo_name=oss.fullname,
            repo_owner=org_for_mirrors,
            service=ServiceEnum.git,
            mirror=True,
            mirror_interval=DEFAULT_MIRROR_INTERVAL
        )
        did_mirror_oss = await mirror_oss(oss_data)

        if did_mirror_oss is True:
            logger.info("Started the Mirroring procces for the OSS successfully.", oss_fullname=oss.fullname)
        else:
            logger.error("Failed to start the Mirroring procces for the OSS.", oss_fullname=oss.fullname)
    
        sleep(2.0)