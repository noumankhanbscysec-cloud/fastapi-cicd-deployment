from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query, status

from database import create_db, create_product, delete_product, get_product_by_id, list_products, update_product
from schemas import ProductCreate, ProductDeleteResponse, ProductOut, ProductUpdate

app = FastAPI(title="Ecommerce API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    create_db()


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to the Ecommerce API"}


@app.get("/products", response_model=list[ProductOut])
def get_products(
    category: str | None = Query(default=None, description="Filter by category"),
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
    category: str | None = Query(default=None, description="Filter by category"),
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


@app.post("/admin/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_new_product(payload: ProductCreate) -> dict[str, Any]:
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
    return {
        "total_products": len(products),
        "featured_products": sum(1 for item in products if item["featured"]),
        "out_of_stock": sum(1 for item in products if item["stock"] <= 0),
        "categories": sorted({item["category"] for item in products}),
    }

