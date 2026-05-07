
from pydantic import Field, BaseModel
from typing import Annotated
###
from oss_archive.schemas import category, general , owner, oss


class SearchCategoriesQueries(BaseModel):
    model_config = {"extra": "forbid"} # Forbid adding other queries

    key: Annotated[str | None, Field(default=None)]
    name: Annotated[str | None, Field(default=None)]
    priority: Annotated[int | None, Field(default=None)]

    limit: Annotated[int, Field(default=100, gt=0, le=100)]
    offset: Annotated[int, Field(default=0, ge=0)]

class GetCategory_Res(
    category.DescriptiveSchema
    ):
    pass
    # main_oss: list[oss.MinimalSchema]
    # owners: list[owner.MinimalSchema]

class CreateCategory_Req(
    category.KeyField,
    category.NameField,
    category.DescriptionField,
    category.TopicsField,
    general.PriorityField,
    general.ReviewedField,
    ):
    pass

class CreateCategory_Res(
    category.FullSchema
    ):
    pass

class CreateCategories_Req(
    BaseModel
    ):
    categories: Annotated[list[CreateCategory_Req], Field()]

class CreateCategories_Res(
    BaseModel
    ):
    new_categories: Annotated[list[category.FullSchema], Field()]
    already_exists: Annotated[list[str], Field()]


class Update_Req(
    category.KeyField_Optional,
    category.NameField_Optional,
    category.DescriptionField_Optional,
    category.TopicsField_Optional,
    general.PriorityField_Optional,
    general.ReviewedField_Optional,
    ):
    pass

