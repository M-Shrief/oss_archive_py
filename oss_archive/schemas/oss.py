from pydantic import Field, BaseModel
from typing import Annotated
from datetime import datetime
### 
from oss_archive.schemas import general

class RepoNameField(BaseModel):
    repo_name: Annotated[str, Field(max_length=256, examples=["DeepSeek-VL"])]

class RepoNameField_Optional(BaseModel):
    repo_name: Annotated[str | None, Field(default=None, max_length=256, examples=["DeepSeek-VL"])]

class FullnameField(BaseModel):
    fullname: Annotated[str, Field(max_length=256, examples=["deepseek-ai:DeepSeek-VL"])]

class FullnameField_Optional(BaseModel):
    fullname: Annotated[str | None, Field(default=None, max_length=256, examples=["deepseek-ai:DeepSeek-VL"])]

class DescriptionField(BaseModel):
    description: Annotated[str | None, Field(max_length=512, examples=["DeepSeek-VL: Towards Real-World Vision-Language Understanding"])]

class DescriptionField_Optional(BaseModel):
    description: Annotated[str | None, Field(default=None, max_length=512, examples=["DeepSeek-VL: Towards Real-World Vision-Language Understanding"])]

class TopicsField(BaseModel):
    topics: Annotated[list[str] | None, Field(examples=[["foundation-models","vision-language-model","vision-language-pretraining"]])]

class TopicsField_Optional(BaseModel):
    topics: Annotated[list[str] | None, Field(default=None, examples=[["foundation-models","vision-language-model","vision-language-pretraining"]])]

class IsMirroredField(BaseModel):
    is_mirrored: Annotated[bool, Field(default=False)]

class IsMirroredField_Optional(BaseModel):
    is_mirrored: Annotated[bool | None, Field(default=None)]

class DevelopmentStatusField(BaseModel):
    development_status: Annotated[general.DevelopmentStatusEnum, Field(default=general.DevelopmentStatusEnum.Ongoing)]

class DevelopmentStatusField_Optional(BaseModel):
    development_status: Annotated[general.DevelopmentStatusEnum | None, Field(default=None)]

class DevelopmentStartedAtField(BaseModel):
    development_started_at: Annotated[datetime | None, Field(default=None)]

class DevelopmentStartedAtField_Optional(BaseModel):
    development_started_at: Annotated[datetime | None, Field(default=None)]

class MirrorLFSField(BaseModel):
    mirror_lfs: Annotated[bool, Field(default=False)]

class MirrorLFSField_Optional(BaseModel):
    mirror_lfs: Annotated[bool | None, Field(default=None)]

class HTMLURLField(BaseModel):
    html_url: Annotated[str, Field(examples=["https://github.com/deepseek-ai/DeepSeek-VL"])]

class HTMLURLField_Optional(BaseModel):
    html_url: Annotated[str | None, Field(default=None, examples=["https://github.com/deepseek-ai/DeepSeek-VL"])]

class CloneURLField(BaseModel):
    clone_url: Annotated[str, Field(examples=["https://github.com/deepseek-ai/DeepSeek-VL.git"])]

class CloneURLField_Optional(BaseModel):
    clone_url: Annotated[str | None, Field(default=None, examples=["https://github.com/deepseek-ai/DeepSeek-VL.git"])]

class FullSchema(
    general.IdField,
    general.PriorityField,
    RepoNameField,
    FullnameField,
    DescriptionField,
    TopicsField,
    general.ReviewedField,
    IsMirroredField,
    DevelopmentStatusField,
    DevelopmentStartedAtField,
    MirrorLFSField,
    HTMLURLField,
    CloneURLField,
    general.CreatedAtField,
    general.UpdatedAtField,
    # Relations
    general.MainCategoryKeyField
    ):
    pass

class DescriptiveSchema(
    general.IdField,
    general.PriorityField,
    RepoNameField,
    FullnameField,
    DescriptionField,
    TopicsField,
    general.ReviewedField,
    IsMirroredField,
    DevelopmentStatusField,
    DevelopmentStartedAtField,
    MirrorLFSField,
    HTMLURLField,
    CloneURLField,
    # Relations
    general.MainCategoryKeyField,
    general.OwnerUsernameField,
    ):
    pass

class MinimalSchema(
    general.IdField,
    general.PriorityField,
    FullnameField,
    IsMirroredField,
    ):
    pass

class JSONSchema(
    general.PriorityField,
    RepoNameField,
    FullnameField,
    DescriptionField,
    TopicsField,
    general.ReviewedField,
    IsMirroredField,
    DevelopmentStatusField,
    DevelopmentStartedAtField,
    MirrorLFSField,
    HTMLURLField,
    CloneURLField,
    # Relations
    general.MainCategoryKeyField,
    general.OwnerUsernameField
):
    pass