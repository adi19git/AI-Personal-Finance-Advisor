from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    color: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str | None = None
    color: str | None = None
    is_default: bool

    model_config = {"from_attributes": True}
