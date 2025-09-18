from flask import Flask, jsonify, request, url_for
from sqlalchemy import func
from models import db, Product, Category, Order

app = Flask(__name__)  
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

def ok(data=None):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    return jsonify(payload)

def err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

# CRUD CREATES
@app.post("/categories")
def create_category():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return err("El campo 'name' es obligatorio", 400)
    if not description:
        return err("El campo 'description' es obligatorio", 400)

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return ok(category.to_dict(), message="Categoría creada"), 201


@app.post("/products")
def create_product():
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")
    category_id = data.get("category_id")

    if not name:
        return err("El campo 'name' es obligatorio", 400)
    if price is None:
        return err("El campo 'price' es obligatorio", 400)
    if stock is None or stock <= 0:
        return err("El campo 'stock' es obligatorio o no hay stock suficiente del producto", 400)
    if not category_id:
        return err("El campo 'category_id' es obligatorio", 400)

    category = Category.query.get(category_id)
    if not category:
        return err("La categoría no existe", 404)

    product = Product(name=name, price=price, stock=stock, category_id=category.id)
    db.session.add(product)
    db.session.commit()
    return ok(product.to_dict(), message="Producto creado"), 201


@app.post("/orders")
def create_order():
    data = request.get_json() or {}
    date = data.get("date")
    client = data.get("client")
    product_ids = data.get("products", [])

    if not date:
        return err("El campo 'fecha' es obligatorio", 400)
    if not client:
        return err("El campo 'client' es obligatorio", 400)
    order = Order(date=date, client=client)
    db.session.add(order)

    if product_ids:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        for product in products:
            product.order = order

    order.total_amount = sum(product.price or 0 for product in order.products)
    db.session.commit()
    return ok(order.to_dict(), message="Orden creada"), 201

# CRUD DELETES 
@app.delete("/products/deleteproduct")
def delete_product():
    name = request.args.get("name")
    if not name:
        return err("El parametro 'name' es obligatorio", 400)
    product = Product.query.filter_by(name=name).first()
    if not product:
        return err("El producto no existe", 404)
    db.session.delete(product)
    db.session.commit()
    return ok(message="Producto eliminado"), 200

@app.delete("/categories/deletecategory")
def delete_category():
    name = request.args.get("name")
    if not name:
        return err("El parametro 'name' es obligatorio", 400)
    category = Category.query.filter_by(name=name).first()
    if not category:
        return err("La categoría no existe", 404)
    db.session.delete(category)
    db.session.commit()
    return ok(message="Categoría eliminada"), 200

@app.delete("/orders/deleteorder")
def delete_order():
    date = request.args.get("date")
    client = request.args.get("client")
    if not date or not client:
        return err("Los datos 'date' y 'client' son obligatorios", 400)
    order = Order.query.filter(Order.date == date, Order.client == client).first()
    if not order:
        return err("La orden no existe", 404)
    db.session.delete(order)
    db.session.commit()
    return ok(message="Orden eliminada"), 200

# CRUDS CONSULTAS
@app.get("/products/allproducts")
def list_products():
    page = request.args.get("page", 1, type=int) 
    per_page = request.args.get("per_page", 5, type=int) 
    sort = request.args.get("sort", "name")
    sort_map = {
        "name": func.lower(Product.name).asc(),
    }
    order_clause = sort_map.get(sort, func.lower(Product.name).asc())
    query = Product.query.order_by(order_clause)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return ok(
        [product.to_dict() for product in pagination.items],
        page=pagination.page,
        per_page=pagination.per_page,
        total_items=pagination.total,
        total_pages=pagination.pages,
    ), 200

@app.get("/orders/allorders")
def list_orders():
    page = request.args.get("page", 1, type=int) 
    per_page = request.args.get("per_page", 5, type=int) 
    sort = request.args.get("sort", "date")
    sort_map = {
        "date": Order.date.asc(),
    }
    order_clause = sort_map.get(sort, Order.date.asc())
    query = Order.query.order_by(order_clause)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return ok(
        [order.to_dict() for order in pagination.items],
        page=pagination.page,
        per_page=pagination.per_page,
        total_items=pagination.total,
        total_pages=pagination.pages,
    ), 200

@app.get("/products/<int:product_id>")
def read_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return err("El producto no existe", 404)
    return jsonify({"success": True, "data": product.to_dict()}), 200

@app.get("/orders/<int:order_id>")
def read_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return err("La orden no existe ", 404)
    return jsonify({"success": True, "data": order.to_dict()}), 200
