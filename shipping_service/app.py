from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import requests
from bson.json_util import dumps, loads

app = Flask(__name__)

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['shipping_db']
shipments_collection = db['shipments']

# URL for the notification service
NOTIFICATION_SERVICE_URL = 'http://172.29.0.4:5000/notification'

def notify_service(shipment_id, message, notification_type):
    notification_data = {
        'shipment_id': shipment_id,
        'message': message,
        'type': notification_type
    }

    try:
        response = requests.post(NOTIFICATION_SERVICE_URL, json=notification_data)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Failed to notify: {e}")

@app.route('/shipments', methods=['POST'])
def create_shipment():
    shipment = request.get_json()
    shipment_id = shipment.get('shipment_id')
    
    shipments_collection.insert_one(shipment)
    
    # Create a notification
    notify_service(shipment_id, f'Shipment {shipment_id} created.', 'shipment_created')

    return jsonify({'message': 'Shipment created successfully'}), 201

@app.route('/shipments', methods=['GET'])
def get_shipments():
    shipments = list(shipments_collection.find({}, {'_id': False}))
    return dumps(shipments), 200

@app.route('/shipments/<shipment_id>', methods=['GET'])
def get_shipment(shipment_id):
    shipment = shipments_collection.find_one({'shipment_id': shipment_id}, {'_id': False})
    if shipment:
        return jsonify(shipment), 200
    else:
        return jsonify({'error': 'Shipment not found'}), 404

@app.route('/shipments/<shipment_id>', methods=['PUT'])
def update_shipment(shipment_id):
    shipment = request.get_json()
    result = shipments_collection.update_one({'shipment_id': shipment_id}, {'$set': shipment})
    
    if result.matched_count:
        # Create a notification
        notify_service(shipment_id, f'Shipment {shipment_id} updated.', 'shipment_updated')
        return jsonify({'message': 'Shipment updated successfully'}), 200
    else:
        return jsonify({'error': 'Shipment not found'}), 404

@app.route('/shipments/<shipment_id>', methods=['DELETE'])
def delete_shipment(shipment_id):
    result = shipments_collection.delete_one({'shipment_id': shipment_id})
    if result.deleted_count:
        return jsonify({'message': 'Shipment deleted successfully'}), 200
    else:
        return jsonify({'error': 'Shipment not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
