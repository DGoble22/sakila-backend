from flask import Blueprint, jsonify
from db_config import get_db_connection;

landing_bp = Blueprint('landing_bp', __name__)

@landing_bp.route('/api/top-films', methods=['GET'])
def get_top_films():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT f.film_id, f.title, c.name AS category_name, COUNT(r.rental_id) AS rental_count
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        JOIN inventory i ON f.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY f.film_id, f.title, c.name
        ORDER BY rental_count DESC
        LIMIT 5;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(results)