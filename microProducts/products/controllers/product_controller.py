from flask import Blueprint, request, jsonify
from products.models.product_model import Products
from db.db import db


product_controller = Blueprint('product_controller', __name__)


@product_controller.route('/api/products', methods=['GET'])
def get_all_products():
    products = Products.query.all()
    result = [
        {'id': p.id, 'name': p.name, 'price': p.price, 'quantity': p.quantity}
        for p in products
    ]
    return jsonify(result)


@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Products.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    })


@product_controller.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'message': 'Datos incompletos'}), 400
    new_product = Products(
        name=data['name'],
        price=data['price'],
        quantity=data['quantity']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201


@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Products.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = float(data.get('price', product.price))
    product.quantity = int(data.get('quantity', product.quantity))
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})


@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
