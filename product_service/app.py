from flask import Flask
from routes import product_bp

# Create and configure the Flask app
app = Flask(__name__)

# Register blueprint
app.register_blueprint(product_bp, url_prefix='/product')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)
