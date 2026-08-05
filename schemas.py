from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120)
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None


class CategoryOut(CategoryBase):
    id: int
    code: str
    created_at: str | None = None


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=120)
    description: str | None = None
    category_id: int = Field(..., ge=1)
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
    category_id: int | None = Field(default=None, ge=1)
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    featured: bool | None = None
    image_url: str | None = None


class ProductOut(ProductBase):
    id: int
    product_code: str
    category_name: str
    category_slug: str | None = None
    category_code: str | None = None
    created_at: str | None = None


class ProductDeleteResponse(BaseModel):
    message: str
