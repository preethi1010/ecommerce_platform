from flask import Flask, jsonify
from flask_pymongo import PyMongo
from pykafka import KafkaClient
from pykafka.common import OffsetType
import json
import threading

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongodb:27017/analytics_db"
mongo = PyMongo(app)
db = mongo.db.analytics

kafka_client = KafkaClient(hosts='kafka:9092')
topic = kafka_client.topics['cart_topic']
consumer = topic.get_simple_consumer(consumer_group="analytics_group", auto_offset_reset=OffsetType.LATEST, reset_offset_on_start=True)

def consume_messages():
    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            
            # Add timestamp and other fields if necessary
            cart_data = {
                'event': data.get('event'),
                'cart': data.get('cart')
            }
            # Insert message into MongoDB
            db.analytics.insert_one(cart_data)

            consumer.commit_offsets()

threading.Thread(target=consume_messages, daemon=True).start()

@app.route('/analytics', methods=['GET'])
def get_analytics():
    # Fetch all records from the analytics collection
    analytics_data = list(db.analytics.find())

    # Convert MongoDB ObjectIds to strings for JSON serialization
    for data in analytics_data:
        data['_id'] = str(data['_id'])

    return jsonify(analytics_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
