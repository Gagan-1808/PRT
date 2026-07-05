import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'appuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'apppassword')
DB_NAME = os.environ.get('DB_NAME', 'namesdb')


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def wait_for_db(retries=15, delay=2):
    """Retry DB connection on startup since MySQL container may not be ready yet."""
    for attempt in range(retries):
        try:
            conn = get_connection()
            conn.close()
            print("Database connection successful.")
            return
        except Exception as e:
            print(f"Waiting for database... ({attempt + 1}/{retries}) - {e}")
            time.sleep(delay)
    raise Exception("Could not connect to database after retries.")


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/api/submit', methods=['POST'])
def submit_name():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO names (name) VALUES (%s)", (name,))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"name": name}), 201


@app.route('/api/names', methods=['GET'])
def get_names():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM names ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
        conn.close()
        names = [row['name'] for row in rows]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"names": names})


if __name__ == '__main__':
    wait_for_db()
    app.run(host='0.0.0.0', port=5000)
