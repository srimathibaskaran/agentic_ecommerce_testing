from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = "local-demo-only-secret"

PRODUCTS = [
    {"id": "p101", "name": "Wireless Mouse", "price": 15.99, "description": "Comfortable wireless mouse"},
    {"id": "p102", "name": "Mechanical Keyboard", "price": 49.99, "description": "Compact mechanical keyboard"},
    {"id": "p103", "name": "USB-C Hub", "price": 24.50, "description": "Multiport USB-C hub"},
]

BASE = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | Demo Shop</title>
<style>
body{font-family:Arial,sans-serif;max-width:980px;margin:32px auto;padding:0 18px;color:#222}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #ddd;padding-bottom:14px}
nav a{margin-left:14px} .card{border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0}
button{padding:9px 13px;cursor:pointer} input{padding:9px;margin:5px 0}
.notice{background:#eef7ee;padding:10px;border-radius:5px}.error{background:#fff0f0;padding:10px;border-radius:5px}
</style></head><body>
<header><h1><a href="{{ url_for('home') }}">Demo Shop</a></h1>
<nav><a href="{{ url_for('products') }}">Products</a><a href="{{ url_for('cart') }}">Cart ({{ cart_count }})</a>
{% if session.get('user') %}<a href="{{ url_for('logout') }}">Logout</a>{% else %}<a href="{{ url_for('login') }}">Login</a>{% endif %}</nav></header>
<main>{{ body|safe }}</main></body></html>
"""

def render_page(title, body, **context):
    cart = session.get("cart", {})
    count = sum(cart.values())
    return render_template_string(BASE, title=title, body=render_template_string(body, **context),
                                  cart_count=count, session=session)

@app.get("/")
def home():
    body = """<h2>Welcome to the Demo Shop</h2>
    <p>This local test shop is for browser automation practice. No real payments are processed.</p>
    <p><a href="{{ url_for('products') }}">Browse products</a></p>"""
    return render_page("Home", body)

@app.get("/login")
def login():
    error = request.args.get("error", "")
    body = """<h2>Login</h2>
    {% if error %}<p class="error" role="alert">{{ error }}</p>{% endif %}
    <form method="post">
      <label for="username">Username</label><br><input id="username" name="username" autocomplete="username"><br>
      <label for="password">Password</label><br><input id="password" name="password" type="password" autocomplete="current-password"><br>
      <button type="submit">Sign in</button>
    </form><p>Demo credentials: demo / demo123</p>"""
    return render_page("Login", body, error=error)

@app.post("/login")
def login_submit():
    if request.form.get("username") == "demo" and request.form.get("password") == "demo123":
        session["user"] = "demo"
        return redirect(url_for("products"))
    return redirect(url_for("login", error="Invalid username or password"))

@app.get("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.get("/products")
def products():
    q = request.args.get("q", "").strip().lower()
    filtered = [p for p in PRODUCTS if q in p["name"].lower()] if q else PRODUCTS
    body = """<h2>Products</h2>
    <form method="get"><label for="search">Search products</label>
    <input id="search" name="q" value="{{ q }}" placeholder="Search products">
    <button type="submit">Search</button></form>
    {% if products %}{% for p in products %}
      <section class="card" data-product-id="{{ p.id }}"><h3>{{ p.name }}</h3>
      <p>{{ p.description }}</p><p>Price: ${{ "%.2f"|format(p.price) }}</p>
      <form method="post" action="{{ url_for('add_to_cart', product_id=p.id) }}">
      <button type="submit">Add to cart</button></form></section>
    {% endfor %}{% else %}<p role="status">No products found</p>{% endif %}"""
    return render_page("Products", body, products=filtered, q=q)

@app.post("/cart/add/<product_id>")
def add_to_cart(product_id):
    if product_id not in {p["id"] for p in PRODUCTS}:
        return "Product not found", 404
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.get("/cart")
def cart():
    cart_data = session.get("cart", {})
    items = []
    total = 0
    for p in PRODUCTS:
        qty = cart_data.get(p["id"], 0)
        if qty:
            items.append({**p, "quantity": qty, "line_total": qty * p["price"]})
            total += qty * p["price"]
    body = """<h2>Your Cart</h2>
    {% if items %}<table border="1" cellpadding="8" cellspacing="0"><thead><tr><th>Product</th><th>Quantity</th><th>Line total</th></tr></thead><tbody>
    {% for item in items %}<tr><td>{{ item.name }}</td><td>{{ item.quantity }}</td><td>${{ "%.2f"|format(item.line_total) }}</td></tr>{% endfor %}
    </tbody></table><p><strong>Cart total: ${{ "%.2f"|format(total) }}</strong></p>
    <a href="{{ url_for('checkout') }}">Proceed to checkout</a>
    {% else %}<p role="status">Your cart is empty</p>{% endif %}"""
    return render_page("Cart", body, items=items, total=total)

@app.get("/checkout")
def checkout():
    if not session.get("cart"):
        return redirect(url_for("cart"))
    body = """<h2>Checkout</h2><p>This is a simulated checkout. No payment details are requested.</p>
    <form method="post"><label for="email">Contact email</label><br>
    <input id="email" name="email" type="email" required value="demo@example.com"><br>
    <button type="submit">Place demo order</button></form>"""
    return render_page("Checkout", body)

@app.post("/checkout")
def checkout_submit():
    if not session.get("cart"):
        return redirect(url_for("cart"))
    session["cart"] = {}
    body = """<h2>Order confirmed</h2><p role="status">Demo order placed successfully.</p>
    <p>No real order or payment was created.</p><a href="{{ url_for('products') }}">Continue shopping</a>"""
    return render_page("Confirmation", body)

if __name__ == "__main__":
    import os
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
