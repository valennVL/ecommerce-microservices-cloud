import os
from flask import Flask, jsonify
from orders.controllers.order_controller import order_controller
from db.db import db
from flask_cors import CORS
from consul_helper import register_service

app = Flask(__name__)
app.secret_key = 'secret123'
app.config.from_object('config.Config')
db.init_app(app)

app.register_blueprint(order_controller)
CORS(app, supports_credentials=True)


@app.route('/health')
def health():
    """Health check endpoint used by Consul."""
    return jsonify({'status': 'healthy', 'service': 'micro-orders'}), 200


with app.app_context():
    db.create_all()
    # Register with Consul
    service_host = os.environ.get('SERVICE_HOST', 'localhost')
    register_service(
        service_name='micro-orders',
        service_id='micro-orders-1',
        address=service_host,
        port=5004,
    )

if __name__ == '__main__':
    app.run()
