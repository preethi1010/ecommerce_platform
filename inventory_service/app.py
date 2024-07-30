from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/inventory_db'
mongo = PyMongo(app)
inventory = mongo.db.inventory

@app.route('/items', methods=['GET'])
def get_items():
    items = list(inventory.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify(items)

@app.route('/item/<id>', methods=['GET'])
def get_item(id):
    item = inventory.find_one({'_id': ObjectId(id)})
    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item)
    else:
        return jsonify({'message': 'Item not found'}), 404

@app.route('/item', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item_id = inventory.insert_one(data).inserted_id
    return jsonify({'message': 'Item added', 'item_id': str(new_item_id)})

@app.route('/item/<id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()
    result = inventory.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count:
        return jsonify({'message': 'Item updated'})
    else:
        return jsonify({'message': 'Item not found'}), 404

@app.route('/item/<id>', methods=['DELETE'])
def delete_item(id):
    result = inventory.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'message': 'Item deleted'})
    else:
        return jsonify({'message': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)