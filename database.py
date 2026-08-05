from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

SEED_PRODUCTS = [
    {
        "name": "Classic Hoodie",
        "slug": "classic-hoodie",
        "description": "Soft premium hoodie with modern fit.",
        "category": "fashion",
        "price": 49.99,
        "stock": 15,
        "featured": 1,
        "image_url": "https://example.com/images/hoodie.jpg",
    },
    {
        "name": "Gaming Headset",
        "slug": "gaming-headset",
        "description": "Noise canceling headset for long sessions.",
        "category": "electronics",
        "price": 79.0,
        "stock": 12,
        "featured": 1,
        "image_url": "https://example.com/images/headset.jpg",
    },
    {
        "name": "Coffee Grinder",
        "slug": "coffee-grinder",
        "description": "Compact burr grinder for fresh coffee.",
        "category": "home",
        "price": 34.5,
        "stock": 0,
        "featured": 0,
        "image_url": "https://example.com/images/grinder.jpg",
    },
    {
        "name": "Fitness Bottle",
        "slug": "fitness-bottle",
        "description": "Leakproof insulated bottle for workouts.",
        "category": "sports",
        "price": 22.75,
        "stock": 25,
        "featured": 0,
        "image_url": "https://example.com/images/bottle.jpg",
    },
    {
        "name": "Desk Lamp",
        "slug": "desk-lamp",
        "description": "Minimal desk lamp with adjustable brightness.",
        "category": "home",
        "price": 28.99,
        "stock": 9,
        "featured": 1,
        "image_url": "https://example.com/images/lamp.jpg",
    },
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                featured INTEGER NOT NULL DEFAULT 0,
                image_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO products (name, slug, description, category, price, stock, featured, image_url)
                VALUES (:name, :slug, :description, :category, :price, :stock, :featured, :image_url)
                """,
                SEED_PRODUCTS,
            )
            conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def list_products(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    featured: bool | None = None,
    in_stock: bool | None = None,
) -> list[dict[str, Any]]:
    query = [
        "SELECT id, name, slug, description, category, price, stock, featured, image_url, created_at FROM products WHERE 1=1"
    ]
    params: list[Any] = []

    if category:
        query.append("AND category = ?")
        params.append(category)
    if min_price is not None:
        query.append("AND price >= ?")
        params.append(min_price)
    if max_price is not None:
        query.append("AND price <= ?")
        params.append(max_price)
    if search:
        query.append("AND (name LIKE ? OR description LIKE ? OR category LIKE ?)")
        term = f"%{search.lower()}%"
        params.extend([term, term, term])
    if featured is not None:
        query.append("AND featured = ?")
        params.append(1 if featured else 0)
    if in_stock is not None:
        query.append("AND stock > 0" if in_stock else "AND stock <= 0")

    query.append("ORDER BY id DESC")

    with get_connection() as conn:
        rows = conn.execute(" ".join(query), params).fetchall()
        return [row_to_dict(row) for row in rows]


def get_product_by_id(product_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, slug, description, category, price, stock, featured, image_url, created_at FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return row_to_dict(row) if row else None


def create_product(payload: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO products (name, slug, description, category, price, stock, featured, image_url)
            VALUES (:name, :slug, :description, :category, :price, :stock, :featured, :image_url)
            """,
            payload,
        )
        conn.commit()
        product_id = cursor.lastrowid
        return get_product_by_id(product_id) or {}


def update_product(product_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    fields = []
    values = []
    for key, value in payload.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(product_id)

    with get_connection() as conn:
        if not fields:
            return get_product_by_id(product_id)
        cursor = conn.execute(
            f"UPDATE products SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return get_product_by_id(product_id)


def delete_product(product_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
