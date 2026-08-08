from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Form, HTTPException, Query, status
from fastapi.responses import HTMLResponse

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


def page_shell(title: str, content: str) -> HTMLResponse:
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{title}</title>
            <style>
                :root {{
                    --bg: #0f172a;
                    --bg-soft: #111827;
                    --card: rgba(15, 23, 42, 0.72);
                    --card-strong: rgba(15, 23, 42, 0.92);
                    --line: rgba(148, 163, 184, 0.2);
                    --text: #e2e8f0;
                    --muted: #94a3b8;
                    --primary: #60a5fa;
                    --primary-strong: #2563eb;
                    --secondary: #22c55e;
                    --danger: #f87171;
                    --shadow: 0 24px 80px rgba(15, 23, 42, 0.45);
                }}

                * {{ box-sizing: border-box; }}

                body {{
                    margin: 0;
                    font-family: Inter, "Segoe UI", sans-serif;
                    color: var(--text);
                    background:
                        radial-gradient(circle at top, rgba(96, 165, 250, 0.18), transparent 32%),
                        linear-gradient(135deg, #020617 0%, #0f172a 30%, #111827 100%);
                    min-height: 100vh;
                }}

                a {{ text-decoration: none; color: inherit; }}

                .nav {{
                    max-width: 1180px;
                    margin: 0 auto;
                    padding: 24px 28px 10px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}

                .brand {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-weight: 700;
                    letter-spacing: 0.04em;
                }}

                .brand-mark {{
                    width: 14px;
                    height: 14px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--primary), var(--secondary));
                    box-shadow: 0 0 20px rgba(96, 165, 250, 0.9);
                }}

                .nav-actions {{
                    display: flex;
                    align-items: center;
                    gap: 14px;
                }}

                .btn {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0.9rem 1.5rem;
                    border-radius: 999px;
                    border: 1px solid var(--line);
                    font-weight: 600;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    cursor: pointer;
                }}

                .btn:hover {{ transform: translateY(-1px); }}

                .btn-primary {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
                    color: white;
                    border-color: transparent;
                    box-shadow: 0 18px 35px rgba(37, 99, 235, 0.35);
                }}

                .btn-secondary {{
                    background: rgba(148, 163, 184, 0.04);
                    border-color: rgba(148, 163, 184, 0.25);
                }}

                .page {{
                    max-width: 1180px;
                    margin: 0 auto;
                    padding: 24px 28px 60px;
                }}

                .hero {{
                    display: grid;
                    grid-template-columns: 1.2fr 0.8fr;
                    gap: 28px;
                    align-items: center;
                    min-height: 70vh;
                }}

                .hero-copy, .panel, .auth-card {{
                    background: var(--card);
                    border: 1px solid var(--line);
                    border-radius: 28px;
                    backdrop-filter: blur(8px);
                    box-shadow: var(--shadow);
                }}

                .hero-copy {{
                    padding: 48px 40px;
                }}

                .eyebrow {{
                    display: inline-flex;
                    padding: 0.45rem 0.9rem;
                    border-radius: 999px;
                    border: 1px solid rgba(96, 165, 250, 0.45);
                    background: rgba(96, 165, 250, 0.09);
                    color: #bfdbfe;
                    font-size: 0.8rem;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }}

                h1 {{
                    margin: 20px 0 18px;
                    font-size: clamp(2.4rem, 5vw, 4.5rem);
                    line-height: 1.02;
                    letter-spacing: -0.04em;
                }}

                .lead {{
                    margin: 0 0 26px;
                    color: var(--muted);
                    font-size: 1.12rem;
                    line-height: 1.7;
                    max-width: 44rem;
                }}

                .hero-actions {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                    margin-bottom: 30px;
                }}

                .stats {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 18px;
                }}

                .stat {{
                    min-width: 120px;
                    padding: 14px 16px;
                    border-radius: 16px;
                    background: rgba(15, 23, 42, 0.7);
                    border: 1px solid var(--line);
                }}

                .stat strong {{
                    display: block;
                    font-size: 1.5rem;
                    margin-bottom: 6px;
                }}

                .stat span {{
                    color: var(--muted);
                    font-size: 0.8rem;
                }}

                .panel {{
                    padding: 24px;
                }}

                .mini-card {{
                    background: linear-gradient(160deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.88));
                    border: 1px solid rgba(96, 165, 250, 0.3);
                    border-radius: 22px;
                    padding: 18px;
                    margin-bottom: 14px;
                }}

                .mini-card h3 {{
                    margin: 0 0 8px;
                    font-size: 1rem;
                }}

                .mini-card p {{
                    margin: 0;
                    color: var(--muted);
                    line-height: 1.6;
                }}

                .auth-shell {{
                    min-height: 80vh;
                    display: grid;
                    place-items: center;
                    padding: 40px 20px;
                }}

                .auth-card {{
                    width: min(100%, 440px);
                    background: var(--card-strong);
                    padding: 32px 28px;
                }}

                .auth-card h2 {{
                    margin: 16px 0 8px;
                    font-size: 2rem;
                }}

                .auth-card .sub {{
                    color: var(--muted);
                    margin-bottom: 22px;
                    line-height: 1.6;
                }}

                .auth-form {{
                    display: flex;
                    flex-direction: column;
                    gap: 18px;
                }}

                .field {{
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}

                .field label {{
                    color: #dbeafe;
                    font-size: 0.85rem;
                    font-weight: 600;
                }}

                .field input {{
                    width: 100%;
                    padding: 0.9rem 1rem;
                    background: rgba(15, 23, 42, 0.9);
                    border: 1px solid rgba(148, 163, 184, 0.35);
                    border-radius: 12px;
                    color: var(--text);
                    font-size: 1rem;
                    outline: none;
                }}

                .field input:focus {{
                    border-color: rgba(96, 165, 250, 0.8);
                    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.18);
                }}

                .auth-form button {{
                    margin-top: 8px;
                    width: 100%;
                    padding: 1rem 1.2rem;
                    border: none;
                    border-radius: 12px;
                    font-size: 1rem;
                    font-weight: 700;
                    color: white;
                    background: linear-gradient(135deg, var(--primary), var(--primary-strong));
                    box-shadow: 0 16px 36px rgba(37, 99, 235, 0.35);
                    cursor: pointer;
                }}

                .divider {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin: 18px 0 12px;
                    color: var(--muted);
                    font-size: 0.8rem;
                    text-transform: uppercase;
                }}

                .divider::before, .divider::after {{
                    content: "";
                    flex: 1;
                    height: 1px;
                    background: rgba(148, 163, 184, 0.2);
                }}

                .link-row {{
                    text-align: center;
                    margin-top: 20px;
                    color: var(--muted);
                }}

                .link-row a {{
                    color: #93c5fd;
                    font-weight: 600;
                }}

                .message {{
                    padding: 22px 20px;
                    border-radius: 18px;
                    border: 1px solid var(--line);
                    margin-bottom: 22px;
                }}

                .message.success {{
                    background: rgba(34, 197, 94, 0.08);
                    border-color: rgba(34, 197, 94, 0.35);
                }}

                .message.error {{
                    background: rgba(248, 113, 113, 0.08);
                    border-color: rgba(248, 113, 113, 0.32);
                }}

                .message h3 {{
                    margin: 0 0 8px;
                    font-size: 1.5rem;
                }}

                .message p {{
                    margin: 0;
                    color: var(--muted);
                    line-height: 1.6;
                }}

                @media (max-width: 860px) {{
                    .hero {{
                        grid-template-columns: 1fr;
                    }}

                    .nav {{
                        flex-wrap: wrap;
                        gap: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
    )


@app.on_event("startup")
def startup() -> None:
    create_db()


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    content = """
        <nav class="nav">
            <div class="brand"><span class="brand-mark"></span> FB CLONE</div>
            <div class="nav-actions">
                <a class="btn btn-secondary" href="/signin">Sign in</a>
                <a class="btn btn-primary" href="/signup">Sign up</a>
            </div>
        </nav>
        <main class="page">
            <section class="hero">
                <div class="hero-copy">
                    <span class="eyebrow">Community hub</span>
                    <h1>Connect with your people.</h1>
                    <p class="lead">
                        Share your ideas, discover what matters, and build a more meaningful online community with a cleaner,
                        faster social experience.
                    </p>
                    <div class="hero-actions">
                        <a class="btn btn-primary" href="/signup">Create account</a>
                        <a class="btn btn-secondary" href="/signin">Already a member</a>
                    </div>
                    <div class="stats">
                        <div class="stat"><strong>12M+</strong><span>Active users</span></div>
                        <div class="stat"><strong>4.9/5</strong><span>Average rating</span></div>
                        <div class="stat"><strong>24/7</strong><span>Community support</span></div>
                    </div>
                </div>
                <aside class="panel">
                    <div class="mini-card">
                        <h3>Daily updates</h3>
                        <p>Stay in the loop with short updates, milestones, and trending conversations from your network.</p>
                    </div>
                    <div class="mini-card">
                        <h3>Private messaging</h3>
                        <p>Keep talks personal and meaningful with secure chat threads and reaction-driven engagement.</p>
                    </div>
                    <div class="mini-card">
                        <h3>Smart communities</h3>
                        <p>Build groups around interests, projects, and shared goals with effortless discovery tools.</p>
                    </div>
                </aside>
            </section>
        </main>
    """
    return page_shell("FB Clone | Social Experience", content)


@app.get("/signin", response_class=HTMLResponse)
def signin_page() -> HTMLResponse:
    content = """
        <div class="auth-shell">
            <div class="auth-card">
                <div class="brand"><span class="brand-mark"></span> FB CLONE</div>
                <h2>Welcome back</h2>
                <p class="sub">Sign in to continue to your dashboard and community updates.</p>
                <form class="auth-form" method="post" action="/auth/signin">
                    <div class="field">
                        <label for="email">Email</label>
                        <input id="email" name="email" type="email" placeholder="you@example.com" required />
                    </div>
                    <div class="field">
                        <label for="password">Password</label>
                        <input id="password" name="password" type="password" placeholder="Enter your password" required />
                    </div>
                    <button type="submit">Sign in</button>
                </form>
                <div class="divider">or</div>
                <div class="link-row">
                    New here? <a href="/signup">Create an account</a>
                </div>
            </div>
        </div>
    """
    return page_shell("Sign in", content)


@app.get("/signup", response_class=HTMLResponse)
def signup_page() -> HTMLResponse:
    content = """
        <div class="auth-shell">
            <div class="auth-card">
                <div class="brand"><span class="brand-mark"></span> FB CLONE</div>
                <h2>Create account</h2>
                <p class="sub">Join your network in minutes and start sharing instantly.</p>
                <form class="auth-form" method="post" action="/auth/signup">
                    <div class="field">
                        <label for="name">Full name</label>
                        <input id="name" name="name" type="text" placeholder="Jane Doe" required />
                    </div>
                    <div class="field">
                        <label for="email">Email</label>
                        <input id="email" name="email" type="email" placeholder="you@example.com" required />
                    </div>
                    <div class="field">
                        <label for="password">Password</label>
                        <input id="password" name="password" type="password" placeholder="Create a password" required />
                    </div>
                    <button type="submit">Sign up</button>
                </form>
                <div class="divider">or</div>
                <div class="link-row">
                    Already have an account? <a href="/signin">Sign in</a>
                </div>
            </div>
        </div>
    """
    return page_shell("Sign up", content)


@app.post("/auth/signin", response_class=HTMLResponse)
def handle_signin(email: str = Form(...), password: str = Form(...)) -> HTMLResponse:
    if "@" not in email or len(password) < 6:
        content = """
            <div class="auth-shell">
                <div class="auth-card">
                    <div class="message error">
                        <h3>Oops</h3>
                        <p>Please enter a valid email and a password with at least 6 characters.</p>
                    </div>
                    <a class="btn btn-primary" href="/signin">Try again</a>
                </div>
            </div>
        """
        return page_shell("Sign in error", content)

    content = f"""
        <div class="auth-shell">
            <div class="auth-card">
                <div class="message success">
                    <h3>Signed in successfully</h3>
                    <p>Welcome back, {email}. Your community is ready.</p>
                </div>
                <a class="btn btn-primary" href="/">Go to home</a>
            </div>
        </div>
    """
    return page_shell("Welcome back", content)


@app.post("/auth/signup", response_class=HTMLResponse)
def handle_signup(name: str = Form(...), email: str = Form(...), password: str = Form(...)) -> HTMLResponse:
    if not name.strip() or "@" not in email or len(password) < 6:
        content = """
            <div class="auth-shell">
                <div class="auth-card">
                    <div class="message error">
                        <h3>Unable to create account</h3>
                        <p>Please provide a full name, a valid email, and a password with at least 6 characters.</p>
                    </div>
                    <a class="btn btn-primary" href="/signup">Try again</a>
                </div>
            </div>
        """
        return page_shell("Sign up error", content)

    content = f"""
        <div class="auth-shell">
            <div class="auth-card">
                <div class="message success">
                    <h3>Account created</h3>
                    <p>Hi {name.strip()}, your profile is ready. You can now sign in and start connecting.</p>
                </div>
                <a class="btn btn-primary" href="/signin">Continue to sign in</a>
            </div>
        </div>
    """
    return page_shell("Account created", content)


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard() -> HTMLResponse:
    stats = admin_overview()
    categories = list_categories()
    products = list_products()[:5]
    content = f"""
        <nav class="nav">
            <div class="brand"><span class="brand-mark"></span> ADMIN PANEL</div>
            <div class="nav-actions">
                <a class="btn btn-secondary" href="/">Website</a>
                <a class="btn btn-primary" href="/signin">Logout</a>
            </div>
        </nav>
        <main class="page">
            <section class="hero" style="grid-template-columns: 1fr; min-height: auto;">
                <div class="hero-copy">
                    <span class="eyebrow">Dashboard overview</span>
                    <h1 style="font-size: clamp(2rem, 4vw, 3rem);">Store performance at a glance</h1>
                    <p class="lead">Manage product visibility, inventory, and category health from one place.</p>
                    <div class="stats">
                        <div class="stat"><strong>{stats['total_products']}</strong><span>Total products</span></div>
                        <div class="stat"><strong>{stats['featured_products']}</strong><span>Featured</span></div>
                        <div class="stat"><strong>{stats['out_of_stock']}</strong><span>Out of stock</span></div>
                        <div class="stat"><strong>{stats['total_categories']}</strong><span>Categories</span></div>
                    </div>
                </div>
            </section>

            <section class="panel" style="margin-top: 20px; padding: 24px;">
                <h3 style="margin-top: 0;">Top categories</h3>
                <div class="stats" style="margin-top: 18px;">
                    {''.join(f'<div class="stat"><strong>{len(category.get("name", ""))}</strong><span>{category.get("name", "")}</span></div>' for category in categories[:4])}
                </div>
            </section>

            <section class="panel" style="margin-top: 20px; padding: 24px;">
                <h3 style="margin-top: 0;">Newest inventory</h3>
                <div style="display: grid; gap: 12px; margin-top: 16px;">
                    {''.join(
                        f'<div class="mini-card"><h3>{product["name"]}</h3><p>{product["category_name"]} · ${product["price"]} · Stock: {product["stock"]}</p></div>'
                        for product in products
                    )}
                </div>
            </section>
        </main>
    """
    return page_shell("Admin Dashboard", content)


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

