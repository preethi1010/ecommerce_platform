from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# Config
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/reviews'
mongo = PyMongo(app)

@app.route('/reviews', methods=['GET'])
def get_all_reviews():
    reviews = mongo.db.reviews.find()
    output = [{'product_id': review['product_id'], 'user': review['user'], 'review': review['review'], 'rating': review['rating']} for review in reviews]
    return jsonify({'result': output})

@app.route('/review/<product_id>', methods=['GET'])
def get_reviews_by_product(product_id):
    reviews = mongo.db.reviews.find({'product_id': product_id})
    output = [{'product_id': review['product_id'], 'user': review['user'], 'review': review['review'], 'rating': review['rating']} for review in reviews]
    return jsonify({'result': output})

@app.route('/review', methods=['POST'])
def add_review():
    data = request.get_json()
    review = {
        'product_id': data['product_id'],
        'user': data['user'],
        'review': data['review'],
        'rating': data['rating']
    }
    mongo.db.reviews.insert_one(review)
    return jsonify({'message': 'Review added successfully!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')