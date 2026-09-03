from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

SEED_CATEGORIES = [
    {"name": "Fashion", "slug": "fashion", "description": "Fashion collection"},
    {"name": "Electronics", "slug": "electronics", "description": "Electronics collection"},
    {"name": "Home", "slug": "home", "description": "Home essentials"},
    {"name": "Sports", "slug": "sports", "description": "Sports and fitness"},
]

SEED_PRODUCTS = [
    {
        "name": "Classic Hoodie",
        "slug": "classic-hoodie",
        "description": "Soft premium hoodie with modern fit.",
        "category_id": 1,
        "price": 49.99,
        "stock": 15,
        "featured": 1,
        "image_url": "https://example.com/images/hoodie.jpg",
    },
    {
        "name": "Gaming Headset",
        "slug": "gaming-headset",
        "description": "Noise canceling headset for long sessions.",
        "category_id": 2,
        "price": 79.0,
        "stock": 12,
        "featured": 1,
        "image_url": "https://example.com/images/headset.jpg",
    },
    {
        "name": "Coffee Grinder",
        "slug": "coffee-grinder",
        "description": "Compact burr grinder for fresh coffee.",
        "category_id": 3,
        "price": 34.5,
        "stock": 0,
        "featured": 0,
        "image_url": "https://example.com/images/grinder.jpg",
    },
    {
        "name": "Fitness Bottle",
        "slug": "fitness-bottle",
        "description": "Leakproof insulated bottle for workouts.",
        "category_id": 4,
        "price": 22.75,
        "stock": 25,
        "featured": 0,
        "image_url": "https://example.com/images/bottle.jpg",
    },
    {
        "name": "Desk Lamp",
        "slug": "desk-lamp",
        "description": "Minimal desk lamp with adjustable brightness.",
        "category_id": 3,
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


def slugify(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        else:
            cleaned.append("-")
    return "".join(cleaned).strip("-")


def ensure_columns(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_code ON categories(code)"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_products_product_code ON products(product_code)"
    )


def next_category_code(conn: sqlite3.Connection) -> str:
    result = conn.execute("SELECT COALESCE(MAX(CAST(code AS INTEGER)), 0) FROM categories").fetchone()[0]
    return f"{int(result) + 1:02d}"


def next_product_code(conn: sqlite3.Connection) -> str:
    result = conn.execute("SELECT COALESCE(MAX(CAST(product_code AS INTEGER)), 0) FROM products").fetchone()[0]
    return f"{int(result) + 1:02d}"


def create_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                code TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if category_count == 0:
            for category in SEED_CATEGORIES:
                conn.execute(
                    """
                    INSERT INTO categories (name, slug, description, code)
                    VALUES (:name, :slug, :description, :code)
                    """,
                    {**category, "code": next_category_code(conn)},
                )
            conn.commit()

        product_table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
        ).fetchone()
        legacy_product_table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='old_products'"
        ).fetchone()

        if product_table_exists is None:
            conn.execute(
                """
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    description TEXT,
                    category_id INTEGER,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0,
                    featured INTEGER NOT NULL DEFAULT 0,
                    image_url TEXT,
                    product_code TEXT UNIQUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        else:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()}
            if "category_id" not in columns or "product_code" not in columns:
                conn.execute("ALTER TABLE products RENAME TO old_products")
                conn.execute(
                    """
                    CREATE TABLE products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        slug TEXT NOT NULL UNIQUE,
                        description TEXT,
                        category_id INTEGER,
                        price REAL NOT NULL,
                        stock INTEGER NOT NULL DEFAULT 0,
                        featured INTEGER NOT NULL DEFAULT 0,
                        image_url TEXT,
                        product_code TEXT UNIQUE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.commit()

                legacy_rows = conn.execute(
                    """
                    SELECT id, name, slug, description, category, price, stock, featured, image_url, created_at
                    FROM old_products
                    """
                ).fetchall()
                for row in legacy_rows:
                    legacy_category = (row["category"] or "").strip()
                    category_id = None
                    if legacy_category:
                        category_slug = slugify(legacy_category)
                        category_row = conn.execute(
                            "SELECT id FROM categories WHERE slug = ?",
                            (category_slug,),
                        ).fetchone()
                        if category_row is None:
                            category_code = next_category_code(conn)
                            cursor = conn.execute(
                                "INSERT INTO categories (name, slug, description, code) VALUES (?, ?, ?, ?)",
                                (
                                    legacy_category.title(),
                                    category_slug,
                                    f"{legacy_category.title()} collection",
                                    category_code,
                                ),
                            )
                            category_id = cursor.lastrowid
                        else:
                            category_id = category_row["id"]

                    product_code = f"{row['id']:02d}"
                    conn.execute(
                        """
                        INSERT INTO products (
                            id, name, slug, description, category_id, price, stock, featured, image_url, product_code, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["id"],
                            row["name"],
                            row["slug"],
                            row["description"],
                            category_id,
                            row["price"],
                            row["stock"],
                            row["featured"],
                            row["image_url"],
                            product_code,
                            row["created_at"],
                        ),
                    )
                conn.commit()
                conn.execute("DROP TABLE old_products")
                conn.commit()

        ensure_columns(conn)

        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if product_count == 0:
            for index, product in enumerate(SEED_PRODUCTS, start=1):
                conn.execute(
                    """
                    INSERT INTO products (name, slug, description, category_id, price, stock, featured, image_url, product_code)
                    VALUES (:name, :slug, :description, :category_id, :price, :stock, :featured, :image_url, :product_code)
                    """,
                    {**product, "product_code": f"{index:02d}"},
                )
            conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def list_categories() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, slug, description, code, created_at FROM categories ORDER BY id ASC"
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, slug, description, code, created_at FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        return row_to_dict(row) if row else None


def create_category(payload: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        code = next_category_code(conn)
        cursor = conn.execute(
            """
            INSERT INTO categories (name, slug, description, code)
            VALUES (:name, :slug, :description, :code)
            """,
            {**payload, "code": code},
        )
        conn.commit()
        return get_category_by_id(cursor.lastrowid) or {}


def update_category(category_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    fields = []
    values = []
    for key, value in payload.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(category_id)

    with get_connection() as conn:
        if not fields:
            return get_category_by_id(category_id)
        cursor = conn.execute(
            f"UPDATE categories SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return get_category_by_id(category_id)


def delete_category(category_id: int) -> bool:
    with get_connection() as conn:
        product_count = conn.execute(
            "SELECT COUNT(*) FROM products WHERE category_id = ?",
            (category_id,),
        ).fetchone()[0]
        if product_count:
            return False
        cursor = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return cursor.rowcount > 0


def list_products(
    category: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    featured: bool | None = None,
    in_stock: bool | None = None,
) -> list[dict[str, Any]]:
    query = [
        """
        SELECT
            p.id,
            p.product_code,
            p.name,
            p.slug,
            p.description,
            p.category_id,
            c.name AS category_name,
            c.slug AS category_slug,
            c.code AS category_code,
            p.price,
            p.stock,
            p.featured,
            p.image_url,
            p.created_at
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE 1=1
        """
    ]
    params: list[Any] = []

    if category:
        query.append("AND c.slug = ?")
        params.append(slugify(category))
    if category_id is not None:
        query.append("AND p.category_id = ?")
        params.append(category_id)
    if min_price is not None:
        query.append("AND p.price >= ?")
        params.append(min_price)
    if max_price is not None:
        query.append("AND p.price <= ?")
        params.append(max_price)
    if search:
        query.append("AND (LOWER(p.name) LIKE ? OR LOWER(COALESCE(p.description, '')) LIKE ? OR LOWER(COALESCE(c.name, '')) LIKE ? OR LOWER(COALESCE(c.slug, '')) LIKE ?)")
        term = f"%{search.lower()}%"
        params.extend([term, term, term, term])
    if featured is not None:
        query.append("AND p.featured = ?")
        params.append(1 if featured else 0)
    if in_stock is not None:
        query.append("AND p.stock > 0" if in_stock else "AND p.stock <= 0")

    query.append("ORDER BY p.id DESC")

    with get_connection() as conn:
        rows = conn.execute(" ".join(query), params).fetchall()
        return [row_to_dict(row) for row in rows]


def get_product_by_id(product_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                p.id,
                p.product_code,
                p.name,
                p.slug,
                p.description,
                p.category_id,
                c.name AS category_name,
                c.slug AS category_slug,
                c.code AS category_code,
                p.price,
                p.stock,
                p.featured,
                p.image_url,
                p.created_at
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (product_id,),
        ).fetchone()
        return row_to_dict(row) if row else None


def create_product(payload: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        payload = dict(payload)
        payload["product_code"] = next_product_code(conn)
        cursor = conn.execute(
            """
            INSERT INTO products (name, slug, description, category_id, price, stock, featured, image_url, product_code)
            VALUES (:name, :slug, :description, :category_id, :price, :stock, :featured, :image_url, :product_code)
            """,
            payload,
        )
        conn.commit()
        return get_product_by_id(cursor.lastrowid) or {}


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
