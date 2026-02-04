from flask import Blueprint, jsonify

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/api/top-films', methods=['GET'])
def get_top_films():
    data = [
        {"id": 1, "title": "ACADEMY DINOSAUR", "rentals": 34},
        {"id": 2, "title": "ELEPHANT TROJAN", "rentals": 31},
        {"id": 3, "title": "BUCKET BROTHERHOOD", "rentals": 30},
        {"id": 4, "title": "RIVER OUTLAW", "rentals": 28},
        {"id": 5, "title": "FORWARD TEMPLE", "rentals": 27}
    ]

    # 4. Serving the dish (Returning JSON)
    return jsonify(data)