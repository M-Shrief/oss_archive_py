"""
    Request and Reponse schemas to be used by the os_software router.
"""
from pydantic import BaseModel, Field
from typing import Annotated
from uuid import UUID
###
from oss_archive.schemas import oss,  general


class SearchOSSQueries(BaseModel):
    model_config = {"extra": "forbid"} # Forbid adding other queries

    id: Annotated[UUID | None, Field(default=None)]
    repo_name: Annotated[str | None, Field(default=None)]
    owner_username: Annotated[str | None, Field(default=None)]
    fullname: Annotated[str | None, Field(default=None)]
    priority: Annotated[int | None, Field(default=None)]
    is_mirrored: Annotated[bool | None, Field(default=None)]
    development_status: Annotated[bool | None, Field(default=None)]


class GetOSS_Res(
    oss.DescriptiveSchema
    ):
    pass
    # category: category.MinimalSchema

class CreateOSS_Req(
    oss.RepoNameField,
    oss.DescriptionField,
    oss.TopicsField,
    oss.IsMirroredField,
    oss.DevelopmentStatusField,
    oss.DevelopmentStartedAtField,
    oss.HTMLURLField,
    oss.CloneURLField,
    general.MainCategoryKeyField,
    general.OwnerUsernameField,
    general.PriorityField,
    general.ReviewedField,
    ):
    pass

class CreateOSS_Res(
    oss.FullSchema
    ):
    pass

class CreateManyOSS_Req(
    BaseModel
    ):
    oss_list: Annotated[list[CreateOSS_Req], Field()]

class CreateManyOSS_Res(
    BaseModel
    ):
    new_oss_list: Annotated[list[oss.FullSchema], Field()]
    already_exists: Annotated[list[str], Field()]



class UpdateOSS_Req(
    oss.RepoNameField_Optional,
    oss.DescriptionField_Optional,
    oss.TopicsField_Optional,
    oss.IsMirroredField_Optional,
    oss.DevelopmentStatusField_Optional,
    oss.DevelopmentStartedAtField_Optional,
    oss.HTMLURLField_Optional,
    oss.CloneURLField_Optional,
    general.MainCategoryKeyField_Optional,
    general.OwnerUsernameField_Optional,
    general.PriorityField_Optional,
    general.ReviewedField_Optional,
):
    pass