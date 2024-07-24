from flask import Blueprint, request, jsonify
from services import create_order, get_all_orders, get_order, update_order, delete_order

order_bp = Blueprint('order_bp', __name__)


@order_bp.route('/', methods=['POST'])
def create_order_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        order = create_order(data)
        return jsonify(order), 201
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@order_bp.route('/', methods=['GET'])
def get_all_orders_route():
    try:
        orders = get_all_orders()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@order_bp.route('/<order_id>', methods=['GET'])
def get_order_route(order_id):
    try:
        order = get_order(order_id)
        if order:
            return jsonify(order), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@order_bp.route('/<order_id>', methods=['PUT'])
def update_order_route(order_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        updated_order = update_order(order_id, data)
        if updated_order:
            return jsonify(updated_order), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@order_bp.route('/<order_id>', methods=['DELETE'])
def delete_order_route(order_id):
    try:
        result = delete_order(order_id)
        if result:
            return jsonify({'message': 'Order deleted'}), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
