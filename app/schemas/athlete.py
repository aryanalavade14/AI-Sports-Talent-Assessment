import re
import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Gender = Literal["male", "female", "other"]
_PHONE_RE = re.compile(r"^\+?[0-9\- ]{7,15}$")


def _check_dob(value: date) -> date:
    today = date.today()
    if value >= today:
        raise ValueError("date_of_birth must be in the past")
    age = (today - value).days / 365.25
    if age < 5 or age > 100:
        raise ValueError("athlete age must be between 5 and 100 years")
    return value


def _check_phone(value: str | None) -> str | None:
    if value is not None and not _PHONE_RE.match(value):
        raise ValueError("phone must be 7-15 digits (optional leading +)")
    return value


class AthleteBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    date_of_birth: date
    gender: Gender
    phone: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    sport: str | None = Field(default=None, max_length=100)

    @field_validator("date_of_birth")
    @classmethod
    def _validate_dob(cls, v):
        return _check_dob(v)

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v):
        return _check_phone(v)


class AthleteCreate(AthleteBase):
    user_id: uuid.UUID | None = Field(
        default=None, description="Admins only: which user this profile belongs to. Athletes: leave empty."
    )


class AthleteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    date_of_birth: date | None = None
    gender: Gender | None = None
    phone: str | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    sport: str | None = Field(default=None, max_length=100)

    @field_validator("date_of_birth")
    @classmethod
    def _dob(cls, v):
        return _check_dob(v) if v is not None else v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        return _check_phone(v)


class AthleteOut(AthleteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
