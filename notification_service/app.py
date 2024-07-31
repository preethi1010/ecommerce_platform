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
topic = kafka_client.topics[b'user_events']
consumer = topic.get_simple_consumer(consumer_group="notification_service", auto_offset_reset=OffsetType.LATEST, reset_offset_on_start=True)
def consume_messages():
    for message in consumer:
        if message is not None:
            message_value = json.loads(message.value.decode('utf-8'))
            if message_value['event'] == 'user_registered':
                notifications.insert_one({
                    'user_id': message_value['user_id'],
                    'message': f"New user registered with email {message_value['user_data']}"
                })
# Start Kafka consumer in a separate thread
threading.Thread(target=consume_messages, daemon=True).start()

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
