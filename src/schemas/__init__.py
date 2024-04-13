from typing import Generic, TypeVar

from pydantic import BaseModel, conint
from pydantic.v1.generics import GenericModel

T = TypeVar("T")


class PageParams(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1) = 1


class PagedResponseSchema(GenericModel, Generic[T]):
    page_count: int
    page: int
    size: int
    results: list[T]
    has_next: bool
    has_prev: bool
