from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
from pykafka import KafkaClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['shipping_db']
shipments_collection = db['shipments']

# Kafka client setup
kafka_client = KafkaClient(hosts='kafka:9092')
topic = kafka_client.topics['shipment_events']

def publish_to_kafka(event_type, shipment_id, shipment_message):    
    try:

        message = {
        'event': event_type,
        'shipment_id': str(shipment_id),
        'message': str(shipment_message)
        }
        with topic.get_producer() as producer:
                producer.produce(json.dumps(message).encode('utf-8'))
    except Exception as e:
        raise Exception(f"Error sending topic message: {e}")

@app.route('/shipments', methods=['POST'])
def create_shipment():
    shipment = request.get_json()
    shipment_id = shipment.get('shipment_id')
    
    shipments_collection.insert_one(shipment)
    
    # Publish to Kafka
    publish_to_kafka('shipment_created', shipment_id, f'Shipment {shipment_id} created.')

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
        # Publish to Kafka
        publish_to_kafka('shipment_updated', shipment_id, f'Shipment {shipment_id} updated.')
        return jsonify({'message': 'Shipment updated successfully'}), 200
    else:
        return jsonify({'error': 'Shipment not found'}), 404

@app.route('/shipments/<shipment_id>', methods=['DELETE'])
def delete_shipment(shipment_id):
    result = shipments_collection.delete_one({'shipment_id': shipment_id})
    if result.deleted_count:
        # Publish to Kafka
        publish_to_kafka('shipment_deleted', shipment_id, f'Shipment {shipment_id} deleted.')
        return jsonify({'message': 'Shipment deleted successfully'}), 200
    else:
        return jsonify({'error': 'Shipment not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
