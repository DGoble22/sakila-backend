from flask import Flask, jsonify
from flask_cors import CORS
from routes.landing_routes import landing_bp
from routes.film_routes import film_bp
from routes.customer_routes import customer_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(landing_bp)
app.register_blueprint(film_bp)
app.register_blueprint(customer_bp)

@app.route('/')
def hello_world():  # put application's code here
    return jsonify({"status": "Success", "message": "The bridge is working!"})


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='localhost')
