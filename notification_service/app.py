from flask import Flask, jsonify, request, json
from flask_pymongo import PyMongo
from pykafka import KafkaClient
from pykafka.common import OffsetType
import threading
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/notification_db'
mongo = PyMongo(app)
notifications = mongo.db.notifications

# Kafka client setup
kafka_client = KafkaClient(hosts='kafka:9092')

user_topic = kafka_client.topics['user_events']
payment_topic = kafka_client.topics['payment_events']
shipment_topic = kafka_client.topics['shipment_events']

user_consumer = user_topic.get_simple_consumer(
    consumer_group="notification_service_group",
    auto_offset_reset=OffsetType.LATEST,
    reset_offset_on_start=True
)
payment_consumer = payment_topic.get_simple_consumer(
    consumer_group="notification_service_group",
    auto_offset_reset=OffsetType.LATEST,
    reset_offset_on_start=True
)
shipment_consumer = shipment_topic.get_simple_consumer(
    consumer_group="notification_service_group",
    auto_offset_reset=OffsetType.LATEST,
    reset_offset_on_start=True
)
def consume_user_messages():
    for message in user_consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            notifications.insert_one({'source': 'user_events', 'data': data})
            user_consumer.commit_offsets()    
     
def consume_payment_messages():
    for message in payment_consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            notifications.insert_one({'source': 'payment_events', 'data': data})
            payment_consumer.commit_offsets()   

def consume_shipment_messages():
    for message in shipment_consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            notifications.insert_one({'source': 'shipment_events', 'data': data})
            shipment_consumer.commit_offsets()   

threading.Thread(target=consume_user_messages, daemon=True).start()
threading.Thread(target=consume_payment_messages, daemon=True).start()
threading.Thread(target=consume_shipment_messages, daemon=True).start()

@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications_list = list(notifications.find())
    for notif in notifications_list:
        notif['_id'] = str(notif['_id'])
    return jsonify(notifications_list)

@app.route('/notification/<id>', methods=['GET'])
def get_notification(id):
    notification = notifications.find_one({'_id': ObjectId(id)})
    if notification:
        notification['_id'] = str(notification['_id'])
        return jsonify(notification)
    else:
        return jsonify({'message': 'Notification not found'}), 404

@app.route('/notification', methods=['POST'])
def add_notification():
    data = request.get_json()
    new_notification_id = notifications.insert_one(data).inserted_id
    return jsonify({'message': 'Notification added', 'notification_id': str(new_notification_id)})

@app.route('/notification/<id>', methods=['PUT'])
def update_notification(id):
    data = request.get_json()
    result = notifications.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count:
        return jsonify({'message': 'Notification updated'})
    else:
        return jsonify({'message': 'Notification not found'}), 404

@app.route('/notification/<id>', methods=['DELETE'])
def delete_notification(id):
    result = notifications.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'message': 'Notification deleted'})
    else:
        return jsonify({'message': 'Notification not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
