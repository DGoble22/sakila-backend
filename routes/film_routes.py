from flask import Blueprint, jsonify
from db_config import get_db_connection
from flask import request
from datetime import datetime
film_bp = Blueprint('film_bp', __name__)

@film_bp.route('/api/film-details/<int:id>', methods=['GET'])
def get_film_details(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
            SELECT f.film_id, f.title, f.description, f.release_year, c.name AS category_name,
                   GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS actors
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            JOIN film_actor fa ON f.film_id = fa.film_id
            JOIN actor a ON fa.actor_id = a.actor_id
            WHERE f.film_id = %s
            GROUP BY f.film_id, f.title, f.description, f.release_year, c.name;
        """

    cursor.execute(query, (id,))
    results = cursor.fetchone()
    cursor.close()
    db.close()

    return jsonify(results)

@film_bp.route('/api/actor-details/<int:id>', methods=['GET'])
def get_actor_details(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
            SELECT f.film_id, f.title AS film_title, COUNT(r.rental_id) AS rental_count
            FROM actor a
            JOIN film_actor fa ON a.actor_id = fa.actor_id
            JOIN film f ON fa.film_id = f.film_id
            JOIN inventory i ON f.film_id = i.film_id
            JOIN rental r ON i.inventory_id = r.inventory_id
            WHERE a.actor_id = %s
            GROUP BY f.film_id, f.title
            ORDER BY rental_count DESC
            LIMIT 5;
            """

    cursor.execute(query, (id,))
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(results)

@film_bp.route('/api/films', methods=['GET'])
def get_films():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    search_query = request.args.get('search')

    if search_query:
        # Searches title OR category OR actor name
        # Distinct avoids duplicates
        sql = """
            SELECT DISTINCT f.film_id, f.title, f.description, f.release_year, f.rating, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            LEFT JOIN film_actor fa ON f.film_id = fa.film_id
            LEFT JOIN actor a ON fa.actor_id = a.actor_id
            WHERE f.title LIKE %s 
               OR c.name LIKE %s 
               OR CONCAT(a.first_name, ' ', a.last_name) LIKE %s
            LIMIT 50;
        """
        wildcard = f"%{search_query}%"
        cursor.execute(sql, (wildcard, wildcard, wildcard))
    else:
        # Default view
        sql = """
            SELECT f.film_id, f.title, f.description, f.release_year, f.rating, c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            LIMIT 50;
        """
        cursor.execute(sql)

    results = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(results)


@film_bp.route('/api/rent-film', methods=['POST'])
def rent_film():
    data = request.get_json()
    film_id = data.get('film_id')
    customer_id = data.get('customer_id')
    staff_id = 1  # Placeholder for now

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        #checks inventory id for the film that is not currently rented out
        check_inventory_sql = """
                              SELECT i.inventory_id
                              FROM inventory i
                              WHERE i.film_id = %s
                                AND i.inventory_id NOT IN (SELECT r.inventory_id
                                                           FROM rental r
                                                           WHERE r.return_date IS NULL)
                              LIMIT 1;
                              """
        cursor.execute(check_inventory_sql, (film_id,))
        available_item = cursor.fetchone()

        if not available_item:
            return jsonify({"error": "Sorry, this film is out of stock!"}), 409

        inventory_id = available_item['inventory_id']

        # Inserts rental record with current timestamp and NULL return date
        insert_rental_sql = """
                            INSERT INTO rental (rental_date, inventory_id, customer_id, return_date, staff_id)
                            VALUES (%s, %s, %s, NULL, %s)
                            """
        rental_date = datetime.now()

        cursor.execute(insert_rental_sql, (rental_date, inventory_id, customer_id, staff_id))
        db.commit()

        return jsonify({"message": f"Success! You have rented this film!"}), 200

    except Exception as e:
        db.rollback()  # reverses changes in case of error
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()