from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/product_db')

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client.productdb
products_collection = db.products

def create_product(data):
    try:
        result = products_collection.insert_one(data)
        product = products_collection.find_one({'_id': result.inserted_id})
        product['_id'] = str(product['_id'])
        return product
    except Exception as e:
        raise Exception(f"Error creating product: {e}")

def get_all_products():
    try:
        products = list(products_collection.find())
        for product in products:
            product['_id'] = str(product['_id'])
        return products
    except Exception as e:
        raise Exception(f"Error getting all products: {e}")

def get_product(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if product:
            product['_id'] = str(product['_id'])
        return product
    except Exception as e:
        raise Exception(f"Error getting product: {e}")

def update_product(product_id, data):
    try:
        result = products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': data})
        if result.matched_count:
            updated_product = products_collection.find_one({'_id': ObjectId(product_id)})
            updated_product['_id'] = str(updated_product['_id'])
            return updated_product
        return None
    except Exception as e:
        raise Exception(f"Error updating product: {e}")

def delete_product(product_id):
    try:
        result = products_collection.delete_one({'_id': ObjectId(product_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise Exception(f"Error deleting product: {e}")