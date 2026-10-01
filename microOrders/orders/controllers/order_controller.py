import requests
from flask import Blueprint, request, jsonify, session
from orders.models.order_model import Order
from db.db import db
from consul_helper import discover_service


order_controller = Blueprint('order_controller', __name__)
VALID_STATUSES = ['pending', 'confirmed', 'cancelled']

@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders])


@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@order_controller.route('/api/orders', methods=['POST'])
def create_order():
    """
    Endpoint para crear una nueva orden.
    Recibe un JSON con una lista de productos con sus respectivos IDs y cantidades.
    Descubre el microservicio de usuarios vía Consul para obtener los datos del
    usuario autenticado a partir de su user_id de sesión.
    Descubre el microservicio de productos vía Consul para verificar disponibilidad
    y actualizar inventario.
    """
    data = request.get_json()

    user_id = session.get('user_id')

    if user_id:
        try:
            users_url = discover_service('micro-users')
            user_resp = requests.get(f'{users_url}/api/users/{user_id}', timeout=5)
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                user_name  = user_data.get('username')
                user_email = user_data.get('email')
            else:
                return jsonify({'message': f'Usuario {user_id} no encontrado en el servicio de usuarios'}), 404
        except RuntimeError as exc:
            return jsonify({'message': str(exc)}), 500
        except requests.exceptions.RequestException as exc:
            return jsonify({'message': f'Error al contactar microservicio de usuarios: {exc}'}), 500
    else:
        fallback = data.get('user', {})
        user_name  = fallback.get('name') or fallback.get('username')
        user_email = fallback.get('email')

    if not user_name or not user_email:
        return jsonify({'message': 'Información de usuario inválida'}), 401

    products = data.get('products')
    if not products or not isinstance(products, list):
        return jsonify({'message': 'Falta o es inválida la información de los productos'}), 400

    try:
        products_url = discover_service('micro-products')
    except RuntimeError as exc:
        return jsonify({'message': str(exc)}), 500

    order_items = []
    total = 0.0

    for item in products:
        product_id = item.get('id')
        requested_qty = int(item.get('quantity', 0))

        if not product_id or requested_qty <= 0:
            return jsonify({'message': f'Datos inválidos para producto {product_id}'}), 400

        # Consultar microservicio de productos
        try:
            resp = requests.get(
                f'{products_url}/api/products/{product_id}',
                timeout=5
            )
        except requests.exceptions.RequestException as e:
            return jsonify({'message': f'Error al contactar microservicio de productos: {str(e)}'}), 500

        if resp.status_code == 404:
            return jsonify({'message': f'Producto {product_id} no existe'}), 404

        if resp.status_code != 200:
            return jsonify({'message': 'Error interno al consultar productos'}), 500

        product_data = resp.json()

        if product_data['quantity'] < requested_qty:
            return jsonify({
                'message': f'Inventario insuficiente para "{product_data["name"]}". '
                           f'Disponible: {product_data["quantity"]}, Solicitado: {requested_qty}'
            }), 409

        subtotal = product_data['price'] * requested_qty
        total += subtotal

        order_items.append({
            'id': product_data['id'],
            'name': product_data['name'],
            'unit_price': product_data['price'],
            'quantity': requested_qty,
            'subtotal': subtotal
        })

    for item in order_items:
        try:
            resp = requests.get(
                f'{products_url}/api/products/{item["id"]}',
                timeout=5
            )
            current_qty = resp.json()['quantity']
            new_qty = current_qty - item['quantity']

            update_resp = requests.put(
                f'{products_url}/api/products/{item["id"]}',
                json={'quantity': new_qty},
                timeout=5
            )
            if update_resp.status_code != 200:
                return jsonify({'message': f'Error al actualizar inventario del producto {item["id"]}'}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({'message': f'Error al actualizar inventario: {str(e)}'}), 500

    try:
        new_order = Order(
            user_name=user_name,
            user_email=user_email,
            total=round(total, 2),
            products=order_items,
            status='pending'
        )
        db.session.add(new_order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error interno al guardar la orden: {str(e)}'}), 500

    return jsonify({'message': 'Orden creada exitosamente', 'order_id': new_order.id}), 201


@order_controller.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({
            'message': 'El campo status es obligatorio'
        }), 400

    new_status = data['status']

    if new_status not in VALID_STATUSES:
        return jsonify({
            'message': 'Estado inválido',
            'allowed_statuses': VALID_STATUSES
        }), 400

    order = Order.query.get_or_404(order_id)

    # Solo permitimos cambiar una orden pendiente
    if order.status != 'pending':
        return jsonify({
            'message': 'Solo las órdenes pendientes pueden cambiar de estado'
        }), 400

    order.status = new_status

    try:
        db.session.commit()

        return jsonify({
            'message': 'Estado actualizado correctamente',
            'order_id': order.id,
            'status': order.status
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'message': f'Error al actualizar el estado: {str(e)}'
        }), 500
