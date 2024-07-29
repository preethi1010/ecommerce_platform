from flask import Flask
from routes import order_bp

# Create and configure the Flask app
app = Flask(__name__)

# Register blueprint
app.register_blueprint(order_bp, url_prefix='/order')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)