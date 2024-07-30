from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/cart_db')

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client.cart_db
carts_collection = db.carts

def create_cart(data):
    try:
        result = carts_collection.insert_one(data)
        cart = carts_collection.find_one({'_id': result.inserted_id})
        cart['_id'] = str(cart['_id'])
        return cart
    except Exception as e:
        raise Exception(f"Error creating cart: {e}")

def get_all_carts():
    try:
        carts = list(carts_collection.find())
        for cart in carts:
            cart['_id'] = str(cart['_id'])
        return carts
    except Exception as e:
        raise Exception(f"Error getting all carts: {e}")

def get_cart(cart_id):
    try:
        cart = carts_collection.find_one({'_id': ObjectId(cart_id)})
        if cart:
            cart['_id'] = str(cart['_id'])
        return cart
    except Exception as e:
        raise Exception(f"Error getting cart: {e}")

def update_cart(cart_id, data):
    try:
        result = carts_collection.update_one({'_id': ObjectId(cart_id)}, {'$set': data})
        if result.matched_count:
            updated_cart = carts_collection.find_one({'_id': ObjectId(cart_id)})
            updated_cart['_id'] = str(updated_cart['_id'])
            return updated_cart
        return None
    except Exception as e:
        raise Exception(f"Error updating cart: {e}")

def delete_cart(cart_id):
    try:
        result = carts_collection.delete_one({'_id': ObjectId(cart_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise Exception(f"Error deleting cart: {e}")
