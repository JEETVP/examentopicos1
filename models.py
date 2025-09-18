from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)   
    stock= db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", back_populates="products")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category_id": self.category_id,
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    products = db.relationship("Product",back_populates="category",cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "products": [product.id for product in self.products],
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    client = db.Column(db.String(120))
    total_amount = db.Column(db.Integer, default=0)
    products = db.relationship("Product",back_populates="order",foreign_keys=[Product.order_id]
    )

    def total(self):
        self.total_amount = sum((product.price or 0) for product in self.products)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "client": self.client,
            "products": [product.id for product in self.products],
            "total_amount": self.total_amount
        }
