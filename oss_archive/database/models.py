from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, validates
from sqlalchemy import Table, Column, DateTime, Enum, ARRAY, String, text, SmallInteger, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID
###
from oss_archive.schemas.general import OwnerTypeEnum, DevelopmentStatusEnum, ActionsEnum

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class PriorityField():
    """Adding a priority field for the model
    the priority is an integer range from 1 to 10, the smaller the more important it is."""
    priority: Mapped[int] = mapped_column(SmallInteger())
    @validates("priority")
    def validate_priority(self, key, priority: int):
        if priority < 1 or priority > 10:
            raise ValueError("Priority should be between 1 and 10")
        return priority
# Enums
owner_type_enum = Enum('Individual', 'Organization', name='owner_type_enum')
development_status_enum = Enum('Ongoing', 'Stalled', 'Stopped', name='development_status_enum')
actions_enum = Enum('archive_only', 'archive_all', 'archive_all_except', name='actions_enum')

# Many-to-Many relations
# categories_owners_table = Table(
#     "categories_owners_table",
#     Base.metadata,
#     Column("main_category_key", ForeignKey("categories.key")),
#     Column("owner_username", ForeignKey("owners.username")),
# )

categories_oss_table = Table(
    "categories_oss_table",
    Base.metadata,
    Column("main_category_key", ForeignKey("categories.key")),
    Column("oss_id", ForeignKey("oss_table.id")),
)


# Tables
class Category(PriorityField, Base):
    __tablename__: str = "categories"
    key: Mapped[str] = mapped_column(String(length=128), primary_key=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(length=256), nullable=True)
    description:  Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    topics: Mapped[list[str]] = mapped_column(ARRAY(String(length=128)), default=[])
    reviewed: Mapped[bool] = mapped_column(Boolean(), default=False)
   # Entity Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    # Relations
    main_oss: Mapped[list["OSS"]] = relationship(back_populates="main_category")
    related_oss: Mapped[list["OSS"]] = relationship(secondary=categories_oss_table, back_populates="related_categories")
    # related_categories: Mapped[list["OSS"]] = relationship(secondary=categories_owners_table, back_populates="related_categories")

    owners: Mapped[list["Owner"]] = relationship(back_populates="main_category")

class Owner(PriorityField, Base):
    __tablename__: str = "owners"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(length=256), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(length=256), nullable=True)
    type: Mapped[OwnerTypeEnum] = mapped_column(Enum(OwnerTypeEnum, name="owner_type_enum", native_enum=True), nullable=False, default=OwnerTypeEnum.Individual)
    source: Mapped[str] = mapped_column(String(length=128), nullable=False)
    other_sources: Mapped[list[str]] = mapped_column(ARRAY(String(length=128)), default=[])
    actions: Mapped[ActionsEnum] = mapped_column(Enum(ActionsEnum, name="actions_enum", native_enum=True), nullable=False)
    actions_on: Mapped[list[str]] = mapped_column(ARRAY(String(128)), default=[])
    html_url: Mapped[str | None] = mapped_column(String(length=256), nullable=True)
    reviewed: Mapped[bool] = mapped_column(Boolean(), default=False)
    # Entity Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    # Relations
    main_category_key: Mapped[str] = mapped_column(ForeignKey("categories.key"), nullable=False)
    main_category: Mapped[Category] = relationship(back_populates="owners")
    # related_categories: Mapped[list[Category]] = relationship(secondary=categories_oss_table, back_populates="related_categories")

    # put entity in strings if it wasn't declared before
    owned_oss: Mapped[list["OSS"]] = relationship(back_populates="owner")

class OSS(PriorityField, Base):
    __tablename__: str = "oss_table"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True, nullable=False)
    repo_name: Mapped[str] = mapped_column(String(length=256), nullable=False)
    fullname: Mapped[str] = mapped_column(String(length=512), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    topics: Mapped[list[str]] = mapped_column(ARRAY(String(length=128)), default=[]) # we gets the field data from the API
    reviewed: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_mirrored: Mapped[bool] = mapped_column(Boolean(), default=False) # did we mirror it?
    development_status: Mapped[DevelopmentStatusEnum] = mapped_column(Enum(DevelopmentStatusEnum, name="development_status_enum", native_enum=True), nullable=False, default=DevelopmentStatusEnum.Ongoing)
    development_started_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True) # Source's Timestamps, it's Date the oss's repo was created/started
    mirror_lfs: Mapped[bool] = mapped_column(Boolean(), default=False) # did we mirror it?
    # URLs
    html_url: Mapped[str | None] = mapped_column(String(length=256), nullable=True) ### oss page (html page)
    clone_url: Mapped[str | None] = mapped_column(String(length=256), nullable=True) ### git clone's URL
    # Entity Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    ### Relations
    main_category_key: Mapped[str] = mapped_column(ForeignKey("categories.key"), nullable=False)
    main_category: Mapped[Category] = relationship(back_populates="main_oss")
    related_categories: Mapped[list[Category]] = relationship(secondary=categories_oss_table, back_populates="related_oss")

    owner_username: Mapped[str] = mapped_column(ForeignKey("owners.username"), nullable=False)
    owner: Mapped[Owner] = relationship(back_populates="owned_oss")
