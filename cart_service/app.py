from flask import Flask
from routes import cart_bp

app = Flask(__name__)

# Register blueprint
app.register_blueprint(cart_bp, url_prefix='/cart')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
