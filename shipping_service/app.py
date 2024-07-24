from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['shipping_db']
shipments_collection = db['shipments']

@app.route('/shipments', methods=['POST'])
def create_shipment():
    shipment = request.get_json()
    shipments_collection.insert_one(shipment)
    return jsonify({'message': 'Shipment created successfully'}), 201

@app.route('/shipments', methods=['GET'])
def get_shipments():
    shipments = list(shipments_collection.find({}, {'_id': False}))
    return jsonify(shipments), 200

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
    app.run(host='0.0.0.0', port=5000)
