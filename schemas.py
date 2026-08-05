from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120)
    description: str | None = None
    category: str = Field(..., min_length=2, max_length=80)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    featured: bool = False
    image_url: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=80)
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    featured: bool | None = None
    image_url: str | None = None


class ProductOut(ProductBase):
    id: int
    created_at: str | None = None

    model_config = {"from_attributes": True}


class ProductDeleteResponse(BaseModel):
    message: str
