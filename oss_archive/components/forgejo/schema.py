from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from enum import Enum
###

class ForgejoOrganization(BaseModel):
    # avatar_url: Annotated[str | None, Field()]
    description: Annotated[str | None, Field()]
    email: Annotated[str | None, Field()]
    full_name: Annotated[str | None, Field()]
    # location: Annotated[str | None, Field()]
    name: Annotated[str | None, Field()]
    # repo_admin_change_team_access: Annotated[bool | None, Field()]
    username: Annotated[str | None, Field()]
    # visibility: Annotated[str | None, Field()]
    website: Annotated[str | None, Field()]

class ForgejoUser(BaseModel):
    # active: Annotated[bool | None, Field()]
    # avatar_url: Annotated[str | None, Field()]
    created: Annotated[datetime | None, Field()]
    description: Annotated[str | None, Field()]
    email: Annotated[str | None, Field()]
    # followers_count: Annotated[int | None, Field()]
    # following_count: Annotated[int | None, Field()]
    html_url: Annotated[str | None, Field()]
    id: Annotated[int | None, Field()]
    # is_admin: Annotated[bool | None, Field()]
    # language: Annotated[str | None, Field()]
    # last_login: Annotated[datetime | None, Field()]
    login: Annotated[str | None, Field()]
    login_name: Annotated[str | None, Field(default="empty")]
    # prohibit_login: Annotated[bool | None, Field()]
    # restricted: Annotated[bool | None, Field()]
    # source_id: Annotated[int | None, Field()]
    # starred_repos_count: Annotated[int | None, Field()]
    # visibility: Annotated[str | None, Field()]
    website: Annotated[str | None, Field()]

class ForgejoRepo(BaseModel):
    # allow_fast_forward_only_merge: Annotated[bool | None, Field()]
    # allow_merge_commits: Annotated[bool | None, Field()]
    # allow_rebase: Annotated[bool | None, Field()]
    # allow_rebase_explicit: Annotated[bool | None, Field()]
    # allow_rebase_update: Annotated[bool | None, Field()]
    # allow_squash_merge: Annotated[bool | None, Field()]
    archived: Annotated[bool | None, Field()]
    archived_at: Annotated[datetime | None, Field()]
    # avatar_url: Annotated[str | None, Field()]
    clone_url: Annotated[str | None, Field()]
    created_at: Annotated[datetime | None, Field()]
    # default_allow_maintainer_edit: Annotated[bool | None, Field()]
    # default_branch: Annotated[str | None, Field()]
    # default_delete_branch_after_merge: Annotated[bool | None, Field()]
    # default_merge_style: Annotated[str | None, Field()]
    # default_update_style: Annotated[str | None, Field()]
    description: Annotated[str | None, Field()]
    # empty: Annotated[bool | None, Field()]
    # fork: Annotated[bool | None, Field()]
    # forks_count: Annotated[int | None, Field()]
    full_name: Annotated[str | None, Field()]
    # globally_editable_wiki: Annotated[bool | None, Field()]
    # has_actions: Annotated[bool | None, Field()]
    # has_issues: Annotated[bool | None, Field()]
    # has_packages: Annotated[bool | None, Field()]
    # has_projects: Annotated[bool | None, Field()]
    # has_pull_requests: Annotated[bool | None, Field()]
    # has_releases: Annotated[bool | None, Field()]
    # has_wiki: Annotated[bool | None, Field()]
    html_url: Annotated[str | None, Field()]
    id: Annotated[int | None, Field()]
    # ignore_whitespace_conflicts: Annotated[bool | None, Field()]
    internal: Annotated[bool | None, Field()]
    language: Annotated[str | None, Field()]
    languages_url: Annotated[str | None, Field()]
    link: Annotated[str | None, Field()]
    mirror: Annotated[bool | None, Field()]
    mirror_interval: Annotated[str | None, Field(default="168h0m0s",examples=["8h0m0s"])]
    mirror_updated: Annotated[datetime | None, Field()]
    name: Annotated[str | None, Field()]
    # object_format_name: Annotated[str | None, Field()]
    # open_issues_count: Annotated[int | None, Field()]
    # open_pr_counter: Annotated[int | None, Field()]
    original_url: Annotated[str | None, Field()]
    # private: Annotated[bool | None, Field()]
    # release_counter: Annotated[int | None, Field()]
    # size: Annotated[int | None, Field()]
    # ssh_url: Annotated[str | None, Field()]
    # stars_count: Annotated[int | None, Field()]
    # template: Annotated[bool | None, Field()]
    topics: Annotated[list[str] | None, Field()]
    updated_at: Annotated[datetime | None, Field()]
    url: Annotated[str | None, Field()]
    # watchers_count: Annotated[int | None, Field()]
    website: Annotated[str | None, Field()]


class ForgejoLicense(BaseModel):
    key: Annotated[str | None, Field(examples=["MIT"])]
    name: Annotated[str | None, Field(examples=["MIT"])]
    implementation: Annotated[str | None, Field(examples=["Create a text file (typically named LICENSE or LICENSE.txt) in the root of your source code and copy the text of the license into the file"])]
    body: Annotated[str | None, Field(examples=["MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated...etc"])]

class ForgejoLicensesListItem(BaseModel):
    key: Annotated[str | None, Field(examples=["MIT"])]
    name: Annotated[str | None, Field(examples=["MIT"])]


### Requests Schemas

class CreateOrgReqBody(BaseModel):
    username: Annotated[str, Field(examples=["user"])]
    org_name: Annotated[str, Field(examples=["org1"])]

class AddUserReqBody(BaseModel):
    email: Annotated[str, Field(examples=["example2@mail.com"])]
    username: Annotated[str, Field(examples=["example2"])]
    password: Annotated[str, Field(examples=["P@ssword1"])]


class ServiceEnum(str, Enum):
    git = "git"
    github = "github"
    gitea = "gitea"
    gitlab = "gitlab"
    gogs = "gogs"
    onedev = "onedev"
    gitbucket = "gitbucket"
    codebase = "codebase"
    forgejo = "forgejo"
class MigrateRepoReqBody(BaseModel):
    clone_addr: Annotated[str, Field(examples=["https://github.com/deepseek-ai/awesome-deepseek-integration.git"])]
    repo_name: Annotated[str, Field(examples=["deepseek-ai:awesome-deepseek-integration"])]
    repo_owner: Annotated[str, Field(examples=["mirrors"])]
    service: Annotated[ServiceEnum, Field(default=ServiceEnum.git)]
    mirror: Annotated[bool, Field(default=True)]
    mirror_interval: Annotated[str, Field(default="168h0m0s")]
    # auth_username: Annotated[str | None, Field(default="")] # used to authenticate to the service
    # auth_password: Annotated[str | None, Field(default="")] # used to authenticate to the service