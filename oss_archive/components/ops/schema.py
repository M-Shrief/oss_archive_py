
from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, TypedDict

class MirrorOSSQueries(BaseModel):
    model_config = {"extra": "forbid"} # Forbid adding other queries

    caregory_key: Annotated[str | None, Field(default=None)]
    owner_username: Annotated[str | None, Field(default=None)]
    # order_by: Annotated[Literal["created_at", "updated_at"] | None, Field(default=None)]
    # tags: Annotated[list[str] | None, Field(default=None)] # multiple query values

class OpsSharedQueries(BaseModel):
    model_config = {"extra": "forbid"} # Forbid adding other queries

    limit: Annotated[int, Field(default=10, gt=0, le=100)]
    offset: Annotated[int, Field(default=0, ge=0)]
