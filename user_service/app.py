from flask import Flask, request, jsonify, json
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from bson.objectid import ObjectId
from pykafka import KafkaClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/users_db'
mongo = PyMongo(app)
users = mongo.db.users

# Kafka client setup
kafka_client = KafkaClient(hosts='kafka:9092')
topic = kafka_client.topics['user_events']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.find_one({'_id': ObjectId(data['id'])})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user_id = users.insert_one({
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password
    }).inserted_id
    
    message = {
        'event': 'user_registered',
        'user_id': str(new_user_id),
        'user_data': data['email']
    }

    with topic.get_producer() as producer:
        producer.produce(json.dumps(message).encode('utf-8'))
    
    return jsonify({'message': 'Registered successfully', 'user_id': str(new_user_id)})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = users.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Login failed!'}), 401
    token = jwt.encode({'id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                       app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    user_data = {
        'username': current_user['username'],
        'email': current_user['email']
    }
    return jsonify({'user': user_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011)