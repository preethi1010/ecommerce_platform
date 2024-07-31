from pymongo import MongoClient
from pykafka import KafkaClient
import json
from bson.objectid import ObjectId
import os
from datetime import datetime

# Configuration
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/cart_db')

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client.cart_db
carts_collection = db.carts

# Kafka client setup
kafka_client = KafkaClient(hosts='kafka:9092')
topic = kafka_client.topics['cart_topic']

def create_cart(data):
    try:
        result = carts_collection.insert_one(data)
        cart = carts_collection.find_one({'_id': result.inserted_id})  
                
        try: 
            cart_message = {
            'event': 'cart_updated',
            'user_id': str(cart.get('user_id')),
            'cart': {
                'product_id': str(cart.get('product_id')),
                'quantity': cart.get('quantity'),
                'cart_id': str(cart['_id']) 
            }
        }
            # Produce message to Kafka
            with topic.get_producer() as producer:
                producer.produce(json.dumps(cart_message).encode('utf-8'))
        except Exception as e:
            raise Exception(f"Error sending topic message: {e}")
            
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
