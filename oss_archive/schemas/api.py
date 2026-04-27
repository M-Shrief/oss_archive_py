from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Annotated, Literal, TypeVar, Generic


class BaseRes(BaseModel):
    message: Annotated[str, Field()]

class SharedQueriesForGetAllRequests(BaseModel):
    """A model to contain shared queries for API request to get a list of entities, like blocks.
    Use like this:
    @app.get("/items/")
    
    async def read_items(queries: Annotated[SharedQueriesForGetAllRequests, Query()]):
        return queries
    """
    model_config = {"extra": "forbid"} # Forbid adding other queries

    limit: Annotated[int, Field(default=100, gt=0, le=100)]
    offset: Annotated[int, Field(default=0, ge=0)]
    # order_by: Annotated[Literal["created_at", "updated_at"] | None, Field(default=None)]
    # tags: Annotated[list[str] | None, Field(default=None)] # multiple query values


DataType = TypeVar('DataType')

class GetAll_Res(BaseModel, Generic[DataType]):
    data: Annotated[list[DataType], Field()]
    total_count: Annotated[int | None, Field(default=None)]
    offset: Annotated[int, Field()]
    limit: Annotated[int, Field()]

class Update_Res(BaseModel):
    pass

class Delete_Res(BaseModel):
    pass
