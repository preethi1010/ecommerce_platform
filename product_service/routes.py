from flask import Blueprint, request, jsonify
from services import create_product, get_all_products, get_product, update_product, delete_product
import logging

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=['POST'])
def create_product_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        product = create_product(data)
        return jsonify(product), 201
    except Exception as e:
        logging.error(f"Error creating product: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@product_bp.route('/', methods=['GET'])
def get_all_products_route():
    try:
        products = get_all_products()
        return jsonify(products), 200
    except Exception as e:
        logging.error(f"Error getting all products: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product_route(product_id):
    try:
        product = get_product(product_id)
        return jsonify(product), 200 if product else 404
    except Exception as e:
        logging.error(f"Error getting product: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@product_bp.route('/<product_id>', methods=['PUT'])
def update_product_route(product_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        updated_product = update_product(product_id, data)
        return jsonify(updated_product), 200 if updated_product else 404
    except Exception as e:
        logging.error(f"Error updating product: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@product_bp.route('/<product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    try:
        result = delete_product(product_id)
        return jsonify({'message': 'Product deleted'}), 200 if result else 404
    except Exception as e:
        logging.error(f"Error deleting product: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
