from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from scalar_fastapi import get_scalar_api_reference # pyright:ignore[reportMissingTypeStubs]
from typing import Annotated
###
from oss_archive.utils.logger import logger
# Database
from oss_archive.database.index import get_sync_db, async_engine
from oss_archive.database.models import Base
from oss_archive.seeders.index import seed
# Components
from oss_archive.components.forgejo.router import router as forgejo_router
from oss_archive.components.categories.router import router as categories_router
from oss_archive.components.owners.router import router as owners_router
from oss_archive.components.oss.router import router as oss_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    lifespan=lifespan,
    title="OSS Archive",
    description="OSS Archive is a software built for archiving important Open-Source Software projects, so that it prevent any attempt to lock people access from it.",
    summary="Archiving Open-Source Software project",
    version="0.1.0",
    # docs_url="/docs",
    # redoc_url="/redoc"
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
    compresslevel=5
)

@app.get("/", status_code=status.HTTP_200_OK)
async def homepage():    
    return {
            "title": app.title,
            "description": app.description,
            "version": app.version,
            "Swagger-documentation_url": app.docs_url,
            "Redoc-documentation_url": app.redoc_url,
            "Scalar-documentation_url": "/scalar"            
        }


@app.get(
    "/scalar",
    include_in_schema=False,
    description="Scalar Modern API Client and Reference, check on https://github.com/scalar/scalar"
    )
async def scalar_html() :
    if app.openapi_url is None:
        return "Not Available"

    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

@app.get("/seed", status_code=status.HTTP_200_OK)
async def seed_database(db: Annotated[Session, Depends(dependency=get_sync_db)]):
    try:
        # Maybe we can add query params to skip what we want
        _ = await seed(db)
        return {"message": "Seedded The Database Successfully"}
    except Exception as e:
        logger.error("Seeding failure", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seeding operation has failed")

@app.get("/ping")
async def ping():    
    return {"message": "pong"}


### Adding API routes
app.include_router(forgejo_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(owners_router, prefix="/api")
app.include_router(oss_router, prefix="/api")
