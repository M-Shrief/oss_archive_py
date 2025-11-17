from dotenv import dotenv_values
from typing import TypedDict


__env = dotenv_values(".env")

ENV = __env.get("ENV") or "dev"

ARCHIVE_BASE_PATH = __env.get("ARCHIVE_BASE_PATH")
COMPRESSED_ARCHIVE_BASE_PATH = __env.get("COMPRESSED_ARCHIVE_BASE_PATH")

JSON_FILES_PATH = __env.get("JSON_FILES_PATH")

class APIConfigType(TypedDict):
    base_url: str | None

API = APIConfigType(
    base_url = __env.get("API_BASE_URL")
)

class DatabaseConfigType(TypedDict):
    user: str
    password: str
    host: str
    port: int
    name: str
    url: str
    conn_str: str

db_port = __env.get("DB_PORT")

DB = DatabaseConfigType(
    user= __env.get("DB_USER") or "postgres",
    password= __env.get("DB_PASSWORD") or "postgres",
    host= __env.get("DB_HOST") or "localhost",
    port= int(db_port) if db_port is not None else 5432,
    name= __env.get("DB_NAME") or "oss_archive",
    url= F"postgresql://{__env.get("DB_USER")}:{__env.get("DB_PASSWORD")}@{__env.get("DB_HOST")}:{__env.get("DB_PORT")}/{__env.get("DB_NAME")}",
    conn_str=  F"host={__env.get("DB_HOST")} port={__env.get("DB_PORT")} user={__env.get("DB_USER")} dbname={__env.get("DB_NAME")} password={__env.get("DB_PASSWORD")} sslmode=disable"        
    )

class ForgejoType(TypedDict):
    base_url: str | None
    access_token: str | None
    admin_username: str | None
    org_for_mirrors: str | None

Forgejo = ForgejoType(
    base_url = __env.get("FORGEJO_BASE_URL"),
    access_token = __env.get("FORGEJO_ACCESS_TOKEN"),
    admin_username = __env.get("FORGEJO_ADMIN_USERNAME"),
    org_for_mirrors = __env.get("FORGEJO_ORG_FOR_MIRRORS")
)