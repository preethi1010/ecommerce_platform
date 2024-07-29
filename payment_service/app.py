import os
import pika
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['payment_db']
payments_collection = db['payments']

def send_payment_processed_message(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='payment_queue')
    channel.basic_publish(exchange='', routing_key='payment_queue', body=str(data))
    connection.close()

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    payments_collection.insert_one(data) 
    send_payment_processed_message(data)  
    return jsonify({"message": "Payment processed successfully"}), 200

@app.route('/refund', methods=['POST'])
def refund():
    data = request.get_json()
    send_payment_processed_message(data)
    return jsonify({"message": "Refund processed successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
