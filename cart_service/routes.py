from flask import Blueprint, request, jsonify
from services import create_cart, get_all_carts, get_cart, update_cart, delete_cart
import logging

cart_bp = Blueprint('cart_bp', __name__)

logger = logging.getLogger(__name__)

@cart_bp.route('/', methods=['POST'])
def create_cart_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        cart = create_cart(data)
        return jsonify(cart), 201
    except Exception as e:
        logger.error(f"Error creating cart: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@cart_bp.route('/', methods=['GET'])
def get_all_carts_route():
    try:
        carts = get_all_carts()
        return jsonify(carts), 200
    except Exception as e:
        logger.error(f"Error getting all carts: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@cart_bp.route('/<cart_id>', methods=['GET'])
def get_cart_route(cart_id):
    try:
        cart = get_cart(cart_id)
        if cart:
            return jsonify(cart), 200
        else:
            return jsonify({"error": "Cart not found"}), 404
    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@cart_bp.route('/<cart_id>', methods=['PUT'])
def update_cart_route(cart_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        updated_cart = update_cart(cart_id, data)
        if updated_cart:
            return jsonify(updated_cart), 200
        else:
            return jsonify({"error": "Cart not found"}), 404
    except Exception as e:
        logger.error(f"Error updating cart: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@cart_bp.route('/<cart_id>', methods=['DELETE'])
def delete_cart_route(cart_id):
    try:
        result = delete_cart(cart_id)
        if result:
            return jsonify({'message': 'Cart deleted'}), 200
        else:
            return jsonify({"error": "Cart not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting cart: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
