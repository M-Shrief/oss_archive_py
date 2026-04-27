
from pydantic import Field, BaseModel
from typing import Annotated
###
from oss_archive.schemas import category, general , owner, oss



class GetCategoryByKey_Res(
    category.DescriptiveSchema
    ):
    main_oss: list[oss.MinimalSchema]
    owners: list[owner.MinimalSchema]

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

