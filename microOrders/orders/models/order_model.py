import json
from db.db import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float, nullable=False)
    products = db.Column(db.Text, nullable=False)
    status = db.Column(
            db.String(20),
            nullable=False,
            default='pending'
            )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_name, user_email, total, products, status='pending'):
        self.user_name = user_name
        self.user_email = user_email
        self.total = total
        self.products = json.dumps(products)
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'total': self.total,
            'products': json.loads(self.products),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
