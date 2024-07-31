from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pykafka import KafkaClient
from bson import ObjectId
import json

app = Flask(__name__)

# Config
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/payments'
mongo = PyMongo(app)

# Kafka client setup
kafka_client = KafkaClient(hosts='kafka:9092')
payment_producer = kafka_client.topics['payment_events'].get_sync_producer()

def send_payment_event(data):
    # Convert ObjectId to string if present
    if '_id' in data:
        data['_id'] = str(data['_id'])
    payment_producer.produce(json.dumps(data).encode('utf-8'))

@app.route('/payments', methods=['GET'])
def get_all_payments():
    payments = mongo.db.payments.find()
    output = [{'payment_id': payment['payment_id'], 'user': payment['user'], 'amount': payment['amount'], 'status': payment['status']} for payment in payments]
    return jsonify({'result': output})

@app.route('/payment/<payment_id>', methods=['GET'])
def get_payment_by_id(payment_id):
    payment = mongo.db.payments.find_one({'payment_id': payment_id})
    if payment:
        output = {'payment_id': payment['payment_id'], 'user': payment['user'], 'amount': payment['amount'], 'status': payment['status']}
    else:
        output = 'No results found'
    return jsonify({'result': output})

@app.route('/payment', methods=['POST'])
def add_payment():
    data = request.get_json()
    payment = {
        'payment_id': data['payment_id'],
        'user': data['user'],
        'amount': data['amount'],
        'status': data['status']
    }
    result = mongo.db.payments.insert_one(payment)
    payment['_id'] = str(result.inserted_id)
    send_payment_event({'source': 'payment_service', 'event': 'payment_processed', 'data': payment})
    return jsonify({'message': 'Payment added successfully!'})

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    payment = {
        'payment_id': data['payment_id'],
        'amount': data['amount'],
        'currency': data['currency'],
        'method': data['method'],
        'status': data['status']
    }
    result = mongo.db.payments.insert_one(payment)
    payment['_id'] = str(result.inserted_id)
    send_payment_event({'source': 'payment_service', 'event': 'payment_processed', 'data': payment})
    return jsonify({'message': 'Payment processed successfully!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
