from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query, status

from database import (
    create_category,
    create_db,
    create_product,
    delete_category,
    delete_product,
    get_category_by_id,
    get_product_by_id,
    list_categories,
    list_products,
    update_category,
    update_product,
)
from schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ProductCreate,
    ProductDeleteResponse,
    ProductOut,
    ProductUpdate,
)

app = FastAPI(title="Ecommerce API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    create_db()


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to the Ecommerce API"}


@app.get("/categories", response_model=list[CategoryOut])
def get_categories() -> list[dict[str, Any]]:
    return list_categories()


@app.post("/admin/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_new_category(payload: CategoryCreate) -> dict[str, Any]:
    return create_category(payload.model_dump())


@app.put("/admin/categories/{category_id}", response_model=CategoryOut)
def update_existing_category(category_id: int, payload: CategoryUpdate) -> dict[str, Any]:
    category = update_category(category_id, payload.model_dump(exclude_unset=True))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.delete("/admin/categories/{category_id}")
def delete_existing_category(category_id: int) -> dict[str, str]:
    deleted = delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": f"Category {category_id} deleted successfully"}


@app.get("/products", response_model=list[ProductOut])
def get_products(
    category: str | None = Query(default=None, description="Filter by category slug"),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, description="Search by name, category, or description"),
    featured: bool | None = Query(default=None),
    in_stock: bool | None = Query(default=None),
) -> list[dict[str, Any]]:
    return list_products(
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        featured=featured,
        in_stock=in_stock,
    )


@app.get("/products/filter", response_model=list[ProductOut])
def filter_products(
    category: str | None = Query(default=None, description="Filter by category slug"),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, description="Search by name, category, or description"),
    featured: bool | None = Query(default=None),
    in_stock: bool | None = Query(default=None),
) -> list[dict[str, Any]]:
    return list_products(
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        featured=featured,
        in_stock=in_stock,
    )


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int) -> dict[str, Any]:
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/products/slug/{slug}", response_model=ProductOut)
def get_product_by_slug(slug: str) -> dict[str, Any]:
    products = list_products(search=slug)
    for product in products:
        if product["slug"] == slug:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products() -> list[dict[str, Any]]:
    return list_products()


@app.post("/admin/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_new_product(payload: ProductCreate) -> dict[str, Any]:
    category = get_category_by_id(payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    data = payload.model_dump()
    if data.get("featured") is None:
        data["featured"] = False
    data["featured"] = int(data["featured"])
    product = create_product(data)
    return product


@app.put("/admin/products/{product_id}", response_model=ProductOut)
def update_existing_product(product_id: int, payload: ProductUpdate) -> dict[str, Any]:
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    if "category_id" in update_data:
        category = get_category_by_id(update_data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    if "featured" in update_data:
        update_data["featured"] = int(update_data["featured"])

    product = update_product(product_id, update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/admin/products/{product_id}", response_model=ProductDeleteResponse)
def delete_existing_product(product_id: int) -> dict[str, str]:
    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {product_id} deleted successfully"}


@app.get("/admin/overview")
def admin_overview() -> dict[str, Any]:
    products = list_products()
    categories = list_categories()
    return {
        "total_products": len(products),
        "featured_products": sum(1 for item in products if item["featured"]),
        "out_of_stock": sum(1 for item in products if item["stock"] <= 0),
        "total_categories": len(categories),
        "categories": [category["name"] for category in categories],
    }

@app.put("/admin/products/{product_id}/stock", response_model=ProductOut
         )
def update_product_stock(product_id: int, stock: int = Query(..., ge=0)) -> dict[str, Any]:
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = update_product(product_id, {"stock": stock})
    return updated_product
 