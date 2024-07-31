from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/order_db')

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client.orderdb
orders_collection = db.orders
def create_order(data):
    try:
        result = orders_collection.insert_one(data)
        order = orders_collection.find_one({'_id': result.inserted_id})
        order['_id'] = str(order['_id'])
        return order
    except Exception as e:
        raise Exception(f"Error creating order: {e}")

def get_all_orders():
    try:
        orders = list(orders_collection.find())
        for order in orders:
            order['_id'] = str(order['_id'])
        return orders
    except Exception as e:
        raise Exception(f"Error getting all orders: {e}")

def get_order(order_id):
    try:
        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if order:
            order['_id'] = str(order['_id'])
        return order
    except Exception as e:
        raise Exception(f"Error getting order: {e}")

def update_order(order_id, data):
    try:
        result = orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': data})
        if result.matched_count:
            updated_order = orders_collection.find_one({'_id': ObjectId(order_id)})
            updated_order['_id'] = str(updated_order['_id'])
            return updated_order
        return None
    except Exception as e:
        raise Exception(f"Error updating order: {e}")

def delete_order(order_id):
    try:
        result = orders_collection.delete_one({'_id': ObjectId(order_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise Exception(f"Error deleting order: {e}")
